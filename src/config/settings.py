import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # HDX HAPI Settings
    hdx_hapi_app_name: str = Field(default="NigeriaHIMS", alias="HDX_HAPI_APP_NAME")
    hdx_hapi_email: str = Field(default="user@example.com", alias="HDX_HAPI_EMAIL")
    hdx_hapi_base_url: str = Field(default="https://hapi.humdata.org", alias="HDX_HAPI_BASE_URL")
    
    # Database Settings
    supabase_db_url: str = Field(default="", alias="SUPABASE_DB_URL")
    database_url: str = Field(default="", alias="DATABASE_URL")
    
    # Pipeline Settings
    target_country_code: str = Field(default="NGA", alias="TARGET_COUNTRY_CODE")
    pipeline_log_level: str = Field(default="INFO", alias="PIPELINE_LOG_LEVEL")
    max_page_limit: int = Field(default=10000, alias="MAX_PAGE_LIMIT")
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_db_connection_url(self) -> str:
        url = self.database_url or self.supabase_db_url
        if not url:
            raise ValueError("No database URL configured. Please set DATABASE_URL or SUPABASE_DB_URL in .env")
        return url

settings = Settings()
