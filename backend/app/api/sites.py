import json
from datetime import date
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.project import Project
from app.models.site import Site
from app.models.analytics import SiteAnalytics
from app.models.user import User
from app.schemas.site import (
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    SiteCreate,
    SiteOut,
    SiteUpdate,
)
from app.utils.geo import calculate_polygon_area_hectares

router = APIRouter(prefix="/sites", tags=["Sites & PostGIS Polygons"])


@router.get("/geojson", response_model=GeoJSONFeatureCollection)
def get_sites_geojson(
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve sites formatted directly as a GeoJSON FeatureCollection for Mapbox GL JS layers.
    """
    query = db.query(Site)
    if project_id:
        query = query.filter(Site.project_id == project_id)

    sites = query.all()
    features = []

    for site in sites:
        geom = site.parsed_geometry
        if not geom:
            continue

        project = db.query(Project).filter(Project.id == site.project_id).first()
        latest_stat = (
            db.query(SiteAnalytics)
            .filter(SiteAnalytics.site_id == site.id)
            .order_by(SiteAnalytics.record_date.desc())
            .first()
        )

        features.append(
            GeoJSONFeature(
                id=site.id,
                geometry=geom,
                properties={
                    "site_id": site.id,
                    "name": site.name,
                    "description": site.description or "",
                    "project_id": site.project_id,
                    "project_name": project.name if project else "Unknown Project",
                    "area_hectares": site.area_hectares,
                    "soil_type": site.soil_type or "Loam",
                    "elevation_meters": site.elevation_meters or 0,
                    "carbon_stored_tons": latest_stat.carbon_stored_tons if latest_stat else 0.0,
                    "biodiversity_score": latest_stat.biodiversity_score if latest_stat else 0.0,
                    "canopy_cover_percentage": latest_stat.canopy_cover_percentage if latest_stat else 0.0,
                    "created_at": site.created_at.isoformat(),
                },
            )
        )

    return GeoJSONFeatureCollection(features=features)


@router.get("", response_model=List[SiteOut])
def list_sites(
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    List all sites as standard JSON array.
    """
    query = db.query(Site)
    if project_id:
        query = query.filter(Site.project_id == project_id)

    sites = query.order_by(Site.created_at.desc()).all()
    result = []

    for s in sites:
        project = db.query(Project).filter(Project.id == s.project_id).first()
        latest_stat = (
            db.query(SiteAnalytics)
            .filter(SiteAnalytics.site_id == s.id)
            .order_by(SiteAnalytics.record_date.desc())
            .first()
        )
        result.append(
            SiteOut(
                id=s.id,
                project_id=s.project_id,
                name=s.name,
                description=s.description,
                geometry=s.parsed_geometry or {},
                area_hectares=s.area_hectares,
                soil_type=s.soil_type,
                elevation_meters=s.elevation_meters,
                created_at=s.created_at,
                updated_at=s.updated_at,
                project_name=project.name if project else None,
                latest_carbon_stored=latest_stat.carbon_stored_tons if latest_stat else 0.0,
                latest_biodiversity_score=latest_stat.biodiversity_score if latest_stat else 0.0,
            )
        )
    return result


@router.post("", response_model=SiteOut, status_code=status.HTTP_201_CREATED)
def create_site(
    site_in: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new site polygon attached to a project. Computes area automatically.
    """
    project = db.query(Project).filter(Project.id == site_in.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Referenced project does not exist"
        )

    # Parse and validate geometry
    if hasattr(site_in.geometry, "model_dump"):
        geom_dict = site_in.geometry.model_dump()
    elif isinstance(site_in.geometry, dict):
        geom_dict = site_in.geometry
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid GeoJSON geometry"
        )

    # Calculate area in hectares
    computed_area = site_in.area_hectares
    if not computed_area or computed_area <= 0:
        computed_area = calculate_polygon_area_hectares(geom_dict)

    site = Site(
        project_id=site_in.project_id,
        name=site_in.name,
        description=site_in.description,
        geojson_geometry=json.dumps(geom_dict),
        area_hectares=computed_area,
        soil_type=site_in.soil_type or "Loam",
        elevation_meters=site_in.elevation_meters or 0.0,
    )
    db.add(site)
    db.commit()
    db.refresh(site)

    # Initialize baseline analytics entry for this site
    initial_carbon = round(site.area_hectares * 12.5, 2)  # baseline estimate ~12.5 t/ha
    initial_analytics = SiteAnalytics(
        site_id=site.id,
        record_date=date.today(),
        carbon_stored_tons=initial_carbon,
        carbon_rate_per_year=round(site.area_hectares * 2.8, 2),
        biodiversity_score=68.0,
        canopy_cover_percentage=42.0,
        species_richness_count=18,
    )
    db.add(initial_analytics)
    db.commit()

    return SiteOut(
        id=site.id,
        project_id=site.project_id,
        name=site.name,
        description=site.description,
        geometry=site.parsed_geometry,
        area_hectares=site.area_hectares,
        soil_type=site.soil_type,
        elevation_meters=site.elevation_meters,
        created_at=site.created_at,
        updated_at=site.updated_at,
        project_name=project.name,
        latest_carbon_stored=initial_carbon,
        latest_biodiversity_score=68.0,
    )


@router.get("/{site_id}", response_model=SiteOut)
def get_site_details(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get detailed site information with geometry and latest metrics.
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    project = db.query(Project).filter(Project.id == site.project_id).first()
    latest_stat = (
        db.query(SiteAnalytics)
        .filter(SiteAnalytics.site_id == site.id)
        .order_by(SiteAnalytics.record_date.desc())
        .first()
    )

    return SiteOut(
        id=site.id,
        project_id=site.project_id,
        name=site.name,
        description=site.description,
        geometry=site.parsed_geometry,
        area_hectares=site.area_hectares,
        soil_type=site.soil_type,
        elevation_meters=site.elevation_meters,
        created_at=site.created_at,
        updated_at=site.updated_at,
        project_name=project.name if project else None,
        latest_carbon_stored=latest_stat.carbon_stored_tons if latest_stat else 0.0,
        latest_biodiversity_score=latest_stat.biodiversity_score if latest_stat else 0.0,
    )


@router.put("/{site_id}", response_model=SiteOut)
def update_site(
    site_id: str,
    site_in: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update site properties or redraw polygon geometry.
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    if site_in.name is not None:
        site.name = site_in.name
    if site_in.description is not None:
        site.description = site_in.description
    if site_in.soil_type is not None:
        site.soil_type = site_in.soil_type
    if site_in.elevation_meters is not None:
        site.elevation_meters = site_in.elevation_meters

    if site_in.geometry is not None:
        if hasattr(site_in.geometry, "model_dump"):
            geom_dict = site_in.geometry.model_dump()
        else:
            geom_dict = site_in.geometry
        site.geojson_geometry = json.dumps(geom_dict)
        site.area_hectares = calculate_polygon_area_hectares(geom_dict)
    elif site_in.area_hectares is not None:
        site.area_hectares = site_in.area_hectares

    db.commit()
    db.refresh(site)

    project = db.query(Project).filter(Project.id == site.project_id).first()
    latest_stat = (
        db.query(SiteAnalytics)
        .filter(SiteAnalytics.site_id == site.id)
        .order_by(SiteAnalytics.record_date.desc())
        .first()
    )

    return SiteOut(
        id=site.id,
        project_id=site.project_id,
        name=site.name,
        description=site.description,
        geometry=site.parsed_geometry,
        area_hectares=site.area_hectares,
        soil_type=site.soil_type,
        elevation_meters=site.elevation_meters,
        created_at=site.created_at,
        updated_at=site.updated_at,
        project_name=project.name if project else None,
        latest_carbon_stored=latest_stat.carbon_stored_tons if latest_stat else 0.0,
        latest_biodiversity_score=latest_stat.biodiversity_score if latest_stat else 0.0,
    )


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(
    site_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a site and its associated analytics history.
    """
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
        )

    db.delete(site)
    db.commit()
    return None
