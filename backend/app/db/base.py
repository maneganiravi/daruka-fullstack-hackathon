# Import all models here for Alembic and Base.metadata.create_all
from app.db.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.project import Project  # noqa
from app.models.site import Site  # noqa
from app.models.analytics import SiteAnalytics  # noqa
