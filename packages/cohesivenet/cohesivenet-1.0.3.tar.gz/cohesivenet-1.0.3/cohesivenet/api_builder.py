import functools

from cohesivenet import Logger, util
from cohesivenet.macros import state as vns3_state
from cohesivenet.exceptions import (
    ApiValueError,
    ApiMethodUnsupportedError,
)


def validate_call(  # noqa: C901
    path_params=None,
    path_constraints=None,
    body_params=None,
    body_constraints=None,
    query_params=None,
    query_constraints=None,
    supported_versions=None,
    file_upload=None,
    file_kwarg=None,
):
    def validate_decorator(api_func):
        @functools.wraps(api_func)
        def api_func_wrapper(api_client, *args, **kwargs):
            if path_params:
                assert len(args) == len(
                    path_params
                ), "declared path params and args are different lengths"
                named_path_params = dict(zip(path_params, args))
            else:
                named_path_params = {}

            if supported_versions:
                vns3_version = vns3_state.get_vns3_version(api_client)
                is_supported = True
                if not is_supported:
                    raise ApiMethodUnsupportedError(
                        method_name=api_func.__name__,
                        version=vns3_version,
                        supported_versions=supported_versions,
                    )

            if path_params:
                for path_param in path_params:
                    if (
                        path_param not in named_path_params
                        or named_path_params[path_param] is None
                    ):
                        raise ApiValueError(
                            "Missing the required path parameter `%s` when calling `%s`"
                            % (path_param, api_func.__name__)
                        )

            # keyword params can be either body params (POST, PUT, PATCH) or query params (GET)
            keyword_params = kwargs
            if body_params:
                for body_param in body_params:
                    if (
                        body_param not in keyword_params
                        or keyword_params[body_param] is None
                    ):
                        raise ApiValueError(
                            "Missing the required field `%s` when calling `%s`"
                            % (body_param, api_func.__name__)
                        )

            if query_params:
                for query_param in query_params:
                    if (
                        query_param not in keyword_params
                        or keyword_params[query_param] is None
                    ):
                        raise ApiValueError(
                            "Missing the required query parameter `%s` when calling `%s`"
                            % (query_param, api_func.__name__)
                        )

            if file_upload:
                assert (
                    file_kwarg
                ), "no kwarg key provided for file upload param validation"
                if file_kwarg not in keyword_params or not keyword_params[file_kwarg]:
                    raise ApiValueError(
                        "Missing the file stream kwarg field `%s` when calling `%s`"
                        % (file_kwarg, api_func.__name__)
                    )

            return api_func(api_client, *args, **kwargs)

        return api_func_wrapper

    return validate_decorator


def parse_version_to_int(v):
    # parse versions like 4.11.3 and 5.0.beta => 4113 and 50
    return int("".join([p for p in v.split(".") if p.isdigit()]))


def raise_unsupported_error(name, vns3_version, *args, **kwargs):
    raise ApiMethodUnsupportedError(name, vns3_version)


def set_version_library(client, api, library):
    """Set the API library functions based on the current clients version

    Arguments:
        client {APIClient}
        api {Object} -
        library {Dict} - {
            func_name: str -> dict[version:str -> func]
        }

    Returns: None
    """
    client_version = client.dot_version
    if not client_version:
        client_version = client.latest_version()

    version_library = {}
    unsupported = []
    for function_name, versions_funcs in library.items():
        _supported = False
        for version_range, func in versions_funcs.items():
            if util.version_in_range(client_version, version_range):
                version_library[function_name] = func
                _supported = True
                break
        if not _supported:
            unsupported.append(function_name)

    Logger.debug(
        "Setting v%s API functions %s" % (client_version, api.__class__.__name__)
    )
    if len(unsupported) > 0:
        Logger.debug("Unsupported functions: %s" % unsupported)

    for name, func in version_library.items():
        setattr(api, name, functools.partial(func, client))
    for funcname in unsupported:
        setattr(
            api,
            funcname,
            functools.partial(raise_unsupported_error, funcname, client_version),
        )


class VersionRouter(object):
    """SETIT"""

    function_library = {}

    def __init__(self, api_client):
        self.__api_client = api_client
        set_version_library(api_client, self, self.function_library)

    @property
    def api_client(self):
        return self.__api_client

    @api_client.setter
    def api_client(self, _):
        raise RuntimeError(
            "Can't reset api_client on VersionRouter. Please instantiate new router."
        )

    @classmethod
    def print_available_functions(cls):
        for function_name, versions in cls.function_library.items():
            versions_supported = ",".join(versions.keys())
            print("%s versions=%s" % (function_name, versions_supported))
