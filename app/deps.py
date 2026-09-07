"""Зависимости FastAPI: собирают объекты, которые нужны роутам.

Какой провайдер поднимется — решает AI_PROVIDER в .env, а не код роутов.
"""

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.base import AIProvider, AIProviderDev, AIProviderError
from app.ai.openrouter import OpenRouterProvider
from app.config import settings
from app.db import get_db
from app.service import ChatService


@lru_cache
def get_ai() -> AIProvider:
    """Провайдер живёт один на всё приложение — пересоздавать его на запрос незачем."""
    name = settings.ai_provider.lower()

    if name == "openrouter":
        return OpenRouterProvider()
    if name == "dev":
        return AIProviderDev()

    raise AIProviderError(f"Неизвестный AI_PROVIDER={settings.ai_provider!r}: ожидается 'dev' или 'openrouter'")


def get_chat_service(db: Session = Depends(get_db), ai_provider: AIProvider = Depends(get_ai)) -> ChatService:

    return ChatService(db, ai_provider)
