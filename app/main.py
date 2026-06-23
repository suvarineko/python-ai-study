"""Точка входа FastAPI (Шаг 1, дополняется на Шаге 3).

TODO:
  - lifespan: на старте Base.metadata.create_all(engine)
  - app = FastAPI(title="ChatLab", lifespan=lifespan)
  - app.include_router(conversations_router)   # появится на Шаге 3
  - GET /healthz -> {"ok": True}
Запуск: python -m uvicorn app.main:app --reload   (из корня ChatLab)

"""
