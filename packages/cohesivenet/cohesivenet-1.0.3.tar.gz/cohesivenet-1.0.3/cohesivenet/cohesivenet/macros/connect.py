from typing import List

from cohesivenet import VNS3Client, Configuration, data_types, MSClient
from cohesivenet.macros import api_operations


def get_vns3_client(host, username=None, password=None, api_token=None, verify=False):
    """Get VNS3 API Client for host

    Arguments:
        host {str}
        username {str}
        password {str}

    Keyword Arguments:
        verify {bool} -- Verify SSL certificate (default: {False})

    Returns:
        [VNS3Client]
    """
    token_auth = api_token is not None
    username = username or "api"
    basic_auth = all([username, password])
    assert (
        basic_auth or token_auth
    ), "Must provide either username/password or api_token"
    return VNS3Client(
        Configuration(
            host=host,
            username=username,
            password=password,
            api_token=api_token,
            verify_ssl=verify,
        )
    )


# Alias for backwards compatability
get_client = get_vns3_client


def get_vns3_clients(*hosts):
    """Create VNS3Clients for host information

    Arguments:
        host {Dict} -- {
            host: str,
            username: str,
            password: str,
            verify: bool (Optional)
        }

    Returns:
        [List[VNS3Client]]
    """
    return [get_vns3_client(**host_data) for host_data in hosts]


# Alias for backwards compatability
get_clients = get_vns3_clients


def get_vns3_clients_common_creds(
    hosts, common_username, common_password, verify=False
):
    """Construct clients for each host

    Arguments:
        hosts {List[str]} -- list of host strings
        common_username {str}
        common_password {str}

    Keyword Arguments:
        verify {bool} -- verify SSL for client

    Returns:
        [List[VNS3Clients]]
    """
    return [
        get_vns3_client(host, common_username, common_password, verify)
        for host in hosts
    ]


# Alias for backwards compatability
get_clients_common_creds = get_vns3_clients_common_creds


def verify_client_connectivity(
    clients: List[VNS3Client],
) -> data_types.BulkOperationResult:
    """Verify the connectivty of provided clients by pinging API

    Arguments:
        clients {List[VNS3Client]}

    Returns:
        data_types.BulkOperationResult
    """

    def _ping_api(_client):
        return _client.sys_admin.get_config()

    return api_operations.__bulk_call_client(clients, _ping_api)


def get_ms_client(host, username=None, password=None, api_token=None, verify=False):
    """Get VNS3 API Client for host

    Arguments:
        host {str}
        username {str}
        password {str}

    Keyword Arguments:
        verify {bool} -- Verify SSL certificate (default: {False})

    Returns:
        [VNS3Client]
    """
    basic_auth = all([username, password])
    token_auth = api_token is not None
    assert (
        basic_auth or token_auth
    ), "Must provide either username/password or api_token"
    return MSClient(
        Configuration(
            host=host,
            username=username,
            password=password,
            api_token=api_token,
            verify_ssl=verify,
        )
    )
