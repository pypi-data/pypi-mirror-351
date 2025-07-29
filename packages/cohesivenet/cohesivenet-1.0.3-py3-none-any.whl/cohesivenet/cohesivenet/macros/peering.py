from functools import partial as bind

from cohesivenet import data_types, CohesiveSDKException, Logger
from cohesivenet.macros import api_operations as api_ops
from cohesivenet.macros.state import (
    VNS3Attr,
    fetch_state_attribute,
    attribute_supported,
)


def set_peer_ids(clients, ids=None) -> data_types.BulkOperationResult:
    """Set peer ids for all clients. Assume order of clients passed as ids

    Arguments:
        clients {List[VNS3Client]}

    Returns:
        BulkOperationResult
    """

    def _set_peer_id(_client, i):
        get_resp = _client.peering.get_peering_status()
        if get_resp.response.id == i:
            _client.add_to_state(VNS3Attr.peer_id, i)
            return get_resp

        resp = _client.peering.put_self_peering_id(id=i)
        _client.add_to_state(VNS3Attr.peer_id, i)
        return resp

    ordered_ids = ids or range(1, len(clients) + 1)

    bound_api_calls = [
        bind(_set_peer_id, client, ordered_ids[index])
        for index, client in enumerate(clients)
    ]

    Logger.debug("Setting peer IDS: %s" % ordered_ids)
    return api_ops.__bulk_call_api(bound_api_calls, parallelize=True)


def _construct_peer_address_mapping(clients, address_type):
    """[summary]

    Arguments:
        clients {List[VNS3Client]}
        address_type {str} - one of primary_private_ip, secondary_private_ip, public_ip, public_dns

    Returns:
        List of tuples where first element is the client and second is a map for peers

        List[Tuple[VNS3Client, Dict]] -- [
            (client,  {
                [peer_id: str]: [peer_address: str],
                ...
            })
        ]
    """
    # fetch state if supported
    if attribute_supported(address_type):
        fetch_state_attribute(clients, address_type)

    client_indexes = range(len(clients))
    client_indexes_set = set(client_indexes)
    peer_address_mapping = []
    for index in client_indexes:
        this_client = clients[index]
        other_clients_indexes = client_indexes_set - {index}
        other_clients = [clients[i] for i in other_clients_indexes]
        client_peers = {
            c.query_state(VNS3Attr.peer_id): c.query_state(address_type)
            for c in other_clients
        }
        if not all(client_peers.values()):
            raise CohesiveSDKException(
                "Could not determine %s for some clients" % address_type
            )
        peer_address_mapping.append((this_client, client_peers))
    return peer_address_mapping


def peer_mesh(
    clients,
    peer_address_map=None,
    address_type=VNS3Attr.primary_private_ip,
    delay_configure=False,
    mtu=None,
):
    """peer_mesh Create a peering mesh by adding each client as peer for other clients.
       The order of the list of clients is the assumed peering id, i.e. client at clients[0]
       has peering id of 1, clients[1] has peering id of 2. Each TLS connection between peers
       is then automatically negotiated.

    Arguments:
        clients {List[VNS3Client]}

    Keyword Arguments:
        peer_address_map {Dict} - Optional map for peering addresses {
            [from_peer_id: str]: {
                [to_peer_id_1: str]: [peer_address_1: str],
                [to_peer_id_2: str]: [peer_address_2: str],
                ...
            }
        }
        address_type {str} - which address to use. Options: primary_private_ip, secondary_private_ip, public_ip or public_dns
        delay_configure {bool} -- delay automatic negotiation of peer (default: False)
        mtu {int} -- Override MTU for the peering TLS connection. VNS3 defaults to 1500. (default: {None})

    Raises:
        CohesiveSDKException

    Returns:
        data_types.BulkOperationResult
    """
    # fetch peer ids and set on clients
    ensure_peer_ids_result = fetch_state_attribute(clients, VNS3Attr.peer_id)
    if api_ops.bulk_operation_failed(ensure_peer_ids_result):
        errors_str = api_ops.stringify_bulk_result_exception(ensure_peer_ids_result)
        Logger.error("Failed to fetch peering Ids for all clients", errors=errors_str)
        raise CohesiveSDKException(
            "Failed to fetch peering Ids for all clients: %s" % errors_str
        )

    # constructu peer address mapping
    if peer_address_map is not None:
        Logger.debug("Using address map passed for peering mesh.")
        peer_id_to_client = {c.query_state(VNS3Attr.peer_id): c for c in clients}
        peer_address_mapping_tuples = [
            (peer_id_to_client[from_peer_id], to_peers_map)
            for from_peer_id, to_peers_map in peer_address_map.items()
        ]
    else:
        Logger.debug("Constructing peering mesh")
        peer_address_mapping_tuples = _construct_peer_address_mapping(
            clients, address_type
        )

    common_peer_kwargs = {}
    if delay_configure:
        common_peer_kwargs.update(force=False)
    if mtu:
        common_peer_kwargs.update(overlay_mtu=mtu)

    def create_all_peers_for_client(client, post_peer_kwargs):
        return [
            client.peering.post_create_peer(
                **dict(peering_request, **common_peer_kwargs)
            )
            for peering_request in post_peer_kwargs
        ]

    run_peering_funcs = []
    # bind api function calls for peer creations
    for vns3_client, peer_mapping in peer_address_mapping_tuples:
        run_peering_funcs.append(
            bind(
                create_all_peers_for_client,
                vns3_client,
                [
                    {"id": peer_id, "name": peer_address}
                    for peer_id, peer_address in peer_mapping.items()
                ],
            )
        )

    Logger.debug("Creating %d-way peering mesh." % len(clients))
    return api_ops.__bulk_call_api(run_peering_funcs, parallelize=True)
