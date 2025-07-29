from __future__ import absolute_import

# flake8: noqa

# import apis into api package
from cohesivenet.api.vns3.bgp_api import BGPApiRouter as BGPApi
from cohesivenet.api.vns3.configuration_api import (
    ConfigurationApiRouter as ConfigurationApi,
)
from cohesivenet.api.vns3.firewall_api import FirewallApiRouter as FirewallApi
from cohesivenet.api.vns3.ipsec_api import IPsecApiRouter as IPsecApi
from cohesivenet.api.vns3.interfaces_api import InterfacesApiRouter as InterfacesApi
from cohesivenet.api.vns3.licensing_api import LicensingApiRouter as LicensingApi
from cohesivenet.api.vns3.monitoring_alerting_api import (
    MonitoringAlertingApiRouter as MonitoringAlertingApi,
)
from cohesivenet.api.vns3.network_edge_plugins_api import (
    NetworkEdgePluginsApiRouter as NetworkEdgePluginsApi,
)
from cohesivenet.api.vns3.overlay_network_api import (
    OverlayNetworkApiRouter as OverlayNetworkApi,
)
from cohesivenet.api.vns3.peering_api import PeeringApiRouter as PeeringApi
from cohesivenet.api.vns3.routing_api import RoutingApiRouter as RoutingApi
from cohesivenet.api.vns3.snapshots_api import SnapshotsApiRouter as SnapshotsApi
from cohesivenet.api.vns3.system_administration_api import (
    SystemAdministrationApiRouter as SystemAdministrationApi,
)
from cohesivenet.api.vns3.access_api import AccessApiRouter as AccessApi
