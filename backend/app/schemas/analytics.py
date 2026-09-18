from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SiteAnalyticsBase(BaseModel):
    record_date: date = Field(default_factory=date.today)
    carbon_stored_tons: float = Field(..., ge=0.0)
    carbon_rate_per_year: Optional[float] = 0.0
    biodiversity_score: float = Field(..., ge=0.0, le=100.0)
    canopy_cover_percentage: float = Field(..., ge=0.0, le=100.0)
    species_richness_count: int = Field(default=0, ge=0)


class SiteAnalyticsCreate(SiteAnalyticsBase):
    site_id: str


class SiteAnalyticsOut(SiteAnalyticsBase):
    id: str
    site_id: str
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TimeSeriesDataPoint(BaseModel):
    record_date: str
    carbon_stored_tons: float
    carbon_rate_per_year: float
    biodiversity_score: float
    canopy_cover_percentage: float
    species_richness_count: int


class SiteTimeSeriesResponse(BaseModel):
    site_id: str
    site_name: str
    area_hectares: float
    data: List[TimeSeriesDataPoint]


class DashboardMetrics(BaseModel):
    total_projects: int
    active_projects: int
    total_sites: int
    total_area_hectares: float
    total_carbon_stored_tons: float
    target_carbon_total_tons: float
    average_biodiversity_score: float
    total_species_recorded: int
