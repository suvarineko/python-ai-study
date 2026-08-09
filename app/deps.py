"""Зависимости FastAPI: собирают объекты, которые нужны роутам.

TODO (Шаг 4):
  - def get_ai() -> AIProvider: return StubProvider()   # позже меняем ТОЛЬКО эту строку
  - прокинуть ai в ChatService: get_chat_service(db=Depends(get_db), ai=Depends(get_ai))
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.service import ChatService


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:

    return ChatService(db)
