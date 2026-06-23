"""ORM-модели (Шаг 2).

TODO: две таблицы в связи один-ко-многим.
  - Conversation: id, title, created_at; messages = relationship(..., cascade="all, delete-orphan")
  - Message: id, conversation_id (ForeignKey), role, content, created_at; conversation = relationship(back_populates=...)

"""
