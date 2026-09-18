import json
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Darukaa.Earth Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = "sqlite:///./daruka_dev.db"

    # JWT Authentication
    JWT_SECRET_KEY: str = "super_secret_darukaa_earth_jwt_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Superuser / Admin
    FIRST_SUPERUSER_EMAIL: str = "admin@darukaa.earth"
    FIRST_SUPERUSER_PASSWORD: str = "AdminPassword123!"

    # CORS (can be JSON array string or comma separated string or list)
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
    ]

    @property
    def parsed_cors_origins(self) -> List[str]:
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            if self.BACKEND_CORS_ORIGINS.startswith("[") and self.BACKEND_CORS_ORIGINS.endswith("]"):
                try:
                    return json.loads(self.BACKEND_CORS_ORIGINS)
                except Exception:
                    pass
            return [i.strip() for i in self.BACKEND_CORS_ORIGINS.split(",") if i.strip()]
        return list(self.BACKEND_CORS_ORIGINS)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
