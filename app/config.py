"""

TODO: класс Settings(BaseSettings) с полями database_url и ai_provider,
читающий .env. Внизу — единственный экземпляр `settings = Settings()`.

"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", extra="ignore")
  database_url: str = "sqlite:///./chatlab.db"
  ai_provider: str = "stub"

settings = Settings()
