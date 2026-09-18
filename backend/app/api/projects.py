from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.project import Project
from app.models.site import Site
from app.models.analytics import SiteAnalytics
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectDetailOut, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["Projects"])


def format_project_out(project: Project, db: Session) -> ProjectOut:
    """Helper to compute project summary stats."""
    sites = db.query(Site).filter(Site.project_id == project.id).all()
    sites_count = len(sites)
    total_area = sum(s.area_hectares for s in sites) if sites else 0.0

    # Calculate latest carbon stored across all sites in this project
    site_ids = [s.id for s in sites]
    total_carbon = 0.0
    if site_ids:
        for s_id in site_ids:
            latest_stat = (
                db.query(SiteAnalytics)
                .filter(SiteAnalytics.site_id == s_id)
                .order_by(SiteAnalytics.record_date.desc())
                .first()
            )
            if latest_stat:
                total_carbon += latest_stat.carbon_stored_tons

    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        client_name=project.client_name,
        status=project.status,
        target_carbon_sequestration_tons=project.target_carbon_sequestration_tons,
        user_id=project.user_id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        sites_count=sites_count,
        total_area_hectares=round(total_area, 2),
        total_carbon_stored_tons=round(total_carbon, 2),
    )


@router.get("", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> Any:
    """
    List all projects. Regular users see their own and public projects; admins see all.
    """
    query = db.query(Project)

    if status_filter:
        query = query.filter(Project.status == status_filter)

    if search:
        query = query.filter(
            Project.name.ilike(f"%{search}%") | Project.client_name.ilike(f"%{search}%")
        )

    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(limit).all()
    return [format_project_out(p, db) for p in projects]


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new project.
    """
    project = Project(
        name=project_in.name,
        description=project_in.description,
        client_name=project_in.client_name,
        status=project_in.status or "active",
        target_carbon_sequestration_tons=project_in.target_carbon_sequestration_tons or 0.0,
        user_id=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return format_project_out(project, db)


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project_details(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get detailed information about a single project including attached sites.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    summary = format_project_out(project, db)
    sites = db.query(Site).filter(Site.project_id == project.id).all()

    sites_list = []
    for s in sites:
        latest_stat = (
            db.query(SiteAnalytics)
            .filter(SiteAnalytics.site_id == s.id)
            .order_by(SiteAnalytics.record_date.desc())
            .first()
        )
        sites_list.append({
            "id": s.id,
            "project_id": s.project_id,
            "name": s.name,
            "description": s.description,
            "geometry": s.parsed_geometry,
            "area_hectares": s.area_hectares,
            "soil_type": s.soil_type,
            "elevation_meters": s.elevation_meters,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "latest_carbon_stored": latest_stat.carbon_stored_tons if latest_stat else 0.0,
            "latest_biodiversity_score": latest_stat.biodiversity_score if latest_stat else 0.0,
        })

    return {
        **summary.model_dump(),
        "sites": sites_list,
    }


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update project details.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this project",
        )

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return format_project_out(project, db)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete project.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    if current_user.role != "admin" and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this project",
        )

    db.delete(project)
    db.commit()
    return None
