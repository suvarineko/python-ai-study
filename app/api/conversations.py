"""HTTP-слой: роуты. Знает про коды/HTTPException, НЕ знает про SQL (Шаги 3–5).

TODO: router = APIRouter(prefix="/conversations", tags=["conversations"])
  POST   ""                  -> создать (201, ConversationOut)
  GET    ""                  -> список (list[ConversationOut])
  GET    "/{conv_id}"        -> детально (ConversationDetail, 404)
  DELETE "/{conv_id}"        -> удалить (204, 404)
  GET    "/{conv_id}/messages" -> история (list[MessageOut], 404)
  POST   "/{conv_id}/messages" -> отправить (201, MessageOut, 404)  # async!
  ConversationNotFound -> raise HTTPException(404)
Эталон — docs/TEACHING_GUIDE.md, Шаги 3–5.
"""

# @router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
# def create_conversation(
#     payload: ConversationCreate,
#     service: ChatService = Depends(get_chat_service),
# ):
#     return service.create_conversation(payload.title)
