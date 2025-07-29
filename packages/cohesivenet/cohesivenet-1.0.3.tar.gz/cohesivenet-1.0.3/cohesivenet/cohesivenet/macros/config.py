import json
import os
import time
from typing import Dict

from cohesivenet import (
    VNS3Client,
    data_types,
    CohesiveSDKException,
    ApiException,
    Logger,
    UrlLib3ConnExceptions,
    HTTPStatus,
    util,
)
from cohesivenet.macros import api_operations


def fetch_keyset_from_source(  # noqa: C901
    client, source, token, wait_timeout=180.0, allow_exists=False
):  # noqa
    """fetch_keyset_from_source Put keyset by providing source controller to download keyset. This
    contains logic that handles whether or not fetching from the source fails, typically due
    to a firewall or routing issue in the underlay network (e.g. security groups and route tables).

    Pseudo-logic:
        PUT new keyset request to fetch from remote controller
        if keyset exists or already in progress, fail immediately as its unexpected
        if PUT succees:
            wait:
                if a new successful put returns: that indicates failure to download from source. return 400
                if timeout: that indicates controller is rebooting, return wait for keyset
                if keyset already exists, wait to ensure keyset  exists, then return keyset details

    Arguments:
        source {str} - host controller to fetch keyset from
        token {str} - secret token used when generating keyset
        wait_timeout {float} - timeout for waiting for keyset and while polling for download failure (default: 1 min)
        allow_exists {bool} - If true and keyset already exists, DONT throw exception

    Raises:
        e: ApiException or CohesiveSDKException

    Returns:
        KeysetDetail
    """
    sleep_time = 2.0
    failure_error_str = (
        "Failed to fetch keyset for source. This typically due to a misconfigured "
        "firewall or routing issue between source and client controllers."
    )

    try:
        put_response = client.config.put_keyset(**{"source": source, "token": token})
    except ApiException as e:
        if allow_exists and ("keyset already exists" in e.get_error_message().lower()):
            Logger.info("Keyset already exists.", host=client.host_uri)
            return client.config.try_get_keyset()

        Logger.info(
            "Failed to fetch keyset: %s" % e.get_error_message(),
            host=client.host_uri,
        )
        
        if e.status == 502 or e.status == 503:
            client.config.wait_for_keyset(wait_timeout)
        else:
            raise e
    except UrlLib3ConnExceptions:
        raise ApiException(
            status=HTTPStatus.SERVICE_UNAVAILABLE,
            reason="Controller unavailable. It is likely rebooting. Try client.sys_admin.wait_for_api().",
        )

    if not put_response.response:
        keyset_data = client.config.get_keyset()
        if keyset_data.response and keyset_data.response.keyset_present:
            raise ApiException(status=400, reason="Keyset already exists.")
        raise ApiException(status=500, reason="Put keyset returned None.")

    start_time = put_response.response.started_at_i
    Logger.info(message="Keyset downloading from source.", start_time=start_time)
    polling_start = time.time()
    while time.time() - polling_start <= wait_timeout:
        try:
            duplicate_call_resp = client.config.put_keyset(
                **{"source": source, "token": token}
            )
        except UrlLib3ConnExceptions:
            Logger.info(
                "API call timeout. Controller is likely rebooting. Waiting for keyset.",
                wait_timeout=wait_timeout,
                source=source,
            )
            client.sys_admin.wait_for_api(timeout=wait_timeout, wait_for_reboot=True)
            return client.config.wait_for_keyset(timeout=wait_timeout)
        except ApiException as e:
            duplicate_call_error = e.get_error_message()

            if duplicate_call_error == "Keyset already exists.":
                keyset_data = client.config.try_get_keyset()
                if not keyset_data:
                    Logger.info(
                        "Keyset exists. Waiting for reboot.",
                        wait_timeout=wait_timeout,
                        source=source,
                    )
                    client.sys_admin.wait_for_api(
                        timeout=wait_timeout, wait_for_reboot=True
                    )
                    return client.config.wait_for_keyset()
                return keyset_data

            if duplicate_call_error == "Keyset setup in progress.":
                # this means download is in progress, but might fail. Wait and retry
                time.sleep(sleep_time)
                continue

            # Unexpected ApiException
            raise e

        # If there is a new start time for keyset generation, that indicates a failure
        new_start_resp = duplicate_call_resp.response
        new_start = new_start_resp.started_at_i if new_start_resp else None
        if (new_start and start_time) and (new_start != start_time):
            Logger.error(failure_error_str, source=source)
            raise ApiException(status=HTTPStatus.BAD_REQUEST, reason=failure_error_str)

        time.sleep(sleep_time)
    raise CohesiveSDKException("Timeout while waiting for keyset.")


