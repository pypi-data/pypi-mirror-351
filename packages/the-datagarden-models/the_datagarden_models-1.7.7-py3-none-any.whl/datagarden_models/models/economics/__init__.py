from pydantic import Field

from ..base import DataGardenModel, DataGardenModelLegends
from .base_economics import EconomicBaseKeys, EconomicMetaDataKeys, EconomicsMetaData
from .gdp import GDP, GDPV1Keys
from .inflation import Inflation, InflationV1Keys
from .investment import Investment, InvestmentKeys
from .labor_market import LaborMarketStatus, LaborMarketStatusKeys
from .productivity import Productivity, ProductivityKeys
from .public_spending import PublicSpendingV1, PublicSpendingV1Keys
from .trade import TradeV1, TradeV1Keys


class EconomicsV1Keys(
    GDPV1Keys,
    EconomicBaseKeys,
    InflationV1Keys,
    TradeV1Keys,
    PublicSpendingV1Keys,
    EconomicMetaDataKeys,
    LaborMarketStatusKeys,
    ProductivityKeys,
    InvestmentKeys,
):
    GDP = "gdp"
    ECONOMICS_METADATA = "economics_metadata"
    DATAGARDEN_MODEL_NAME = "Economics"
    INFLATION = "inflation"
    TRADE = "trade"
    PUBLIC_SPENDING = "public_spending"
    LABOR_MARKET_STATUS = "labor_market_status"
    PRODUCTIVITY = "productivity"
    INVESTMENT = "investment"


class EconomicsV1Legends(DataGardenModelLegends):
    GDP = "Gross Domestic Product"
    INFLATION = "Inflation numbers"
    TRADE = "Trade statistics"
    PUBLIC_SPENDING = "Public spending"
    LABOR_MARKET_STATUS = "Labor market status"
    PRODUCTIVITY = "Productivity statistics"
    INVESTMENT = "Investment statistics"
    ECONOMICS_METADATA = "Metadata about currency, units and reference year used for the data."
    MODEL_LEGEND = "Economic data for a region. "


L = EconomicsV1Legends


class EconomicsV1(DataGardenModel):
    datagarden_model_version: str = Field("v1.0", frozen=True, description=L.DATAGARDEN_MODEL_VERSION)
    economics_metadata: EconomicsMetaData = Field(default_factory=EconomicsMetaData, description=L.METADATA)
    gdp: GDP = Field(default_factory=GDP, description=L.GDP)
    inflation: Inflation = Field(default_factory=Inflation, description=L.INFLATION)
    trade: TradeV1 = Field(default_factory=TradeV1, description=L.TRADE)
    public_spending: PublicSpendingV1 = Field(default_factory=PublicSpendingV1, description=L.PUBLIC_SPENDING)
    labor_market_status: LaborMarketStatus = Field(
        default_factory=LaborMarketStatus, description=L.LABOR_MARKET_STATUS
    )
    productivity: Productivity = Field(default_factory=Productivity, description=L.PRODUCTIVITY)
    investment: Investment = Field(default_factory=Investment, description=L.INVESTMENT)

    class Meta(DataGardenModel.Meta):
        fields_to_include_in_data_dump: list[str] = DataGardenModel.Meta.fields_to_include_in_data_dump + [
            "economics_metadata"
        ]
