class AccessApiData(object):
    TokenResponse = {"api_token": "f76a2cb3ca8107ba0aaa0394ca929cd622580938"}

    ExpireTokenResponse = {
        "response_type": "success",
        "response": {"message": "Successfully expired token"},
    }

    ApiKeysResponse = {
        "response_type": "success",
        "response": [
            {
                "id": 3,
                "name": "default",
                "enabled": True,
                "created_at": "2020-05-06T19:02:40.000Z",
                "default_key": False,
                "active_tokens": 1,
                "expired_tokens": 7,
                "last_access_time": "2020-05-12T22:43:13.000Z",
                "last_access_ip": "54.236.197.84",
            }
        ],
    }

    ExpireKeyTokens = {
        "response_type": "success",
        "response": {
            "message": "Invalidated 1 tokens",
            "name": "test",
            "id": 2,
            "enabled": True,
            "active_tokens": 0,
        },
    }

    NewApiKeyResponse = {
        "response_type": "success",
        "response": {
            "message": "Key created",
            "name": "api-created-new-again",
            "api_key": "4f00ac88739f00dbb8fd3b878a96d9e94aeae3b6a0b0048fd8427d5eee722b70c85c72de2f91331c18c90e90befd54e03b600efe1aa9c21e699256be87b9f9ef",
            "id": 4,
            "active_tokens": 0,
            "enabled": True,
        },
    }

    ApiKeyUpdatedResponse = {
        "response_type": "success",
        "response": {
            "message": "Key updated",
            "name": "test-updated",
            "id": 2,
            "enabled": True,
            "active_tokens": 1,
        },
    }


class AdminApiData(object):
    LdapSettingsResponse = {
        "response_type": "success",
        "response": {
            "ldap_host": None,
            "ldap_port": None,
            "ldap_ssl": None,
            "ldap_binddn": None,
            "ldap_bindpw": None,
        },
    }

    LdapUserSchemaResponse = {
        "response_type": "success",
        "response": {
            "ldap_user_base": "DN",
            "ldap_user_id_attribute": "1",
            "ldap_user_list_filter": "subtree",
        },
    }

    LdapGroupSchemaResponse = {
        "response_type": "success",
        "response": {
            "ldap_group_required": True,
            "ldap_group_base": "vns3admin",
            "ldap_group_id_attribute": "fact",
            "ldap_group_list_filter": None,
            "ldap_group_member_attribute": "again",
            "ldap_group_member_attr_format": "UserDN",
            "ldap_search_scope": "subtree",
        },
    }


class BackupsApiData(object):
    CreateBackupResponse = {
        "response_type": "success",
        "response": {
            "status": "Backup process queued",
            "uuid": "ce81bb5b-a917-49c7-8efd-d97d158d31fe",
        },
    }

    BackupJobStatusResponse = {
        "response_type": "success",
        "response": {
            "uuid": "ce81bb5b-a917-49c7-8efd-d97d158d31fe",
            "status": "Queued",
            "filename": "",
        },
    }


class CloudMonitoringApiData(object):
    CreateVirtualNetworkResponse = {
        "response_type": "success",
        "response": {"msg": "Virtual Network created", "id": 1},
    }

    CreateVns3TopologyResponse = {
        "response_type": "success",
        "response": {"msg": "VNS3 Topology created", "id": 1},
    }

    Vns3Topology = {
        "id": 1,
        "name": "Test VNS3 Topology",
        "virtual_network_name": "dev-env-network",
        "virtual_network_id": 1,
        "vns3_controllers": [{"id": 1, "name": "test-vns3-bp"}],
        "description": None,
    }

    Vns3TopologyDetail = {"response": Vns3Topology}

    Vns3TopologyList = {"response": [Vns3Topology]}

    VirtualNetwork = {
        "id": 1,
        "name": "dev-env-network",
        "description": "test environment",
        "created_at": "2020-05-14T14:27:16.000Z",
    }

    VirtualNetworkDetail = {"response": VirtualNetwork}

    VirtualNetworkList = {"response": [VirtualNetwork]}

    CloudVlan = {
        "id": 1,
        "name": "AWS VPC VLAN",
        "virtual_network_name": "dev-env-network",
        "virtual_network_id": 1,
        "description": "Test description for my testing topology turtles",
    }

    CloudVlanDetail = {"response": CloudVlan}

    CloudVlanList = {"response": [CloudVlan]}

    CloudVlanComponent = {
        "id": 1,
        "name": "dev-env-bplatta-vpc",
        "cloud_vlan_id": 1,
        "cloud_vlan": "AWS VPC VLAN",
        "cloud_cred_id": 1,
        "cloud_type": "EC2",
        "region": "us-east-1",
        "description": "My  vlan test",
    }

    CloudVlanComponentDetail = {"response": CloudVlanComponent}

    CloudVlanComponentList = {"response": [CloudVlanComponent]}

    Webhook1 = {
        "id": 1,
        "name": "bens-test-webhook",
        "validate_cert": False,
        "created_at": "2020-05-18T16:23:37.279Z",
        "updated_at": "2020-05-18T16:23:37.279Z",
        "body": "{}",
        "url": None,
        "custom_properties": [],
        "headers": [],
        "parameters": [],
        "events": ["tunnel_down", "tunnel_up"],
    }

    Webhook2 = {
        "id": 1,
        "name": "bens-2-webhook",
        "validate_cert": False,
        "created_at": "2020-05-18T16:23:37.279Z",
        "updated_at": "2020-05-18T16:23:37.279Z",
        "body": "{}",
        "url": None,
        "custom_properties": [{"name": "Prop1", "value": "val1"}],
        "headers": [],
        "parameters": [],
        "events": ["tunnel_down"],
    }

    WebhookDetail = {"response_type": "success", "response": Webhook1}

    WebhookListResponse = {"response_type": "success", "response": [Webhook1, Webhook2]}

    Alert = {
        "custom_properties": [],
        "events": ["test", "tunnel_down", "tunnel_up"],
        "enabled": True,
        "updated_at": "2020-05-18T16:42:19.407Z",
        "url": "https://hooks.slack.com/services/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",
        "webhook_id": 1,
        "id": 1,
        "created_at": "2020-05-18T16:42:19.407Z",
        "name": "BensAlert",
    }

    AlertDetail = {"response_type": "success", "response": Alert}

    AlertListResponse = {"response_type": "success", "response": [Alert]}


