from typing import Optional

from pydantic import Field

from datagarden_models.models.base import DataGardenSubModel


class ConsumerTrustKeys:
    NATIONAL_INDICATORS = "national_indicators"
    BY_POPULATION_GROUP = "by_population_group"


class ConsumerTrustLegends:
    NATIONAL_INDICATORS = (
        "National indicators of consumer trust, usually defined by national statistics "
        "agencies. Be careful to compare data from different countries."
    )
    BY_POPULATION_GROUP = (
        "Indicators of consumer trust by population group. Usually defined by national statistics "
        "agencies. Be careful to compare data from different countries."
    )


L = ConsumerTrustLegends


class ConsumerTrust(DataGardenSubModel):
    national_indicators: Optional[dict[str, float]] = Field(default=None, description=L.NATIONAL_INDICATORS)
    by_population_group: Optional[dict[str, dict[str, float]]] = Field(
        default=None, description=L.BY_POPULATION_GROUP
    )
