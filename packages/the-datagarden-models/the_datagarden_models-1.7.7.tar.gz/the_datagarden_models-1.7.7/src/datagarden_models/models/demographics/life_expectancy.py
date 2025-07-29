from typing import Optional

from pydantic import Field

from datagarden_models.models.base import DataGardenSubModel


class AgeGenderLifeExpectancyLegends:
    AGE_GENDER_MALE = (
        "Life expectancy for males. In number years still expected to live per age or age group."
    )
    AGE_GENDER_FEMALE = (
        "Life expectancy for females. In number years still expected to live per age or age group."
    )
    AGE_GENDER_TOTAL = (
        "Life expectancy for total population. In number years still expected to live per age or age group."
    )


AGL = AgeGenderLifeExpectancyLegends


class LifeExpectancyByAgeGender(DataGardenSubModel):
    male: dict = Field(default_factory=dict, description=AGL.AGE_GENDER_MALE)
    female: dict = Field(default_factory=dict, description=AGL.AGE_GENDER_FEMALE)
    total: dict = Field(default_factory=dict, description=AGL.AGE_GENDER_TOTAL)


class LifeExpectancyAtBirthLegends:
    MALE = (
        "Male Life expectancy at birth for birthyear of record period. In years expected to live when born."
    )
    FEMALE = (
        "Female Life expectancy at birth for birthyear of record period. In years expected to live when born."
    )
    TOTAL = (
        "Total Life expectancy at birth for birthyear of record period. In years expected to live when born."
    )


LEB = LifeExpectancyAtBirthLegends


class LifeExpectancyAtBirth(DataGardenSubModel):
    male: Optional[float] = Field(default=None, description=LEB.MALE)
    female: Optional[float] = Field(default=None, description=LEB.FEMALE)
    total: Optional[float] = Field(default=None, description=LEB.TOTAL)


class LifeExpectancyV1Keys:
    LIFE_EXPECTANCY_AT_BIRTH = "life_expectancy_at_birth"
    REMAINING_LIFE_EXPECTANCY = "remaining_life_expectancy"


class LifeExpectancyV1Legends:
    LIFE_EXPECTANCY_AT_BIRTH = (
        "Life expectancy per age or age group at birth. In years expected to live when born"
    )
    REMAINING_LIFE_EXPECTANCY = (
        "Life expectancy per age or age group at current age. In years expected to live as of current age"
    )


L = LifeExpectancyV1Legends


class LifeExpectancy(DataGardenSubModel):
    life_expectancy_at_birth: LifeExpectancyAtBirth = Field(
        default_factory=LifeExpectancyAtBirth, description=L.LIFE_EXPECTANCY_AT_BIRTH
    )

    remaining_life_expectancy: LifeExpectancyByAgeGender = Field(
        default_factory=LifeExpectancyByAgeGender, description=L.REMAINING_LIFE_EXPECTANCY
    )
