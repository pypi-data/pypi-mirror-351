from typing import Optional

from pydantic import Field

from datagarden_models.models.base import DataGardenSubModel
from datagarden_models.models.base.standard_models import (
    EconomicsValue,
    ValueAndPercentage,
)


###########################################
########## Start Model defenition #########
###########################################
class HouseholdIncomeLegends:
    AVERAGE_INCOME = "Average household income."
    PERCENTAGE_HIGH_INCOME = "Percentage of households with high income."
    PERCENTAGE_LOW_INCOME = "Percentage of households with low income."
    GDHI_PER_PERSON = "Gross Disposable Household Income per person."


HI = HouseholdIncomeLegends


class HouseholdIncome(DataGardenSubModel):
    average_income: Optional[EconomicsValue] = Field(default=None, description=HI.AVERAGE_INCOME)
    percentage_high_income: Optional[float] = Field(default=None, description=HI.PERCENTAGE_HIGH_INCOME)
    percentage_low_income: Optional[float] = Field(default=None, description=HI.PERCENTAGE_LOW_INCOME)
    gdhi_per_person: Optional[EconomicsValue] = Field(default=None, description=HI.GDHI_PER_PERSON)


class HouseholdIncomeKeys:
    AVERAGE_INCOME = "average_income"
    PERCENTAGE_HIGH_INCOME = "percentage_high_income"
    PERCENTAGE_LOW_INCOME = "percentage_low_income"
    GDHI_PER_PERSON = "gdhi_per_person"


###########################################
########## Start Model defenition #########
###########################################
class WagesLegends:
    AVERAGE_MONTHLY_WAGE = "Gross median wages per month."
    AVERAGE_WEEKLY_WAGE = "Gross median wages per week."


WL = WagesLegends


class Wages(DataGardenSubModel):
    average_monthly_wage: Optional[EconomicsValue] = Field(default=None, description=WL.AVERAGE_MONTHLY_WAGE)
    average_weekly_wage: Optional[EconomicsValue] = Field(default=None, description=WL.AVERAGE_WEEKLY_WAGE)


class WagesKeys:
    AVERAGE_MONTHLY_WAGE = "average_monthly_wage"
    AVERAGE_WEEKLY_WAGE = "average_weekly_wage"


###########################################
########## Start Model defenition #########
###########################################
class EconomicsLegends:
    HOUSEHOLD_INCOME = "Average household income."
    SOCIAL_WELFARE_BENEFIT = "Population count with social welfare benefit other then pension."
    WAGES = "Wage information."


EL = EconomicsLegends


class Economics(DataGardenSubModel):
    household_income: Optional[HouseholdIncome] = Field(default=None, description=EL.HOUSEHOLD_INCOME)
    social_welfare_benefit: Optional[ValueAndPercentage] = Field(
        default=None, description=EL.SOCIAL_WELFARE_BENEFIT
    )
    wages: Optional[Wages] = Field(default=None, description=EL.WAGES)


class EconomicsKeys(HouseholdIncomeKeys, WagesKeys):
    HOUSEHOLD_INCOME = "household_income"
    WAGES = "wages"
    SOCIAL_WELFARE_BENEFIT = "social_welfare_benefit"