def setup_controller(
    client: VNS3Client,
    topology_name: str,
    license_file: str,
    license_parameters: Dict,
    keyset_parameters: Dict,
    controller_name: str = None,
    peering_id: int = 1,
    reboot_timeout=120,
    keyset_timeout=120,
):
    """setup_controller Set the topology name, controller license, keyset and peering ID if provided

    Arguments:
        client {VNS3Client}
        topology_name {str}
        controller_name {str}
        keyset_parameters {Dict} -- UpdateKeysetRequest {
            'source': 'str',
            'token': 'str',
            'topology_name': 'str',
            'sealed_network': 'bool'
        }
        peering_id {int} -- ID for this controller in peering mesh

    Returns:
        OperationResult
    """
    current_config = client.config.get_config().response
    Logger.info("Setting topology name", name=topology_name)
    config_update = {}
    if topology_name and current_config.topology_name != topology_name:
        config_update.update({"topology_name": topology_name})
    if controller_name and current_config.controller_name != controller_name:
        config_update.update({"controller_name": controller_name})
    if config_update:
        client.config.put_config(**config_update)

    if not current_config.licensed:
        if not os.path.isfile(license_file):
            raise CohesiveSDKException("License file does not exist")

        with open(license_file) as f:
            license_file_data = f.read().strip()
        Logger.info("Uploading license file", path=license_file)
        client.licensing.upload_license(license_file_data)

    accept_license = False
    try:
        current_license = client.licensing.get_license().response
        accept_license = not current_license or not current_license.finalized
    except ApiException as e:
        if e.get_error_message() == "Must be licensed first.":
            accept_license = True
        else:
            raise e

    if accept_license:
        Logger.info("Accepting license", parameters=license_parameters)
        client.licensing.put_set_license_parameters(**license_parameters)
        Logger.info("Waiting for server reboot.")
        client.sys_admin.wait_for_api(timeout=reboot_timeout, wait_for_reboot=True)

    current_keyset = api_operations.retry_call(
        client.config.get_keyset, max_attempts=20
    ).response
    if not current_keyset.keyset_present and not current_keyset.in_progress:
        Logger.info("Generating keyset", parameters=keyset_parameters)
        api_operations.retry_call(client.config.put_keyset, kwargs=keyset_parameters)
        Logger.info("Waiting for keyset ready")
        client.config.wait_for_keyset(timeout=keyset_timeout)
    elif current_keyset.in_progress:
        client.config.wait_for_keyset(timeout=keyset_timeout)

    current_peering_status = client.peering.get_peering_status().response
    if not current_peering_status.id and peering_id:
        Logger.info("Setting peering id", id=peering_id)
        client.peering.put_self_peering_id(**{"id": peering_id})
    return client


def license_clients(clients, license_file_path) -> data_types.BulkOperationResult:
    """Upload license file to all clients. These will have DIFFERENT keysets. See keyset operations
       if all controllers are to be in the same clientpack topology

    Arguments:
        clients {List[VNS3Client]}
        license_file_path {str} - full path to license file

    Returns:
        BulkOperationResult
    """
    license_file = open(license_file_path).read().strip()

    def _upload_license(_client):
        return _client.licensing.upload_license(license_file)

    return api_operations.__bulk_call_client(clients, _upload_license)


def accept_clients_license(
    clients, license_parameters
) -> data_types.BulkOperationResult:
    """Accept licenses for all. These will have DIFFERENT keysets. See keyset operations
       if all controllers are to be in the same clientpack topology. Assumes same license
       parameters will be accepted for all clients

    Arguments:
        clients {List[VNS3Client]}
        license_parameters {UpdateLicenseParametersRequest} - dict {
            'subnet': 'str',
            'managers': 'str',
            'asns': 'str',
            'clients': 'str',
            'my_manager_vip': 'str',
            'default': 'bool'
        }

    Returns:
        BulkOperationResult
    """

    def _accept_license(_client):
        return _client.licensing.put_set_license_parameters(**license_parameters)

    return api_operations.__bulk_call_client(clients, _accept_license)


def fetch_keysets(clients, root_host, keyset_token, wait_timeout=80.0):
    """fetch_keysets Fetch keysets for all clients from root_host

    Arguments:
        clients {List[VNS3Client]}
        root_host {str}
        keyset_token {str}

    Returns:
        BulkOperationResult
    """

    def _fetch_keyset(_client):
        return fetch_keyset_from_source(
            _client, root_host, keyset_token, wait_timeout=wait_timeout
        )

    return api_operations.__bulk_call_client(clients, _fetch_keyset, parallelize=False)


