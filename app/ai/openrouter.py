"""Провайдер поверх OpenRouter — OpenAI-совместимый /chat/completions.

Формат запроса и ответа: https://openrouter.ai/docs/api-reference/chat-completion

Клиент httpx создаётся на каждый вызов: один HTTP-запрос на одно сообщение,
накладные расходы на соединение теряются на фоне задержки самой модели.
"""

import httpx

from app.ai.base import AIProvider, AIProviderError
from app.config import settings
from app.models import Message


class OpenRouterProvider(AIProvider):
    """Отправляет историю диалога в OpenRouter и возвращает текст ответа."""

    def __init__(self, client: httpx.AsyncClient | None = None):
        # client подменяют тесты, чтобы не ходить в сеть. В бою — всегда None.
        self._client = client

    async def complete(self, messages: list[Message]) -> str:
        url = f"{settings.openrouter_base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openrouter_api_key}"}
        payload = {
            "model": settings.openrouter_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }

        try:
            if self._client is not None:
                response = await self._client.post(url, json=payload, headers=headers)
            else:
                async with httpx.AsyncClient(timeout=settings.openrouter_timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise AIProviderError(f"OpenRouter недоступен: {exc}") from exc

        # Пустой ключ ловится здесь же: OpenRouter вернёт 401 с внятным текстом.
        if response.status_code != httpx.codes.OK:
            raise AIProviderError(f"OpenRouter ответил {response.status_code}: {response.text[:300]}")

        return response.json()["choices"][0]["message"]["content"]
