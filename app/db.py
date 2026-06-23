"""

TODO:
  - engine = create_engine(settings.database_url, connect_args=...)  # для sqlite check_same_thread=False
  - SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
  - class Base(DeclarativeBase): pass
  - def get_db(): открыть сессию на время запроса (yield) и закрыть после

"""
