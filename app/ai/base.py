"""

TODO: class AIProvider(Protocol) с одним методом
      `async def complete(self, messages: list[Message]) -> str: ...`

"""
from collections.abc import AsyncIterator

from app.models import Message
from abc import ABC, abstractmethod

class AIProviderError(Exception):
    """Провайдер не смог выдать ответ: сеть, конфиг или ошибка апстрима."""

class AIProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[Message]) -> str:
        ...

    @abstractmethod
    async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
        ...

class AIProviderDev(AIProvider):
  async def complete(self, messages: list[Message]) -> str:
    return "Тест дев"

  async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
    # По 4 символа, а не по словам: split() съедает пробелы и склеить куски
    # обратно в "Тест дев" уже не получится.
    reply = "Тест дев"
    for start in range(0, len(reply), 4):
      yield reply[start:start + 4]

class AIProviderProd(AIProvider):
  async def complete(self, messages: list[Message]) -> str:
    return "Тест прод"

  async def stream(self, messages: list[Message]) -> AsyncIterator[str]:
    yield "Тест прод"
