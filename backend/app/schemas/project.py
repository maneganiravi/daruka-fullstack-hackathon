from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: Optional[str] = "active"  # "planning", "active", "completed"
    target_carbon_sequestration_tons: Optional[float] = 0.0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: Optional[str] = None
    target_carbon_sequestration_tons: Optional[float] = None


class ProjectOut(ProjectBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    sites_count: Optional[int] = 0
    total_area_hectares: Optional[float] = 0.0
    total_carbon_stored_tons: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailOut(ProjectOut):
    sites: List[Any] = []
