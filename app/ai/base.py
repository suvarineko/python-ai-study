"""

TODO: class AIProvider(Protocol) с одним методом
      `async def complete(self, messages: list[Message]) -> str: ...`

"""
from app.models import Message
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[Message]) -> str:
        ...

class AIProviderDev(AIProvider):
  async def complete(self, messages: list[Message]) -> str:
    return "Тест дев"

class AIProviderProd(AIProvider):
  async def complete(self, messages: list[Message]) -> str:
    return "Тест прод"
