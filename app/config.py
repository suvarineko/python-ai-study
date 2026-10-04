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
  openrouter_system_prompt: str = ""

  # --- Телеграм-бот (app/bot.py) ---
  telegram_bot_token: str = ""
  # Кому бот отвечает: id через запятую. Пусто — отвечает всем.
  telegram_allowed_users: str = ""
  # Адрес нашего же API, к которому бот ходит как обычный клиент.
  api_base_url: str = "http://127.0.0.1:8906"

settings = Settings()
