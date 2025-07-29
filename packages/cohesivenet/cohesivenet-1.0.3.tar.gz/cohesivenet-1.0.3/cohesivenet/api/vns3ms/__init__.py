from __future__ import absolute_import

# flake8: noqa

# import apis into api package
from cohesivenet.api.vns3ms.access_api import AccessApiRouter as AccessApi
from cohesivenet.api.vns3ms.administration_api import (
    AdministrationApiRouter as AdministrationApi,
)
from cohesivenet.api.vns3ms.backups_api import BackupsApiRouter as BackupsApi
from cohesivenet.api.vns3ms.cloud_monitoring_api import (
    CloudMonitoringApiRouter as CloudMonitoringApi,
)
from cohesivenet.api.vns3ms.system_api import SystemApiRouter as SystemApi
from cohesivenet.api.vns3ms.user_api import UserApiRouter as UserApi
from cohesivenet.api.vns3ms.vns3_management_api import (
    VNS3ManagementApiRouter as VNS3ManagementApi,
)
