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
    for chank in "Тест дев".split():
      yield chank

class AIProviderProd(AIProvider):
  async def complete(self, messages: list[Message]) -> str:
    return "Тест прод"
