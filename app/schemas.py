"""

TODO:
  Вход:  ConversationCreate{title}, MessageCreate{content}
  Выход: ConversationOut{id,title,created_at}, MessageOut{id,role,content,created_at}
         ConversationDetail(ConversationOut){messages: list[MessageOut]}
  У выходных схем: model_config = ConfigDict(from_attributes=True)
"""

from pydantic import ConfigDict, BaseModel
from datetime import datetime

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
    content: str
    created_at: datetime
