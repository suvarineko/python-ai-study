"""Юнит-тесты телеграм-бота.

Ни в Телеграм, ни в наш API не ходим: подменяем модуль httpx внутри app.bot
подделкой, которая записывает запросы и отдаёт заготовленные ответы.
"""

import pytest

from app import bot


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise AssertionError(f"неожиданный {self.status_code}")


@pytest.fixture()
def fake_httpx(monkeypatch):
    """Перехватывает httpx.post/get внутри app.bot."""
    sent = []
    replies = {}

    def post(url, json=None, timeout=None):
        sent.append(("POST", url, json))
        # Сверяем по концу URL: ".../conversations/5/messages" содержит и
        # "/conversations", так что проверка подстрокой дала бы не тот ответ.
        for key, response in replies.items():
            if url.endswith(key):
                return response
        return FakeResponse()

    def get(url, params=None, timeout=None):
        sent.append(("GET", url, params))
        return FakeResponse(payload={"result": []})

    monkeypatch.setattr(bot.httpx, "post", post)
    monkeypatch.setattr(bot.httpx, "get", get)
    monkeypatch.setattr(bot, "chats", {})  # у каждого теста свой пустой словарь
    return sent, replies


def texts_sent_to_telegram(sent) -> list[str]:
    return [body["text"] for method, url, body in sent if "sendMessage" in url]


def test_start_greets_and_forgets_old_conversation(fake_httpx):
    sent, _ = fake_httpx
    bot.chats[42] = 7  # как будто диалог уже был

    bot.handle_message({"chat": {"id": 42}, "text": "/start"})

    assert 42 not in bot.chats
    assert texts_sent_to_telegram(sent) == ["Привет! Напишите вопрос — передам модели."]


def test_text_creates_conversation_once_and_relays_reply(fake_httpx):
    sent, replies = fake_httpx
    replies["/conversations"] = FakeResponse(201, {"id": 5})
    replies["/messages"] = FakeResponse(201, {"content": "Лиссабон"})

    bot.handle_message({"chat": {"id": 42}, "text": "Столица Португалии?"})
    bot.handle_message({"chat": {"id": 42}, "text": "А река?"})

    assert bot.chats == {42: 5}
    # Диалог создали один раз, сообщений отправили два
    assert sum(1 for m, url, _ in sent if m == "POST" and url.endswith("/conversations")) == 1
    assert [body["content"] for m, url, body in sent if url.endswith("/messages")] == [
        "Столица Португалии?",
        "А река?",
    ]
    assert texts_sent_to_telegram(sent) == ["Лиссабон", "Лиссабон"]


def test_api_error_goes_to_chat_instead_of_crashing(fake_httpx):
    sent, replies = fake_httpx
    replies["/conversations"] = FakeResponse(201, {"id": 5})
    replies["/messages"] = FakeResponse(502, text="OpenRouter ответил 429")

    bot.handle_message({"chat": {"id": 42}, "text": "Привет"})

    assert texts_sent_to_telegram(sent) == ["Не получилось: API ответил 502\nOpenRouter ответил 429"]


def test_non_text_message_gets_polite_refusal(fake_httpx):
    sent, _ = fake_httpx

    bot.handle_message({"chat": {"id": 42}, "photo": [{"file_id": "x"}]})

    assert texts_sent_to_telegram(sent) == ["Я понимаю только текст."]


def test_unreachable_api_tells_user_instead_of_losing_message(fake_httpx, monkeypatch):
    """Если uvicorn не поднят, человек должен это увидеть в чате."""
    sent, _ = fake_httpx

    def refuse(url, json=None, timeout=None):
        sent.append(("POST", url, json))
        if "api.telegram.org" in url:
            return FakeResponse()
        raise bot.httpx.ConnectError("Connection refused")

    monkeypatch.setattr(bot.httpx, "post", refuse)
    bot.handle_message({"chat": {"id": 42}, "text": "Привет"})

    assert texts_sent_to_telegram(sent) == [
        "API не отвечает: http://127.0.0.1:8906\nЗапущен ли uvicorn? (ConnectError)"
    ]


def test_telegram_error_does_not_crash_polling(fake_httpx, monkeypatch):
    """409 (вторая копия бота) — возвращаем пустой список, а не падаем."""
    monkeypatch.setattr(bot.httpx, "get", lambda url, params=None, timeout=None: FakeResponse(
        409, {"ok": False, "error_code": 409, "description": "Conflict: terminated by other getUpdates"}
    ))

    assert bot.get_updates(0) == []
