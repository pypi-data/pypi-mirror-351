from datagarden_models.models.weather import WeatherV1, WeatherV1Keys

from .demographics import DemographicsV1, DemographicsV1Keys
from .economics import EconomicsV1, EconomicsV1Keys
from .health import HealthV1, HealthV1Keys
from .household import HouseholdV1, HouseholdV1Keys
from .social_environment import SocialEnvironmentV1, SocialEnvironmentV1Keys


class DatagardenModels:
    DEMOGRAPHICS = DemographicsV1
    ECONOMICS = EconomicsV1
    HEALTH = HealthV1
    SOCIAL_ENVIRONMENT = SocialEnvironmentV1
    WEATHER = WeatherV1
    HOUSEHOLD = HouseholdV1


class DatagardenModelKeys:
    DEMOGRAPHICS = DemographicsV1Keys
    ECONOMICS = EconomicsV1Keys
    HEALTH = HealthV1Keys
    SOCIAL_ENVIRONMENT = SocialEnvironmentV1Keys
    WEATHER = WeatherV1Keys
    HOUSEHOLD = HouseholdV1Keys


__all__ = ["DatagardenModels", "DatagardenModelKeys"]
