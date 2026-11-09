import urllib.parse
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_DIRECT: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "*"

    @field_validator("DATABASE_URL", "DATABASE_URL_DIRECT", mode="before")
    @classmethod
    def normalize_db_url(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            return v
        parsed = urllib.parse.urlsplit(v.strip())
        scheme = "postgresql+asyncpg"
        query_params = urllib.parse.parse_qs(parsed.query)
        clean_params: dict[str, str] = {}
        needs_ssl = (
            "ssl" in query_params or
            "sslmode" in query_params or
            "neon.tech" in parsed.netloc or
            "aws." in parsed.netloc
        )
        if needs_ssl:
            clean_params["ssl"] = "require"
        clean_query = urllib.parse.urlencode(clean_params)
        return urllib.parse.urlunsplit((scheme, parsed.netloc, parsed.path, clean_query, parsed.fragment))

    model_config = SettingsConfigDict(
        env_file=(str(BASE_DIR / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
