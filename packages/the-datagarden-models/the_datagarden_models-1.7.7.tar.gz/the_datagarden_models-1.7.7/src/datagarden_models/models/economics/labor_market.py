from typing import Optional

from pydantic import Field

from datagarden_models.models.base import DataGardenSubModel

########## Start Model defenition #########


class LaborMarketStatusLegends:
    EMPLOYED = "Total number of employed persons."
    EMPLOYED_RATE = "Percentage of employed persons as percentage of working age population. (age 16-64)"
    UNEMPLOYED = "Total number of unemployed persons."
    UNEMPLOYMENT_RATE = (
        "Percentage of unemployed persons actively seeking work as percentage of aged population above 16."
    )
    INACTIVE = "Total number of inactive persons."
    INACTIVE_RATE = "Percentage of inactive persons as percentage of working age population. (age 16-64)"
    CLAIM_UNEMPLOYMENT_BENEFIT = "Total number of persons claiming unemployment benefits."
    CLAIM_UNEMPLOYMENT_BENEFIT_RATE = (
        "Percentage of persons claiming unemployment benefits as percentage of working age population. "
        "(age 16-64)"
    )


L = LaborMarketStatusLegends


class LaborMarketStatus(DataGardenSubModel):
    employed: Optional[float] = Field(default=None, description=L.EMPLOYED)
    employed_rate: Optional[float] = Field(default=None, description=L.EMPLOYED_RATE)
    unemployed: Optional[float] = Field(default=None, description=L.UNEMPLOYED)
    unemployment_rate: Optional[float] = Field(default=None, description=L.UNEMPLOYMENT_RATE)
    inactive: Optional[float] = Field(default=None, description=L.INACTIVE)
    inactive_rate: Optional[float] = Field(default=None, description=L.INACTIVE_RATE)
    claim_unemployment_benefit: Optional[float] = Field(
        default=None, description=L.CLAIM_UNEMPLOYMENT_BENEFIT
    )
    claim_unemployment_benefit_rate: Optional[float] = Field(
        default=None, description=L.CLAIM_UNEMPLOYMENT_BENEFIT_RATE
    )


class LaborMarketStatusKeys:
    EMPLOYED = "employed"
    EMPLOYED_RATE = "employed_rate"
    UNEMPLOYED = "unemployed"
    UNEMPLOYMENT_RATE = "unemployment_rate"
    INACTIVE = "inactive"
    INACTIVE_RATE = "inactive_rate"
    CLAIM_UNEMPLOYMENT_BENEFIT = "claim_unemployment_benefit"
    CLAIM_UNEMPLOYMENT_BENEFIT_RATE = "claim_unemployment_benefit_rate"
