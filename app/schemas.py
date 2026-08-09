"""

  Вход:  ConversationCreate{title}, MessageCreate{content}
  Выход: ConversationOut{id,title,created_at}, MessageOut{id,role,content,created_at}
         ConversationDetail(ConversationOut){messages: list[MessageOut]}
  У выходных схем: model_config = ConfigDict(from_attributes=True)
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ConversationCreate(BaseModel):
    title: str

class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime

class MessageCreate(BaseModel):
    content: str

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime

class ConversationDetail(ConversationOut):
    messages: list[MessageOut]
