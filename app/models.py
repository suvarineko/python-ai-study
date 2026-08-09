"""ORM-модели (Шаг 2).

TODO: две таблицы в связи один-ко-многим.
  + Conversation: id, title, created_at; messages = relationship(..., cascade="all, delete-orphan")
  + Message: id, conversation_id (ForeignKey), role, content, created_at; conversation = relationship(back_populates=...)

"""

from datetime import datetime, timezone
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

def _now() -> datetime:
    return datetime.now(timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=_now)
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.id",
    )

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    role: Mapped[str]  # "user" | "assistant"
    content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=_now)
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
