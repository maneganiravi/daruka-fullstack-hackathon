import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class SiteAnalytics(Base):
    __tablename__ = "site_analytics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    site_id = Column(String(36), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True)

    record_date = Column(Date, default=date.today, nullable=False, index=True)
    carbon_stored_tons = Column(Float, default=0.0, nullable=False)
    carbon_rate_per_year = Column(Float, default=0.0, nullable=False)  # tons/yr
    biodiversity_score = Column(Float, default=0.0, nullable=False)    # 0.0 - 100.0
    canopy_cover_percentage = Column(Float, default=0.0, nullable=False)  # 0.0 - 100.0
    species_richness_count = Column(Integer, default=0, nullable=False)

    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    site = relationship("Site", back_populates="analytics")
