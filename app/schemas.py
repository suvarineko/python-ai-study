"""

TODO:
  Вход:  ConversationCreate{title}, MessageCreate{content}
  Выход: ConversationOut{id,title,created_at}, MessageOut{id,role,content,created_at}
         ConversationDetail(ConversationOut){messages: list[MessageOut]}
  У выходных схем: model_config = ConfigDict(from_attributes=True)
"""
