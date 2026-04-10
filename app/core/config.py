from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "遗境焕活"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./heritage_revive.db"


settings = Settings()
