import typing

from functools import partial as bind

from cohesivenet import (
    data_types,
    network_math,
    Logger,
    util,
    VNS3Client,
    CohesiveSDKException,
)
from cohesivenet.macros import api_operations, state


VNS3Attr = state.VNS3Attr


def create_local_gateway_route(client, local_cidr, **route_kwargs):
    """[summary]

    Arguments:
        client {[type]} -- [description]
        local_cidr {[type]} -- [description]

    Keyword Arguments:
        gateway {[type]} -- [description] (default: {None})

    Returns:
        OperationResult
    """
    route = dict(
        **{
            "cidr": local_cidr,
            "description": "Local Underlay Network Routing",
            "interface": "eth0",
            "gateway": network_math.get_default_gateway(local_cidr),
            "advertise": "False",
            "metric": 0,
        },
        **route_kwargs
    )
    api_kwargs = {"should_raise": True}
    api_kwargs.update(route)
    return api_operations.try_call_api(client.routing.post_create_route, **api_kwargs)


def create_local_gateway_routes_for_peers(
    client: VNS3Client, local_network: str, peer_ips: typing.List[str]
):
    """Create route to local underlay gateway for IPs. This is commonly done for explicit routes
       to VNS3 peers.

    Arguments:
        client {VNS3Client}
        local_network {str} - local network cidr for VPC/VNET
        peer_ips {typing.List[str]}

    Returns:
        dict with list of routes.

        {
            response: [{
                cidr: "X.X.X.X/32",
                interface: "eth0",
            }, ...]
        }
    """
    routes = [
        {
            "cidr": ip if ip.endswith("/32") else "%s/32" % ip,
            "description": "Peer route to local gateway",
            "interface": "eth0",
            "gateway": network_math.get_default_gateway(local_network),
            "advertise": False,
        }
        for ip in peer_ips
    ]

    for route in routes:
        client.routing.post_create_route_if_not_exists(route)
    return client.routing.get_routes().json()


def create_peer_mesh_local_gw_routes(
    clients, subnets=None, address_type=VNS3Attr.primary_private_ip
):
    """Create explicit routes between VNS3 peers for peering traffic by pointing peer ips
    to the local gateway.

    For example, for clients = [VNS3@10.0.1.5, VNS3@10.0.2.10]
    in private clouds that are peered where 10.0.1.5 in 10.0.1.0/24 and
    10.0.2.10 in 10.0.2.0/24

    This func  will create the following routes:
        On VNS3@10.0.1.5:
            Route: cidr=10.0.2.10/32 on eth0 to network gateway at 10.0.1.1
        On VNS3@10.0.2.10:
            Route: cidr=10.0.1.5/32 on eth0 to network gateway at 10.0.2.1

    Assumptions:
        - IF subnets list not passed, Clients need to have the VPC/VNet network they are contained
        in set on their state.
            e.g. client.update_state({"network": "10.0.1.0/24"}); client.query_state("network");
            This function queries the following keys: network

    Arguments:
        clients {List[VNS3Client]}

    Keyword Arguments:
        subnets: List[str] - list of subnets for each client.
        address_type {str} -- Type of address to use for cidr route. (default: {VNS3Attr.primary_private_ip})
    """
    create_client_routes_funcs = []
    client_ips = [
        state.fetch_client_state_attribute(client, address_type) for client in clients
    ]

    if subnets:
        assert len(subnets) == len(
            clients
        ), "If subnets passed, must be same number of clients passed"

    for i, client in enumerate(clients):
        client_subnet_cidr = subnets[i] if subnets else client.query_state("subnet")
        client_ip = state.fetch_client_state_attribute(client, address_type)
        assert (
            client_subnet_cidr
        ), "Each client must have 'subnet' set on client.state if subnets arg not passed"
        create_client_routes_funcs.append(
            bind(
                create_local_gateway_routes_for_peers,
                client,
                client_subnet_cidr,
                list(set(client_ips) - set([client_ip])),
            )
        )

    return api_operations.__bulk_call_api(create_client_routes_funcs, parallelize=True)


def create_route_advertisements(
    clients, local_subnets
) -> data_types.BulkOperationResult:
    """create_route_advertisements Create a route advertisement for controllers network

    Arguments:
        clients {List[VNS3Client]}
        local_subnets {List[str]} - order should correspond with clients list

    Returns:
        data_types.BulkOperationResult
    """
    assert len(clients) == len(
        local_subnets
    ), "clients list length must equal local_subnets list length"

    invalid = []
    for index, client in enumerate(clients):
        private_ip = state.get_primary_private_ip(client)
        if not network_math.subnet_contains_ipv4(private_ip, local_subnets[index]):
            invalid.append("%s not in %s" % (private_ip, local_subnets[index]))

    if len(invalid):
        raise AssertionError(
            "Invalid subnets provided for clients: %s." % ",".join(invalid)
        )

    def _create_route(_client, subnet):
        return _client.routing.post_create_route(
            **{
                "cidr": subnet,
                "description": "Local subnet advertisement",
                "advertise": True,
                "gateway": "",
            }
        )

    bound_api_calls = [
        bind(_create_route, client, local_subnets[index])
        for index, client in enumerate(clients)
    ]

    return api_operations.__bulk_call_api(bound_api_calls)


def create_route_table(client: VNS3Client, routes, state={}):
    """Create routing policy

    Arguments:
        client {VNS3Client}
        routes {List[Route]} - [{
            "cidr": "str",
            "description": "str",
            "interface": "str",
            "gateway": "str",
            "tunnel": "int",
            "advertise": "bool",
            "metric": "int",
        }, ...]

    Keyword Arguments:
        state {dict} - State to format routes with. (can call client.state)

    Returns:
        Tuple[List[str], List[str]] - success, errors
    """
    successes = []
    errors = []
    Logger.debug(
        "Setting controller route table.",
        host=client.host_uri,
        route_count=len(routes),
    )

    _sub_vars = state or client.state
    for i, route_kwargs in enumerate(routes):
        skip = False
        for key, value in route_kwargs.items():
            _value, err = util.format_string(value, _sub_vars)
            if err:
                errors.append("Route key %s not formattable." % key)
                skip = True
            else:
                route_kwargs.update(**{key: _value})

        if skip:
            continue

        client.routing.post_create_route_if_not_exists(route_kwargs)
        successes.append("Route created: route=%s" % str(route_kwargs))

    if errors:
        raise CohesiveSDKException(",".join(errors))

    return successes, errors
