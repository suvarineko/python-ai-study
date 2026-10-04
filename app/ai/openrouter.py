"""Провайдер поверх OpenRouter — OpenAI-совместимый /chat/completions.

Формат запроса и ответа: https://openrouter.ai/docs/api-reference/chat-completion

Клиент httpx создаётся на каждый вызов: один HTTP-запрос на одно сообщение,
накладные расходы на соединение теряются на фоне задержки самой модели.
"""

import json

import httpx

from app.ai.base import AIProvider, AIProviderError
from app.config import settings
from app.models import Message


class OpenRouterProvider(AIProvider):
    """Отправляет историю диалога в OpenRouter и возвращает текст ответа."""

    def __init__(self, client: httpx.AsyncClient | None = None):
        # client подменяют тесты, чтобы не ходить в сеть. В бою — всегда None.
        self._client = client

    def _payload(self, messages: list[Message]) -> dict:
        """Историю переводим в формат OpenAI, системный промпт ставим первым.

        Промпт — настройка из .env, поэтому подставляется здесь на каждый запрос
        и в БД не хранится: иначе правка .env не доехала бы до старых диалогов.
        """
        chat = [{"role": m.role, "content": m.content} for m in messages]
        if settings.openrouter_system_prompt:
            chat.insert(0, {"role": "system", "content": settings.openrouter_system_prompt})
        return {"model": settings.openrouter_model, "messages": chat}

    async def complete(self, messages: list[Message]) -> str:
        url = f"{settings.openrouter_base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openrouter_api_key}"}
        payload = self._payload(messages)

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

    async def stream(self, messages: list[Message]):
        """То же самое, но ответ отдаётся кусками, как только они приходят.

        OpenRouter присылает кадры `data: {...}` с обрывком текста в
        choices[0].delta.content и закрывает поток кадром `data: [DONE]`.
        """
        url = f"{settings.openrouter_base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openrouter_api_key}"}
        payload = self._payload(messages) | {"stream": True}

        client = self._client or httpx.AsyncClient(timeout=settings.openrouter_timeout)
        try:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != httpx.codes.OK:
                    text = (await response.aread()).decode(errors="replace")
                    raise AIProviderError(f"OpenRouter ответил {response.status_code}: {text[:300]}")

                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue  # пустые строки и keepalive `: OPENROUTER PROCESSING`
                    data = line[len("data: "):]
                    if data == "[DONE]":
                        return
                    delta = json.loads(data)["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
        except httpx.HTTPError as exc:
            raise AIProviderError(f"OpenRouter недоступен: {exc}") from exc
        finally:
            if self._client is None:  # свой клиент закрываем, тестовый — нет
                await client.aclose()
