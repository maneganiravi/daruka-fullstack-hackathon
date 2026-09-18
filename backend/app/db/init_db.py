import json
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.session import engine
from app.models.analytics import SiteAnalytics
from app.models.project import Project
from app.models.site import Site
from app.models.user import User
from app.utils.geo import calculate_polygon_area_hectares


def init_db(db: Session) -> None:
    """Create all tables and seed sample hackathon data if empty."""
    Base.metadata.create_all(bind=engine)

    # 1. Create or get Admin Superuser
    admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
    if not admin:
        admin = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="Darukaa Admin",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    # 2. Create standard demo user
    demo_user = db.query(User).filter(User.email == "ecologist@darukaa.earth").first()
    if not demo_user:
        demo_user = User(
            email="ecologist@darukaa.earth",
            hashed_password=get_password_hash("Ecologist2026!"),
            full_name="Dr. Maya Sharma",
            role="user",
            is_active=True,
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    # 3. Seed Sample Projects if none exist
    if db.query(Project).count() == 0:
        # Project 1: Western Ghats Rainforest Canopy Restoration
        p1 = Project(
            name="Western Ghats Rainforest Canopy Restoration",
            description=(
                "Restoring contiguous wildlife corridors and native canopy cover "
                "across degraded tea plantation buffers in Kerala & Karnataka."
            ),
            client_name="Global Biodiversity Trust",
            status="active",
            target_carbon_sequestration_tons=25000.0,
            user_id=admin.id,
        )
        db.add(p1)

        # Project 2: Sundarbans Mangrove Blue Carbon Initiative
        p2 = Project(
            name="Sundarbans Mangrove Blue Carbon Initiative",
            description=(
                "High-density mangrove afforestation along delta shorelines to "
                "prevent coastal erosion and maximize blue carbon soil capture."
            ),
            client_name="Coastal Resilience Fund",
            status="active",
            target_carbon_sequestration_tons=40000.0,
            user_id=demo_user.id,
        )
        db.add(p2)

        # Project 3: Aravalli Scrub Forest & Aquifer Recharge
        p3 = Project(
            name="Aravalli Scrub Forest & Aquifer Recharge",
            description=(
                "Indigenous native thorn forest plantation aimed at arresting "
                "desertification and restoring groundwater recharge zones."
            ),
            client_name="Delhi-NCR Eco Regeneration",
            status="planning",
            target_carbon_sequestration_tons=12000.0,
            user_id=admin.id,
        )
        db.add(p3)
        db.commit()
        db.refresh(p1)
        db.refresh(p2)
        db.refresh(p3)

        # 4. Seed Geographical Sites with GeoJSON Polygons
        poly1 = {
            "type": "Polygon",
            "coordinates": [
                [
                    [76.0850, 11.6850],
                    [76.1250, 11.6950],
                    [76.1350, 11.6600],
                    [76.0900, 11.6450],
                    [76.0850, 11.6850],
                ]
            ],
        }
        s1 = Site(
            project_id=p1.id,
            name="Wayanad Wildlife Corridor Sector 4",
            description="High elevation moist deciduous forest patch connecting Brahmagiri and Nagarhole reserves.",
            geojson_geometry=json.dumps(poly1),
            area_hectares=calculate_polygon_area_hectares(poly1),
            soil_type="Laterite High-Humus",
            elevation_meters=920.0,
        )
        db.add(s1)

        poly2 = {
            "type": "Polygon",
            "coordinates": [
                [
                    [76.4200, 11.1200],
                    [76.4600, 11.1350],
                    [76.4750, 11.0950],
                    [76.4300, 11.0850],
                    [76.4200, 11.1200],
                ]
            ],
        }
        s2 = Site(
            project_id=p1.id,
            name="Silent Valley Buffer Restoration Zone",
            description="Evergreen canopy restoration plot focusing on endemic Cullenia exarillata trees.",
            geojson_geometry=json.dumps(poly2),
            area_hectares=calculate_polygon_area_hectares(poly2),
            soil_type="Red Acidic Loam",
            elevation_meters=1150.0,
        )
        db.add(s2)

        poly3 = {
            "type": "Polygon",
            "coordinates": [
                [
                    [88.8200, 21.9200],
                    [88.8650, 21.9350],
                    [88.8750, 21.8900],
                    [88.8300, 21.8800],
                    [88.8200, 21.9200],
                ]
            ],
        }
        s3 = Site(
            project_id=p2.id,
            name="Gosaba Tidal Mangrove Plot 1",
            description="Pneumatophore density zone dominated by Rhizophora mucronata and Avicennia marina.",
            geojson_geometry=json.dumps(poly3),
            area_hectares=calculate_polygon_area_hectares(poly3),
            soil_type="Saline Alluvial Silt",
            elevation_meters=3.5,
        )
        db.add(s3)
        db.commit()
        db.refresh(s1)
        db.refresh(s2)
        db.refresh(s3)

        # 5. Seed Time Series Environmental Analytics Data for Chart.js
        today = date.today()

        for i in range(12, -1, -1):
            d = today - timedelta(days=i * 30)
            factor = (12 - i) / 12.0
            carbon_val = round(1200.0 + (factor * 3400.0), 2)
            bio_val = round(52.0 + (factor * 36.0), 1)
            canopy_val = round(30.0 + (factor * 48.0), 1)
            rate_val = round(180.0 + (factor * 95.0), 1)
            species_cnt = int(24 + (factor * 42))

            stat = SiteAnalytics(
                site_id=s1.id,
                record_date=d,
                carbon_stored_tons=carbon_val,
                carbon_rate_per_year=rate_val,
                biodiversity_score=min(bio_val, 98.0),
                canopy_cover_percentage=min(canopy_val, 92.0),
                species_richness_count=species_cnt,
            )
            db.add(stat)

        for i in range(10, -1, -1):
            d = today - timedelta(days=i * 30)
            factor = (10 - i) / 10.0
            carbon_val = round(850.0 + (factor * 2600.0), 2)
            bio_val = round(58.0 + (factor * 31.0), 1)
            canopy_val = round(35.0 + (factor * 42.0), 1)
            rate_val = round(140.0 + (factor * 80.0), 1)
            species_cnt = int(30 + (factor * 35))

            stat = SiteAnalytics(
                site_id=s2.id,
                record_date=d,
                carbon_stored_tons=carbon_val,
                carbon_rate_per_year=rate_val,
                biodiversity_score=min(bio_val, 94.0),
                canopy_cover_percentage=min(canopy_val, 88.0),
                species_richness_count=species_cnt,
            )
            db.add(stat)

        for i in range(8, -1, -1):
            d = today - timedelta(days=i * 30)
            factor = (8 - i) / 8.0
            carbon_val = round(1500.0 + (factor * 4100.0), 2)
            bio_val = round(64.0 + (factor * 28.0), 1)
            canopy_val = round(45.0 + (factor * 38.0), 1)
            rate_val = round(220.0 + (factor * 110.0), 1)
            species_cnt = int(18 + (factor * 26))

            stat = SiteAnalytics(
                site_id=s3.id,
                record_date=d,
                carbon_stored_tons=carbon_val,
                carbon_rate_per_year=rate_val,
                biodiversity_score=min(bio_val, 95.0),
                canopy_cover_percentage=min(canopy_val, 90.0),
                species_richness_count=species_cnt,
            )
            db.add(stat)

        db.commit()
