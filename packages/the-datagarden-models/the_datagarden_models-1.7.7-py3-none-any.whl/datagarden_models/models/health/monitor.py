from typing import Optional

from pydantic import Field

from datagarden_models.models.base import DataGardenSubModel


class HealthMonitorKeys:
    BY_AGE_GROUP = "by_age_group"


class HealthMonitorLegends:
    BY_AGE_GROUP = "Health monitor data by age group"


L = HealthMonitorLegends


class HealthMonitor(DataGardenSubModel):
    by_age_group: Optional[dict[str, dict[str, float]]] = Field(default=None, description=L.BY_AGE_GROUP)
