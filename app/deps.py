"""

TODO:
  - def get_ai() -> AIProvider: return StubProvider()   # позже меняем ТОЛЬКО эту строку
  - def get_chat_service(db=Depends(get_db), ai=Depends(get_ai)) -> ChatService

"""

# def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
#     return ChatService(db)