def __add_controller_states(config, infra_state, groups=None):
    """
    Merge config and infrastructure states

    Arguments:
        config {dict}
        infra_state {dict}

    Keyword Arguments:
        groups {dict} - name: str -> size: int

    Raises:
        CohesiveSDKException: [description]

    Returns:
        [type] -- [description]
    """
    if not infra_state:
        return config

    controllers = config["controllers"]

    _group_indexes = None
    if groups:
        _group_indexes = {env: 0 for env in groups}
        missing_states = [g for g in groups if g not in infra_state]
        if missing_states:
            raise CohesiveSDKException(
                "If groups are provided. infra_state must be keyed by group. "
                "e.g. groups={aws: 3, azure: 2}, infra_state={aws: {...}, azure: {...}}"
            )

    for i, controller in enumerate(controllers):
        controller_vars = controller.get("variables", {})
        if groups:
            group = controller_vars["group"]
            if group not in infra_state:
                continue

            group_size = groups[group]
            _cur_group_index = _group_indexes[group]
            if _cur_group_index >= group_size:
                continue

            group_state = infra_state[group]
            for key, val in group_state.items():
                controller_vars[key] = val[_cur_group_index]
                _group_indexes[group] = _cur_group_index + 1
        else:
            for key, val in infra_state.items():
                assert type(val) in (
                    tuple,
                    list,
                ), "Expected infra state vars to be lists, indexed by controller"
                if len(val) > i:
                    controller_vars[key] = val[i]

        controller.update(variables=controller_vars)
    return config


def get_config_from_env():
    # Update for environment
    cn_vars = {
        k.replace("CN_", "").lower(): v
        for k, v in dict(os.environ).items()
        if k.startswith("CN_")
    }

    env_config = {"license_file": cn_vars.pop("license", None)}

    controller_vars = {
        k: v.split(",") for k, v in cn_vars.items() if k.startswith("controllers")
    }

    variables = {k: v for k, v in cn_vars.items() if k not in controller_vars}

    return dict(env_config, **controller_vars, **{"variables": variables})


def _filter_dict_none_vals(d, none_vals=("", None)):
    return dict(list(filter(lambda kv: kv[1] not in none_vals, d.items())))


def __add_config_from_env(config, env_config):
    """Get configuration details from environment

    Arguments:
        config {dict}

    Raises:
        CohesiveSDKException: [description]

    Returns:
        [dict]
    """
    NONE_VALS = ("", None)
    topology_vars = env_config.pop("variables", {})
    topology_vars_non_null = _filter_dict_none_vals(topology_vars)
    topology_vars_plugin_images = env_config.pop("plugin_images", {})
    topology_vars_plugin_images_non_null = _filter_dict_none_vals(
        topology_vars_plugin_images
    )

    updated_config = dict(
        config,
        **{
            "variables": dict(config.get("variables", {}), **topology_vars_non_null),
            "plugin_images": dict(
                config.get("plugin_images", {}), **topology_vars_plugin_images_non_null
            ),
        }
    )

    controllers = config["controllers"]
    for key, config_value in env_config.items():
        if config_value in NONE_VALS:
            continue

        if key.startswith("controllers"):
            assert (
                type(config_value) is list
            ), "Controller state vars should be passed as lists"
            var_name = "_".join(key.split("_")[1:]).strip("_")
            for i, controller_var_value in enumerate(config_value):
                if controller_var_value in NONE_VALS:
                    continue

                if len(controllers) < i:
                    controllers.append({})

                controller_config = controllers[i]
                controller_vars = controller_config.get("variables", {})
                controller_vars.update(**{var_name: controller_var_value})
                controller_config.update(variables=controller_vars)

        elif type(config_value) in (str, int):
            updated_config.update(**{key: config_value})
        else:
            raise CohesiveSDKException(
                "Unknown environment variable value key=%s, value=%s"
                % (key, config_value)
            )

    updated_config.update(controllers=controllers)
    return updated_config


def __resolve_string_vars(string, local_vars, global_config):
    """Resolve string variable. Sub local and global vars into string

    Arguments:
        string {str}
        local_vars {dict}
        global_config {dict}

    Returns:
        [tuple] - (str, errors)
    """
    string_vars = util.is_formattable_string(string)
    if not string_vars:
        return string, None

    errors = []
    for var in string_vars:
        if var.startswith("config."):
            path = var.replace("config.", "")
            val = util.get_path(global_config, path)
            if not val:
                continue

            if type(val) is dict:
                if string != "{%s}" % var:
                    errors.append(
                        "Can't format dict into string for config var %s and string %s"
                        % (var, string)
                    )
                else:
                    return val, None
            else:
                string = string.replace("{%s}" % var, val)
        elif var in local_vars:
            string = string.replace("{%s}" % var, local_vars[var])
    return string, None if not errors else ",".join(errors)


