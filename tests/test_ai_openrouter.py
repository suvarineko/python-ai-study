"""Юнит-тесты OpenRouterProvider.

Сеть не трогаем: httpx.MockTransport перехватывает запрос и отдаёт заготовленный
ответ. Заодно проверяем, что именно мы отправляем наружу.
"""

import asyncio

import httpx
import pytest

from app.ai.base import AIProviderError
from app.ai.openrouter import OpenRouterProvider
from app.config import settings
from app.models import Message


@pytest.fixture(autouse=True)
def fake_settings(monkeypatch):
    """Тесты не должны зависеть от того, что лежит в .env."""
    monkeypatch.setattr(settings, "openrouter_api_key", "test-key")
    monkeypatch.setattr(settings, "openrouter_model", "test/model")
    monkeypatch.setattr(settings, "openrouter_base_url", "https://openrouter.ai/api/v1")


def call(handler, messages=None) -> str:
    """Прогоняет complete() поверх поддельного транспорта."""
    messages = messages if messages is not None else [Message(role="user", content="Привет")]

    async def main():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await OpenRouterProvider(client=client).complete(messages)

    return asyncio.run(main())


def test_complete_returns_model_reply():
    reply = call(lambda request: httpx.Response(
        200, json={"choices": [{"message": {"role": "assistant", "content": "Привет! Чем помочь?"}}]}
    ))

    assert reply == "Привет! Чем помочь?"


def test_request_carries_model_history_and_auth():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = httpx.Response(200, content=request.content).json()
        return httpx.Response(200, json={"choices": [{"message": {"content": "ок"}}]})

    call(handler, [
        Message(role="user", content="Первый вопрос"),
        Message(role="assistant", content="Первый ответ"),
        Message(role="user", content="Второй вопрос"),
    ])

    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["auth"] == "Bearer test-key"
    assert seen["body"]["model"] == "test/model"
    assert seen["body"]["messages"] == [
        {"role": "user", "content": "Первый вопрос"},
        {"role": "assistant", "content": "Первый ответ"},
        {"role": "user", "content": "Второй вопрос"},
    ]


def test_http_error_becomes_ai_provider_error():
    with pytest.raises(AIProviderError, match="429"):
        call(lambda request: httpx.Response(429, text="Rate limit exceeded"))
