"""Зависимости FastAPI: собирают объекты, которые нужны роутам.

TODO (Шаг 4):
  - def get_ai() -> AIProvider: return StubProvider()   # позже меняем ТОЛЬКО эту строку
  - прокинуть ai в ChatService: get_chat_service(db=Depends(get_db), ai=Depends(get_ai))
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.service import ChatService
from app.ai.base import AIProvider, AIProviderDev, AIProviderProd

def get_ai() -> AIProvider:
    return AIProviderDev()

def get_chat_service(db: Session = Depends(get_db), ai_provider=Depends(get_ai)) -> ChatService:

    return ChatService(db, ai_provider)
