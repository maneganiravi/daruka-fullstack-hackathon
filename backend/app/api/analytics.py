from datetime import date
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_active_user, get_db
from app.models.project import Project
from app.models.site import Site
from app.models.analytics import SiteAnalytics
from app.models.user import User
from app.schemas.analytics import (
    DashboardMetrics,
    SiteAnalyticsBase,
    SiteAnalyticsOut,
    SiteTimeSeriesResponse,
    TimeSeriesDataPoint,
)

router = APIRouter(prefix="/analytics", tags=["Analytics & Chart.js Metrics"])


@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get aggregate environmental metrics for high-level cards and admin dashboard.
    """
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "active").count()

    total_sites = db.query(Site).count()
    total_area = db.query(func.sum(Site.area_hectares)).scalar() or 0.0

    target_carbon = db.query(func.sum(Project.target_carbon_sequestration_tons)).scalar() or 0.0

    # Calculate latest carbon stored and biodiversity across all sites
    sites = db.query(Site).all()
    total_carbon = 0.0
    biodiversity_scores = []
    total_species = 0

    for site in sites:
        latest = (
            db.query(SiteAnalytics)
            .filter(SiteAnalytics.site_id == site.id)
            .order_by(SiteAnalytics.record_date.desc())
            .first()
        )
        if latest:
            total_carbon += latest.carbon_stored_tons
            biodiversity_scores.append(latest.biodiversity_score)
            total_species += latest.species_richness_count

    avg_biodiversity = (
        round(sum(biodiversity_scores) / len(biodiversity_scores), 1)
        if biodiversity_scores
        else 0.0
    )

    return DashboardMetrics(
        total_projects=total_projects,
        active_projects=active_projects,
        total_sites=total_sites,
        total_area_hectares=round(float(total_area), 2),
        total_carbon_stored_tons=round(float(total_carbon), 2),
        target_carbon_total_tons=round(float(target_carbon), 2),
        average_biodiversity_score=avg_biodiversity,
        total_species_recorded=total_species,
    )


@router.get("/sites/{site_id}", response_model=SiteTimeSeriesResponse)
def get_site_time_series(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get time-series carbon and biodiversity metrics for Chart.js interactive graphs.
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    records = (
        db.query(SiteAnalytics)
        .filter(SiteAnalytics.site_id == site_id)
        .order_by(SiteAnalytics.record_date.asc())
        .all()
    )

    data_points = [
        TimeSeriesDataPoint(
            record_date=r.record_date.strftime("%Y-%m-%d"),
            carbon_stored_tons=round(r.carbon_stored_tons, 2),
            carbon_rate_per_year=round(r.carbon_rate_per_year, 2),
            biodiversity_score=round(r.biodiversity_score, 1),
            canopy_cover_percentage=round(r.canopy_cover_percentage, 1),
            species_richness_count=r.species_richness_count,
        )
        for r in records
    ]

    return SiteTimeSeriesResponse(
        site_id=site.id,
        site_name=site.name,
        area_hectares=site.area_hectares,
        data=data_points,
    )


@router.post("/sites/{site_id}", response_model=SiteAnalyticsOut, status_code=status.HTTP_201_CREATED)
def add_site_metric_entry(
    site_id: str,
    metric_in: SiteAnalyticsBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Log a new environmental measurement data point for a site.
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    record = SiteAnalytics(
        site_id=site_id,
        record_date=metric_in.record_date or date.today(),
        carbon_stored_tons=metric_in.carbon_stored_tons,
        carbon_rate_per_year=metric_in.carbon_rate_per_year or 0.0,
        biodiversity_score=metric_in.biodiversity_score,
        canopy_cover_percentage=metric_in.canopy_cover_percentage,
        species_richness_count=metric_in.species_richness_count,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
