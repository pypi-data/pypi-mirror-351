from pydantic import Field

from ..base import DataGardenModel, DataGardenModelLegends
from .base_health import HealthBaseKeys
from .death_statistics import DeathStatistics, DeathStatisticsKeys
from .health_care_facilities import HealthCareFacilities, HealthCareFacilitiesKeys
from .monitor import HealthMonitor, HealthMonitorKeys
from .vacination_coverage import VaccinationCoverage, VaccinationCoverageKeys


class HealthV1Keys(
    HealthBaseKeys,
    DeathStatisticsKeys,
    HealthCareFacilitiesKeys,
    VaccinationCoverageKeys,
    HealthMonitorKeys,
):
    DEATH_STATISTICS = "death_statistics"
    HEALTH_CARE_FACILITIES = "health_care_facilities"
    VACINATION_COVERAGE = "vacination_coverage"
    HEALTH_MONITOR = "health_monitor"
    DATAGARDEN_MODEL_NAME = "Health"


class HealthV1Legends(DataGardenModelLegends):
    MODEL_LEGEND: str = "Health data for a region."
    DEATH_STATISTICS = "Death statistics for the rgion."
    HEALTH_CARE_FACILITIES = "Healthcare facilities available in the region."
    VACINATION_COVERAGE = "Vaccination coverage per region."
    HEALTH_MONITOR = "Health monitor data for the region."


L = HealthV1Legends


class HealthV1(DataGardenModel):
    datagarden_model_version: str = Field("v1.0", frozen=True, description=L.DATAGARDEN_MODEL_VERSION)

    death_statistics: DeathStatistics = Field(default_factory=DeathStatistics, description=L.DEATH_STATISTICS)
    health_care_facilities: HealthCareFacilities = Field(
        default_factory=HealthCareFacilities, description=L.HEALTH_CARE_FACILITIES
    )
    vacination_coverage: VaccinationCoverage = Field(
        default_factory=VaccinationCoverage, description=L.VACINATION_COVERAGE
    )
    health_monitor: HealthMonitor = Field(default_factory=HealthMonitor, description=L.HEALTH_MONITOR)
