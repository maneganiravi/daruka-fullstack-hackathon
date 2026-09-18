import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Site(Base):
    __tablename__ = "sites"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Stores GeoJSON geometry polygon as JSON string / PostGIS geometry representation
    geojson_geometry = Column(Text, nullable=False)

    area_hectares = Column(Float, default=0.0, nullable=False)
    soil_type = Column(String(100), default="Loam", nullable=True)
    elevation_meters = Column(Float, default=0.0, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project = relationship("Project", back_populates="sites")
    analytics = relationship("SiteAnalytics", back_populates="site", cascade="all, delete-orphan")

    @property
    def parsed_geometry(self):
        """Returns the geometry as Python dictionary."""
        try:
            return json.loads(self.geojson_geometry)
        except Exception:
            return None
