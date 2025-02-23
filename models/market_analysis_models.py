from pydantic import BaseModel, Field
from typing import List, Optional


class CompetitorInfo(BaseModel):
    name: str
    market_share: Optional[float] = Field(None, description="Market share percentage")
    market_cap: Optional[float] = Field(
        None, description="Market capitalization in USD"
    )
    key_products: Optional[List[str]] = Field(
        None, description="Main products/services"
    )
    strengths: Optional[List[str]] = Field(
        None, description="Key competitive advantages"
    )


class MarketMetrics(BaseModel):
    total_market_size: Optional[float] = Field(
        None, description="Total market size in USD"
    )
    growth_rate: Optional[float] = Field(
        None, description="Annual growth rate percentage"
    )
    market_maturity: Optional[str] = Field(
        None, description="Emerging/Growth/Mature/Declining"
    )
    key_trends: Optional[List[str]] = Field(None, description="Major market trends")


class MarketAnalysis(BaseModel):
    market_metrics: MarketMetrics
    competitors: List[CompetitorInfo]
    barriers_to_entry: Optional[List[str]] = None
    regulatory_factors: Optional[List[str]] = None
    technology_drivers: Optional[List[str]] = None
