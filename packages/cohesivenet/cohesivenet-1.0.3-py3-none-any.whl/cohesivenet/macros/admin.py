import time
from typing import Dict, List

from cohesivenet import VNS3Client, data_types
from cohesivenet.macros import api_operations


def roll_api_password(
    new_password, clients: List[VNS3Client]
) -> data_types.BulkOperationResult:
    """roll_api_password

    Update all passwords for clients

    Arguments:
        new_password {str}
        clients {List[VNS3Client]}

    Returns:
        BulkOperationResult - tuple containing the clients that
        succeeded and the clients that failed with their exceptions
    """

    def _update_password(_client):
        resp = _client.config.put_update_api_password(password=new_password)
        _client.configuration.password = new_password
        return resp

    return api_operations.__bulk_call_client(
        clients, _update_password, parallelize=True
    )


def disable_uis(clients: List[VNS3Client]):
    """disable_uis

    Disable all UIs for clients

    Arguments:
        clients {List} -- List of VNS3Clients

    Returns:
        BulkOperationResult
    """

    def _disable_ui(_client):
        resp = _client.config.put_update_admin_ui(enabled=False)
        # required to avoid 502 from api resetting itself
        time.sleep(2.0)
        return resp

    return api_operations.__bulk_call_client(clients, _disable_ui)


def roll_ui_credentials(
    new_credentials: Dict, clients: List[VNS3Client], enable_ui=False
):
    """Update UI credentials to common credentials

    Arguments:
        new_credentials {dict} -- {username: str, password: str}
        clients {List} -- List of VNS3 clients
        enable_ui {Bool} -- whether to enable UI

    Returns:
        BulkOperationResult
    """
    assert "username" in new_credentials, '"username" required in new_credentials arg'
    assert "password" in new_credentials, '"password" required in new_credentials arg'

    def _update_ui_credentials(_client):
        resp = _client.config.put_update_admin_ui(
            **{
                "admin_username": new_credentials.get("username"),
                "admin_password": new_credentials.get("password"),
                "enabled": enable_ui,
            }
        )
        # required to avoid 502 from api resetting itself
        time.sleep(2.0)
        return resp

    return api_operations.__bulk_call_client(
        clients, _update_ui_credentials, parallelize=True
    )
