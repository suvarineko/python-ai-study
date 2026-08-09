"""
TODO:
  + class ConversationNotFound(Exception)
  - class ChatService(db, ai) с методами:
    + create_conversation(title), list_conversations(), get_conversation(id),
    + delete_conversation(id), list_messages(id),
    - async send_message(id, content):  сохранить user -> позвать ai.complete(history) -> сохранить assistant
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Conversation, Message


class ConversationNotFound(Exception):
    """Диалог с указанным id не найден."""

    def __init__(self, conversation_id: int):
        self.conversation_id = conversation_id
        super().__init__(f"Conversation {conversation_id} not found")


class ChatService:
    """Инкапсулирует операции с БД. Одна сессия — на время запроса."""

    def __init__(self, db: Session):
        self.db = db

    # --- Conversations ---

    def create_conversation(self, title: str) -> Conversation:
        """Создаёт новый диалог и возвращает его (с проставленным id)."""
        conversation = Conversation(title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def list_conversations(self) -> list[Conversation]:
        """Возвращает все диалоги (новые сверху)."""
        stmt = select(Conversation).order_by(Conversation.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_conversation(self, conversation_id: int) -> Conversation:
        """Возвращает диалог по id или бросает ConversationNotFound."""
        conversation = self.db.get(entity=Conversation, ident=conversation_id)
        if conversation is None:
            raise ConversationNotFound(conversation_id)
        return conversation

    def delete_conversation(self, conversation_id: int) -> None:
        """Удаляет диалог вместе со всеми его сообщениями.

        Каскад настроен на связи (cascade="all, delete-orphan"), поэтому
        удаление объекта через ORM снимает и связанные Message.
        """
        conversation = self.get_conversation(conversation_id)
        self.db.delete(conversation)
        self.db.commit()

    # --- Messages ---

    def list_messages(self, conversation_id: int) -> list[Message]:
        """Возвращает сообщения диалога в порядке добавления."""
        # conversation = self.get_conversation(conversation_id)
        query = select(Message.content, Message.role).where(Message.conversation_id == conversation_id).order_by("id")

        return self.db.scalars(query).all()

    def add_message(self, conversation_id: int, role: str, content: str) -> Message:
        """Добавляет сообщение в диалог и возвращает его.

        Проверяет существование диалога — иначе ConversationNotFound.
        """
        self.get_conversation(conversation_id)  # проверка существования
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
