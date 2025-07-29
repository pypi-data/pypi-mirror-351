from __future__ import absolute_import

import pytest

from tests.rest_mock import RestClientMock

import cohesivenet
import cohesivenet.api.vns3ms as vns3ms_api
from cohesivenet import MSClient, Configuration, LATEST_VNS3_MS_VERSION
from cohesivenet.rest import ApiException


class TestVNS3Client(object):
    """Test VNS3ms API client"""

    def test_api_properties(self):
        """Test all API groups are accessible as properties"""
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0",
                username="api",
                api_key="abcdefge",
                verify_ssl=False,
            )
        )

        assert hasattr(api_client, "access")
        assert type(api_client.access) is vns3ms_api.AccessApi
        assert hasattr(api_client, "admin")
        assert type(api_client.admin) is vns3ms_api.AdministrationApi
        assert hasattr(api_client, "backups")
        assert type(api_client.backups) is vns3ms_api.BackupsApi
        assert hasattr(api_client, "cloud_monitoring")
        assert type(api_client.cloud_monitoring) is vns3ms_api.CloudMonitoringApi
        assert hasattr(api_client, "system")
        assert type(api_client.system) is vns3ms_api.SystemApi
        assert hasattr(api_client, "user")
        assert type(api_client.user) is vns3ms_api.UserApi
        assert hasattr(api_client, "vns3_management")
        assert type(api_client.vns3_management) is vns3ms_api.VNS3ManagementApi

    def test_get_client_state(self):
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0:8000",
                username="api",
                api_key="abcdefge",
                verify_ssl=False,
            )
        )

        state = api_client.state
        assert type(state) is dict
        assert len(state) == 0

    def test_get_latest_available_version(self):
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0:8000",
                username="api",
                api_key="abcdefge",
                verify_ssl=False,
            )
        )

        latest_version = api_client.latest_version()
        assert LATEST_VNS3_MS_VERSION == latest_version

    def test_add_client_state(self):
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0:8000",
                username="api",
                api_key="abcdefge",
                verify_ssl=False,
            )
        )

        api_client.add_to_state("private_ip", "10.0.24.30")
        state = api_client.state
        assert "private_ip" in state and state["private_ip"] == "10.0.24.30"
        assert len(state) == 1

    def test_update_client_state(self):
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0",
                username="api",
                api_key="abcdefge",
                verify_ssl=False,
            )
        )

        updates = {
            "topology_container_network": "192.169.16.0/24",
            "subnet": "10.0.2.0/24",
        }
        api_client.update_state(updates)
        state = api_client.state
        assert set(updates.keys()).issubset(set(state.keys()))
        assert state["subnet"] == updates["subnet"]
        assert len(state) == 2

    def test_query_state(self):
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0",
                username="api",
                api_key="abcdefge",
                verify_ssl=False,
            )
        )

        test_value = 12312
        updates = {
            "container_network": "192.169.16.0/28",
            "subnet": "10.0.2.0/24",
            "test_key": test_value,
        }

        api_client.update_state(updates)
        assert api_client.query_state("test_key") == test_value

    def test_host_uri_property(self):
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0:443",
                username="api",
                api_key="abcdefge",
                verify_ssl=False,
            )
        )
        assert api_client.host_uri == "0.0.0.0"

    def test_api_version_routing(self):
        """Test api_builder.VersionRouter inits class based on class correctly"""
        api_client = MSClient(
            configuration=Configuration(
                host="0.0.0.0",
                username="api",
                password="password",
                verify_ssl=False,
            )
        )

        api_client.ms_version = "2.1.1"
        expected_api_methods = [
            "put_activate_api_key",
            "post_create_token",
            "put_expire_token",
            "put_invalidate_api_key_tokens",
            "get_api_keys",
            "post_create_api_key",
            "put_update_api_key",
            "delete_api_key",
        ]

        access_api = api_client.access
        for method_name in expected_api_methods:
            assert hasattr(access_api, method_name), (
                "Missing method %s on access_api" % method_name
            )
