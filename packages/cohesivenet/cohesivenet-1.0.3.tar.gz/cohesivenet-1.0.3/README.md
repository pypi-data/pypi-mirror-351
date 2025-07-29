# Python Cohesive Networks SDK
[![contact][contact-image]][contact-url] ![contact][python-versions-badge]

Cohesive Networks SDK is Python tool providing access to the VNS3 and VNS3:ms APIs from applications written in Python. It also includes common pipelines and macro functions for building network topologies.

## API Versions supported
The SDK will make best efforts to always be backwards compatible. All SDK releases will support VNS3 versions starting with VNS3 v4.8.4 and VNS3:ms starting with v2.1.1.

| cohesivenet==X |    VNS3 API    |     MS API     |
|----------------|:--------------:|:--------------:|
|  0.4.1-1.x.x   |  4.8.4-6.0.0   |   2.1.1-2.5.X  |
|     0.4.0      |  4.8.4-5.0.0   |   2.1.1-2.3.5  |
|     0.3.X      |  4.8.4-4.11.3  |   2.1.1-2.3.5  |
| 0.1.35-0.2.X   |  4.8.4-4.10.1  |   2.1.1-2.3.5  |
|     0.1.34     |  4.8.4-4.10.1  |       N/A      |    # MS SDK not supported
|     0.1.33     |  4.8.4-4.9.2   |       N/A      |    # MS SDK not supported
|     0.1.32     |  4.8.4-4.9.1   |       N/A      |    # MS SDK not supported
|     0.1.0-31   |      4.8.4     |       N/A      |    # MS SDK not supported
    
- View [VNS3 API specifications](https://docs.cohesive.net/apis/vns3/v/) with SDK examples.
- View [VNS3:ms API specifications](https://docs.cohesive.net/apis/vns3-ms/v/) with SDK examples.

## Installation

You can PIP install with

```sh
pip install cohesivenet
```
(you may need to run `pip` with root permission: `sudo pip install cohesivenet`)

or Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

## Usage

### Configuring a Client

```python
import cohesivenet
from pprint import pprint

configuration = cohesivenet.Configuration(
    host='[vns3-host]:8000',
    username='api',         
    password='YOUR_PASSWORD',
    verify_ssl=False) # Local cert is used by default. Can add your own cert.
# Configure HTTP basic authorization: basicAuth
configuration.username = 'api'
configuration.password = 'YOUR_PASSWORD'
configuration.host = "[vns3-host]:8000"
# Create an instance of the API class
vns3_controller = cohesivenet.VNS3Client(configuration)

try:
    api_response = vns3_controller.config.get_config()
    pprint(api_response)
except cohesivenet.ApiException as e:
    print("Exception fetching VNS3 Configuration get_config(): %s\n" % e)

# OR
from cohesivenet.macros import connect as vns3_connect

vns3_host = "55.55.55.55:8000"
api_user = "api"
api_ps = "test1234"
vns3 = vns3_connect.get_client(vns3_host, api_user, api_ps)
config = vns3.config.get_config()
print(config.response)
```

### Storing state VNS3 Client
Sometimes its useful to be able to cache particular state on VNS3 client as it is passed through scripts. This can be used with the `add_to_state` function on a VNS3Client:

```python
from cohesivenet.macros import vns3_connect

vns3 = vns3_connect.get_vns3_client(
    host="10.10.10.10:8000",
    username="api",
    password="heresmypassword"
)

peering_status_data = vns3.peering.get_peering_status()
my_peer_id = peering_status_data.response.id
vns3.add_to_state('peer_id', my_peer_id)

# Later to retrieve
vns3.query_state('peer_id') # => my_peer_id

# Viewing entire state:
vns3.state # => dict

# Update state with dict:
my_state_updates = {'peer_id': my_peer_id, 'secondary_ip': my_secondary_ip}
vns3.update_state(my_state_updates)
```

### Methods
Each sub-api is available from the VNS3Client instance as follows:

```python
# VNS3
vns3_client.access                # Manage access urls and api tokens
vns3_client.bgp                   # BGPApi for Border Gateway Protocol methods
vns3_client.config                # ConfigurationApi provides VNS3 config methods
vns3_client.firewall              # FirewallApi for configuring VNS3 policies
vns3_client.ipsec                 # IPsecApi for IPsec tunnel methods
vns3_client.interfaces            # InterfacesApi for viewing VNS3 interfaces
vns3_client.monitoring            # MonitoringAlertingApi
vns3_client.network_edge_plugins  # NetworkEdgePluginsApi
vns3_client.overlay_network       # OverlayNetworkApi for managing the overlay network
vns3_client.peering               # PeeringApi for peering VNS3 controllers
vns3_client.routing               # RoutingApi for configuring routing
vns3_client.snapshots             # SnapshotsApi for managing backups
vns3_client.sys_admin             # SystemAdministrationApi for access and sys admin tasks
vns3_client.licensing             # LicensingApi for controller licensing 

# VNS3:ms
ms_client.access                  # Provision short-lived access URLs or API keys for any VNS3 controller in your topology
ms_client.admin                   # Configure VNS3:ms administration settings such as LDAP integration
ms_client.vns3_management         # Manage VNS3 controllers in your network topology, automating snapshots, HA and more
ms_client.cloud_monitoring        # Configure and monitor your cloud by tracking cloud VPCs, virtual networks and VNS3 topologies
ms_client.system                  # System configuration such as SSL, NTP hosts and remote support
ms_client.backups                 # Configure backups for VNS3:ms and your controller snapshots
ms_client.user                    # User management endpoints for configuring credentials
```

### Common API patterns: `cohesivenet.macros`
Many API calls are called together to configure a topology or update a network configuration. More macros will be added to 
increasingly simplify VNS3 topology creation and configuration. More documentation to come.

```python
macros.admin                  # Admin operations typically applied to multiple controllers at once
macros.config                 # configuring multiple clients
macros.connect                # connecting to clients
macros.firewall               # firewall operations like idempotently creating full firewall
macros.ipsec                  # ipsec operations like creating a tunnel and then a route
macros.network_edge_plugins   # Manage container system network, images and running containers
macros.overlay_network        # overlay network functions like calculating network segments of the overlay
macros.peering                # topology peering operations like creating a peering mesh between controllers
macros.routing                # Operations for updating routing in your topology
macros.state                  # Methods for fetching the state of your controller(s)
```

### Logging
The SDK can be configured to emit logs for better visibility into what it's doing. The SDK supports INFO, DEBUG, and ERROR logging.

There are two ways to enable it:

1. Set the environment variable `COHESIVE_LOG_LEVEL` to the value `debug`, `info` or `error`

   ```sh
   $ export COHESIVE_LOG_LEVEL=debug
   ```

2. Enable it through Python's logging module:

   ```python
   import logging
   logging.basicConfig()
   logging.getLogger('cohesivenet').setLevel(logging.DEBUG)
   ```

## Author

solutions@cohesive.net

<!-- Markdown links -->

[contact-image]: https://img.shields.io/badge/contact-support-blue.svg?style=flat-square
[contact-url]: https://support.cohesive.net/support/home
[python-versions-badge]: https://img.shields.io/badge/python-3.5%20%7C%203.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue