from cohesivenet import VNS3Client


def create_tunnel_endpoint(
    client: VNS3Client,
    tunnel_name,
    tunnel_secret,
    target_ip,
    target_network_cidr,
    vti_block,
    target_network_name=None,
    tunnel_parameters={},
    route_parameters={},
):
    """create_tunnel_endpoint Create IPsec endpoint and route to target network

    Arguments:
        client {VNS3Client} -- VNS3 Api client
        tunnel_name {str} -- Name to be used for tunnel
        tunnel_secret {str} -- Pre-Shared Secret for use on both sides of tunnel
        target_ip {str} -- IP address of target endpoint
        target_network_cidr {str or ipaddress.IPv4Network} -- CIDR of target network for routing
        vti_block {str} -- CIDR to use for network interface

    Keyword Arguments:
        target_network_name {str} -- [description] (default: {None})
        tunnel_parameters {dict} -- parameters to use for IPsec endpoint (default: {{}})
        route_parameters {dict} -- parameters to use for route (default: {{}})

    Returns:
        [Tuple[IpsecRemoteEndpoint, Dict]]
    """
    ipsec_endpoint = client.ipsec.post_create_ipsec_endpoint(
        **dict(
            {
                "name": tunnel_name,
                "ipaddress": target_ip,
                "secret": tunnel_secret,
                "pfs": True,
                "ike_version": 2,
                "nat_t_enabled": "False",  # # older versions of VNS3 required string parameters.
                "extra_config": "local-peer-id=%s" % client.configuration.host_uri,
                "vpn_type": "vti",
                "route_based_int_address": str(vti_block),
                "route_based_local": "0.0.0.0/0",
                "route_based_remote": "0.0.0.0/0",
            },
            **tunnel_parameters
        )
    )

    routes = client.routing.post_create_route(
        **dict(
            {
                "cidr": target_network_cidr,
                "description": "Route to %s via tunnel" % target_network_name
                or target_network_cidr,
                "tunnel": list(ipsec_endpoint.response.tunnels.keys())[0],
                "advertise": "False",
                "gateway": "",
                "metric": 0,
            },
            **route_parameters
        )
    )

    return {"endpoint": ipsec_endpoint.data, "routes": routes.data}