def __resolve_route_config_variables(controller, config):
    """Resolve variables in route kwargs

    Arguments:
        controller {dict}
        config {dict}

    Raises:
        CohesiveSDKException: [description]

    Returns:
        [dict]
    """
    routes = controller.get("routes", [])
    if not routes:
        return config

    local_vars = controller.get("variables", {})
    format_errors = []
    for i, route_kwargs in enumerate(routes):
        for key, val in route_kwargs.items():
            val, err = __resolve_string_vars(val, local_vars, config)
            if err:
                format_errors.append(err)
            route_kwargs.update(**{key: val})

    if format_errors:
        raise CohesiveSDKException(
            "Failed to format routes: %s" % ",".join(format_errors)
        )
    return config


def __resolve_peering_config_variables(controller, config):
    """Resolve peering config variables.

    Arguments:
        controller {dict}
        config {dict}

    Raises:
        CohesiveSDKException: [description]

    Returns:
        [dict]
    """
    peering = controller.get("peering", {})
    peers = peering.get("peers", {})
    local_vars = controller.get("variables", {})
    if not peers:
        return config

    format_errors = []
    for peer_id, peer_name in peers.items():
        peer_name, err = __resolve_string_vars(peer_name, local_vars, config)
        if err:
            format_errors.append(err)
        peers[peer_id] = peer_name

    if format_errors:
        raise CohesiveSDKException(
            "Failed to format peers: %s" % ",".join(format_errors)
        )
    return config


def __resolve_plugins_config_variables(controller, config):
    """Resolve Plugin images for controller

    Arguments:
        controller {dict}
        config {dict}

    Raises:
        CohesiveSDKException: [description]

    Returns:
        [dict]
    """
    plugins = controller.get("plugins", [])
    local_vars = controller.get("variables", {})
    if not plugins:
        return config

    format_errors = []
    for plugin in plugins:
        for key, val in plugin.items():
            val_resolved, err = __resolve_string_vars(val, local_vars, config)
            if err:
                format_errors.append(err)
                continue
            plugin[key] = val_resolved

    if format_errors:
        raise CohesiveSDKException(
            "Failed to resolve controller plugin vars: %s" % ",".join(format_errors)
        )
    return config


def __substitute_controller_variables(config):
    """Substitute variables and set defaults for config

    Arguments:
        config {dict}

    Raises:
        Exception: [description]

    Returns:
        [dict]
    """
    global_variables = config.get("variables", {})
    set_master_password = global_variables.get("set_master_password")
    master_password = global_variables.get("master_password")
    for controller in config["controllers"]:
        # add global variables controller state, overriding with local variables
        local_variables = dict(global_variables, **controller.get("variables", {}))

        # Password logic:
        #   - use passwords passed by ENV
        #   - if none, use passwords in config file
        #   - if still none >
        #   -   if master password is passed and set_master_password flag is NOT true, use master
        #   -   else use default password for clouds
        if not local_variables.get("api_password"):
            if not master_password or set_master_password:
                cloud = local_variables.get("cloud", None)
                if cloud == "azure":
                    local_variables["api_password"] = "%s-%s" % (
                        local_variables["instance_name"],
                        local_variables["primary_private_ip"],
                    )
                else:
                    local_variables["api_password"] = local_variables["instance_id"]
            else:
                local_variables["api_password"] = master_password

        if not local_variables.get("host"):
            local_variables["host"] = local_variables["public_ip"]

        for key, value in local_variables.items():
            if util.is_formattable_string(value):
                try:
                    local_variables[key] = value.format(**local_variables)
                except KeyError:
                    raise CohesiveSDKException("Missing variable %s" % value)

        controller["variables"] = local_variables
        __resolve_route_config_variables(controller, config)
        __resolve_peering_config_variables(controller, config)
        __resolve_plugins_config_variables(controller, config)
    return config


def read_config_file(config_file):
    try:
        return json.loads(open(config_file).read())
    except json.decoder.JSONDecodeError:
        raise CohesiveSDKException(
            "Invalid config file %s. Must be valid json." % config_file
        )


def resolve_config_variables(
    config_dict, infra_state=None, fetch_env=False, groups=None
):
    """Resolve and fetch config variables

    Arguments:
        config_dict {dict}

    Keyword Arguments:
        infra_state {dict} - infrastructure state
        fetch_env {bool} - read vars from env if True
        groups {Dict{str -> int}} - group_name, size dict

    Returns:
        [type] -- [description]
    """
    _config = dict(config_dict)

    if not groups:
        controllers = config_dict["controllers"]
        groups = {}
        for controller in controllers:
            controller_group = controller["variables"].get("group")
            if not controller_group:
                continue
            elif controller_group in groups:
                groups[controller_group] = groups[controller_group] + 1
            else:
                groups[controller_group] = 1

    if infra_state:
        _config = __add_controller_states(_config, infra_state, groups=groups)

    if fetch_env:
        _config = __add_config_from_env(_config, get_config_from_env())

    return __substitute_controller_variables(_config)
