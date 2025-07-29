from typing import Optional

from pydantic import Field

from datagarden_models.models.base import DataGardenSubModel


class ResearchAndDevelopmentInvestmentLegends:
    PUBLIC_INVESTMENT = "Public investment in research and development."
    COMPANY_EXPENDITURE = "Company expenditure on research and development."


RDI = ResearchAndDevelopmentInvestmentLegends


class ResearchAndDevelopmentInvestmentKeys:
    PUBLIC_INVESTMENT = "public_investment"
    COMPANY_EXPENDITURE = "company_expenditure"


class ResearchAndDevelopmentInvestment(DataGardenSubModel):
    public_investment: Optional[float] = Field(default=None, description=RDI.PUBLIC_INVESTMENT)
    company_expenditure: Optional[float] = Field(default=None, description=RDI.COMPANY_EXPENDITURE)


###########################################
########## Start Model defenition #########
###########################################
class InvestmentLegends:
    INWARD_FOREIGN_DIRECT_INVESTMENT = (
        "Value of foreign direct investments (FDI) into the country from non-resident companies."
    )
    OUTWARD_FOREIGN_DIRECT_INVESTMENT = (
        "Value of foreign direct investments (FDI) of resident companies in other countries."
    )

    RESEARCH_AND_DEVELOPMENT_INVESTMENT = "Value of research and development (R&D) investments."


IL = InvestmentLegends


class Investment(DataGardenSubModel):
    inward_foreign_direct_investment: Optional[float] = Field(
        default=None, description=IL.INWARD_FOREIGN_DIRECT_INVESTMENT
    )
    outward_foreign_direct_investment: Optional[float] = Field(
        default=None, description=IL.OUTWARD_FOREIGN_DIRECT_INVESTMENT
    )
    research_and_development_investment: Optional[ResearchAndDevelopmentInvestment] = Field(
        default=None, description=IL.RESEARCH_AND_DEVELOPMENT_INVESTMENT
    )


class InvestmentKeys(ResearchAndDevelopmentInvestmentKeys):
    INWARD_FOREIGN_DIRECT_INVESTMENT = "inward_foreign_direct_investment"
    OUTWARD_FOREIGN_DIRECT_INVESTMENT = "outward_foreign_direct_investment"
    RESEARCH_AND_DEVELOPMENT_INVESTMENT = "research_and_development_investment"
