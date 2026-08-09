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
from fastapi import FastAPI

from app.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # На старте создаём таблицы, если их ещё нет.
    init_db()
    yield


app = FastAPI(title="ChatLab", lifespan=lifespan)



@app.get("/healthz")
def healthz():
    return {"ok": True}


if __name__ == "__main__":
  uvicorn.run(app, port=8906)
