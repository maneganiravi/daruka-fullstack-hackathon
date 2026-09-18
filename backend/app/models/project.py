import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    client_name = Column(String(255), nullable=True)
    status = Column(String(50), default="active", nullable=False)  # "planning", "active", "completed"
    target_carbon_sequestration_tons = Column(Float, default=0.0, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="projects")
    sites = relationship("Site", back_populates="project", cascade="all, delete-orphan")
