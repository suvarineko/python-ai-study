"""

TODO: класс Settings(BaseSettings) с полями database_url и ai_provider,
читающий .env. Внизу — единственный экземпляр `settings = Settings()`.

"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", extra="ignore")
  database_url: str = "sqlite:///./chatlab.db"

  # Какой провайдер отдавать в get_ai(): "dev" | "openrouter"
  ai_provider: str = "dev"

  # --- OpenRouter (OpenAI-совместимый API) ---
  openrouter_api_key: str = ""
  openrouter_model: str = "qwen/qwen3.7-flash"
  openrouter_base_url: str = "https://openrouter.ai/api/v1"
  openrouter_timeout: float = 60.0

settings = Settings()
