"""Точка входа FastAPI (Шаг 1, дополняется на Шаге 3).

TODO:
  - lifespan: на старте Base.metadata.create_all(engine)
  - app = FastAPI(title="ChatLab", lifespan=lifespan)
  - app.include_router(conversations_router)   # появится на Шаге 3
  - GET /healthz -> {"ok": True}
Запуск: python -m uvicorn app.main:app --reload   (из корня ChatLab)

"""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.ai.base import AIProviderError
from app.api.conversations import router as conversations_router
from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # На старте создаём таблицы, если их ещё нет.
    init_db()
    yield


app = FastAPI(title="ChatLab", lifespan=lifespan)

app.include_router(conversations_router)


@app.exception_handler(AIProviderError)
async def ai_provider_error_handler(request: Request, exc: AIProviderError):
    """Ловит ошибки конфига: get_ai() падает ещё до входа в тело роута."""
    return JSONResponse(status_code=status.HTTP_502_BAD_GATEWAY, content={"detail": str(exc)})


@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
  uvicorn.run(app, port=8906)