class SystemApiData(object):
    NTPHosts = {
        "response_type": "success",
        "response": {
            "0": "0.ubuntu.pool.ntp.org",
            "1": "1.ubuntu.pool.ntp.org",
            "2": "2.ubuntu.pool.ntp.org",
            "3": "3.ubuntu.pool.ntp.org",
            "4": "ntp.ubuntu.com",
        },
    }

    CredTypeDetails = {
        "name": "EC2",
        "code": "ec2",
        "fields": [
            {
                "name": "Use VNS3:ms IAM Role (Recommended Option)",
                "description": "Use VNS3:ms IAM Role to provide credentials",
                "required": True,
                "type": "BOOLEAN",
            },
            {
                "name": "Account ID",
                "description": "AWS Account ID (optional - VNS3:ms will attempt to fill if left blank)",
                "required": False,
                "type": "STRING",
            },
            {
                "name": "Access Key",
                "description": "AWS Access key",
                "required": True,
                "type": "STRING",
            },
            {
                "name": "Secret Key",
                "description": "AWS Secret key",
                "required": True,
                "type": "PASSWORD",
            },
            {
                "name": "GovCloud",
                "description": "These creds are for use in the EC2 GovCloud",
                "required": True,
                "type": "BOOLEAN",
            },
        ],
    }


class Vns3ManagementApiData(object):
    CreateVns3ControllerResponse = {
        "response_type": "success",
        "response": {"msg": "VNS3 Controller created", "id": 1},
    }

    Vns3SnapshotsList = {
        "response": {
            "snapshots": [
                {
                    "snapshot_id": 1,
                    "created_at": "2020-05-15T17:42:41.000Z",
                    "snapshot_name": "snapshot_20200515_1589564561_52.72.51.23",
                    "snapshot_size": 2072122,
                    "sha1_checksum": "c9cbcaca7d0e1996ae2411fde50f74881eeac542",
                    "available": True,
                    "status": "Stored locally",
                    "vns3_controller_id": 1,
                    "vns3_controller_name": "test-vns3-bp",
                }
            ],
            "failed_snapshots": [],
        }
    }

    ControllerReport = {
        "response_type": "success",
        "response": {
            "snapshot_date": "2020-05-15",
            "snapshot": [
                {
                    "controller_id": 1,
                    "controller_name": "test-vns3-bp",
                    "controller_version": "3.5-default",
                    "active": True,
                    "created_date": "2020-05-14T14:29:59+00:00",
                    "topology_id": 1,
                    "topology_name": "Test VNS3 Topology",
                    "virtual_network_id": 1,
                    "virtual_network_name": "dev-env-network",
                    "ha_backup_enabled": False,
                }
            ],
        },
    }

    Vns3Controller = {
        "id": 1,
        "name": "test-vns3-bp",
        "owner": "admin",
        "virtual_network_id": 1,
        "virtual_network": "dev-env-network",
        "vns3_topology_id": 1,
        "vns3_topology": "Test VNS3 Topology",
        "vns3_address": "10.0.1.34",
        "private_ip_address": None,
        "vns3_version": "3.5-default",
        "licensed": None,
        "active": True,
        "peered": None,
        "description": None,
        "controller_status": {
            "last_contact_time": "2020-05-15T17:47:25.000Z",
            "last_successful_contact_time": "2020-05-15T17:47:25.000Z",
            "last_contact_code": 200,
            "last_contact_result": "OK",
            "failed_contact_count": 0,
            "alerts_enabled": False,
        },
        "alerts_enabled": False,
    }

    Vns3ControllerDetail = {"response": Vns3Controller}

    Vns3ControllerList = {"response": [Vns3Controller]}

    Vns3ControllerHaDetail = {
        "response_type": "success",
        "response": {
            "ha_enabled": True,
            "ha_initialised": False,
            "ha_cloud_validated": True,
            "ms_sync_state": "Available",
            "ms_sync_fail_count": 0,
            "backup_active": False,
            "backup_sync_fail_count": 0,
            "ha_cloud_cred_id": 1,
            "primary_server_available": True,
            "backup_server_available": False,
            "ha_type": "cold",
            "ha_sync_processing": False,
            "ha_instance_id": "",
            "ha_image_id": "ami-12341234",
        },
    }


class UserApiData(object):

    CredsList = {
        "response_type": "success",
        "response": [
            {
                "id": 1,
                "name": "BensEc2Cred",
                "code": "ec2",
                "verified": True,
                "verification_message": "Cloud creds verified",
            }
        ],
    }
