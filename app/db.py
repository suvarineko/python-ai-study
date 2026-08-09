"""

TODO:
  + engine = create_engine(settings.database_url, connect_args=...)  # для sqlite check_same_thread=False
  + SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
  + class Base(DeclarativeBase): pass
  + def get_db(): открыть сессию на время запроса (yield) и закрыть после

"""

from app.config import Settings

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

settings = Settings()

# Для SQLite нужен check_same_thread=False, чтобы одну сессию можно было
# использовать внутри обработчиков FastAPI. Для других СУБД аргумент не нужен.
connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

def init_db() -> None:
    """Создаёт все таблицы, объявленные через Base, если их ещё нет.
    """
    from app import models  # noqa: F401  — регистрирует таблицы в metadata

    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI-зависимость: открывает сессию на время запроса и закрывает после."""
    with SessionLocal() as session:
        yield session
