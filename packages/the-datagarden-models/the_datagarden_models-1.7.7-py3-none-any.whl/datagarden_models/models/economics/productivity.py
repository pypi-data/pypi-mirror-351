from typing import Optional

from pydantic import Field

from datagarden_models.models.base import DataGardenSubModel, EconomicsValue


###########################################
########## Start Model defenition #########
###########################################
class ProductivityLegends:
    VALUE_ADDED_PER_WORKED_HOUR = "Value added per worked hour."


PL = ProductivityLegends


class Productivity(DataGardenSubModel):
    value_added_per_worked_hour: Optional[EconomicsValue] = Field(
        default=None, description=PL.VALUE_ADDED_PER_WORKED_HOUR
    )


class ProductivityKeys:
    VALUE_ADDED_PER_WORKED_HOUR = "value_added_per_worked_hour"
