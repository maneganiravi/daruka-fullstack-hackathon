from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class GeoJSONGeometry(BaseModel):
    type: Literal["Polygon", "MultiPolygon"]
    coordinates: List[Any]


class SiteBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    soil_type: Optional[str] = "Loam"
    elevation_meters: Optional[float] = 0.0


class SiteCreate(SiteBase):
    project_id: str
    geometry: Union[GeoJSONGeometry, Dict[str, Any]]
    area_hectares: Optional[float] = None  # If not provided, computed from polygon coordinates


class SiteUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    geometry: Optional[Union[GeoJSONGeometry, Dict[str, Any]]] = None
    soil_type: Optional[str] = None
    elevation_meters: Optional[float] = None
    area_hectares: Optional[float] = None


class SiteOut(SiteBase):
    id: str
    project_id: str
    geometry: Dict[str, Any]
    area_hectares: float
    created_at: datetime
    updated_at: datetime
    project_name: Optional[str] = None
    latest_carbon_stored: Optional[float] = 0.0
    latest_biodiversity_score: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)


# GeoJSON standard schemas for direct Mapbox consumption
class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    id: str
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: List[GeoJSONFeature]
