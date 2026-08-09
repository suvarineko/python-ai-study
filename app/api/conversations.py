"""HTTP-слой: роуты. Знает про коды/HTTPException, НЕ знает про SQL.

  POST   ""                  -> создать (201, ConversationOut)
  GET    ""                  -> список (list[ConversationOut])
  GET    "/{conv_id}"        -> детально (ConversationDetail, 404)
  DELETE "/{conv_id}"        -> удалить (204, 404)
  GET    "/{conv_id}/messages" -> история (list[MessageOut], 404)
  POST   "/{conv_id}/messages" -> добавить (201, MessageOut, 404)  # async!
  ConversationNotFound -> raise HTTPException(404)
Эталон — docs/TEACHING_GUIDE.md, Шаги 3–5.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_chat_service
from app.schemas import (
    ConversationCreate,
    ConversationDetail,
    ConversationOut,
    MessageCreate,
    MessageOut,
)
from app.service import ChatService, ConversationNotFound

router = APIRouter(prefix="/conversations", tags=["conversations"])

def _not_found(exc: ConversationNotFound) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreate,
    service: ChatService = Depends(get_chat_service),
):

    return service.create_conversation(payload.title)

@router.get("", response_model=list[ConversationOut])
def list_conversations(
    service: ChatService = Depends(get_chat_service),
):

    return service.list_conversations()

@router.get("/{conv_id}", response_model=ConversationDetail)
def get_conversation(
    conv_id: int,
    service: ChatService = Depends(get_chat_service),
):

    try:
        return service.get_conversation(conv_id)
    except ConversationNotFound as exc:
        raise _not_found(exc) from exc

@router.delete("/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conv_id: int,
    service: ChatService = Depends(get_chat_service),
):

    try:
        service.delete_conversation(conv_id)
    except ConversationNotFound as exc:
        raise _not_found(exc) from exc

@router.get("/{conv_id}/messages", response_model=list[MessageOut])
def list_messages(
    conv_id: int,
    service: ChatService = Depends(get_chat_service),
):

    try:
        return service.list_messages(conv_id)
    except ConversationNotFound as exc:
        raise _not_found(exc) from exc

@router.post(
    "/{conv_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
def create_message(
    conv_id: int,
    payload: MessageCreate,
    service: ChatService = Depends(get_chat_service),
):

    try:
        return service.add_message(conv_id, role="user", content=payload.content)
    except ConversationNotFound as exc:
        raise _not_found(exc) from exc
