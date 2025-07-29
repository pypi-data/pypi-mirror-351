from pydantic import Field

from ..base import DataGardenModel, DataGardenModelLegends
from .consumer_trust import ConsumerTrust, ConsumerTrustKeys
from .local_facilities import LocalFacilities, LocalFacilitiesKeys


class SocialEnvironmentV1Keys(
    LocalFacilitiesKeys,
    ConsumerTrustKeys,
):
    LOCAL_FACILITIES = "local_facilities"
    CONSUMER_TRUST = "consumer_trust"
    DATAGARDEN_MODEL_NAME = "SocialEnvironment"


class SocialEnvironmentV1Legends(DataGardenModelLegends):
    MODEL_LEGEND = "Social environment data for a region. "
    LOCAL_FACILITIES = "Information about available of local facilities"
    CONSUMER_TRUST = "Information about consumer trust"


L = SocialEnvironmentV1Legends


class SocialEnvironmentV1(DataGardenModel):
    datagarden_model_version: str = Field("v1.0", frozen=True, description=L.DATAGARDEN_MODEL_VERSION)
    local_facilities: LocalFacilities = Field(default_factory=LocalFacilities, description=L.LOCAL_FACILITIES)
    consumer_trust: ConsumerTrust = Field(default_factory=ConsumerTrust, description=L.CONSUMER_TRUST)
