"""Телеграм-бот: тонкий клиент к нашему же HTTP API.

Как запустить:
  1. Напишите @BotFather в Телеграме, команда /newbot — он выдаст токен.
  2. Положите токен в .env:  TELEGRAM_BOT_TOKEN=123456:AA...
  3. В одном терминале поднимите API:  python -m uvicorn app.main:app --reload --port 8906
  4. В другом запустите бота:          python -m app.bot

Как это работает, если совсем коротко:
  getUpdates   — спрашиваем у Телеграма «есть новые сообщения?»
  POST /messages — пересылаем текст в наш API, он ходит в модель
  sendMessage  — отправляем ответ модели обратно в чат

Ни фреймворков, ни asyncio: обычный цикл и три HTTP-запроса. Всё, что бот
умеет, лежит в пяти функциях ниже.
"""

import httpx

from app.config import settings

# Все методы Телеграма — это просто URL вида .../bot<ТОКЕН>/<имяМетода>
TELEGRAM_API = f"https://api.telegram.org/bot{settings.telegram_bot_token}"

# Какому диалогу в нашей БД соответствует чат в Телеграме: {chat_id: conversation_id}.
# Словарь живёт в памяти процесса — после перезапуска бота диалоги начнутся заново.
chats: dict[int, int] = {}


def send_message(chat_id: int, text: str) -> None:
    """Написать в чат."""
    httpx.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=30,
    )


def get_updates(offset: int) -> list[dict]:
    """Забрать новые сообщения.

    Это long polling: если сообщений нет, Телеграм держит запрос до 30 секунд
    и только потом отвечает пустым списком. Поэтому цикл в main() не крутится
    впустую и не спамит запросами.
    """
    response = httpx.get(
        f"{TELEGRAM_API}/getUpdates",
        params={"offset": offset, "timeout": 30},
        timeout=60,  # больше, чем timeout Телеграма, иначе httpx оборвёт раньше
    )
    answer = response.json()
    if not answer.get("ok"):
        # Чаще всего это 409: запущена вторая копия бота. Без этой проверки
        # было бы падение с невнятным KeyError: 'result'.
        print("Телеграм вернул ошибку:", answer.get("description", answer))
        return []
    return answer["result"]


def get_conversation_id(chat_id: int) -> int:
    """id диалога для этого чата. Если диалога ещё нет — создаём через наш API."""
    if chat_id not in chats:
        response = httpx.post(
            f"{settings.api_base_url}/conversations",
            json={"title": f"Телеграм {chat_id}"},
            timeout=30,
        )
        response.raise_for_status()
        chats[chat_id] = response.json()["id"]
    return chats[chat_id]


def ask_agent(chat_id: int, text: str) -> str:
    """Переслать сообщение в наш API и вернуть ответ модели."""
    try:
        conversation_id = get_conversation_id(chat_id)
        response = httpx.post(
            f"{settings.api_base_url}/conversations/{conversation_id}/messages",
            json={"content": text},
            timeout=settings.openrouter_timeout + 10,  # модель думает дольше, чем обычный запрос
        )
    except httpx.HTTPError as exc:
        # Без этой ветки сообщение пропало бы молча: Телеграму апдейт уже
        # подтверждён, а ошибка ушла бы только в консоль.
        return f"API не отвечает: {settings.api_base_url}\nЗапущен ли uvicorn? ({exc.__class__.__name__})"

    if response.status_code != 201:
        return f"Не получилось: API ответил {response.status_code}\n{response.text[:300]}"
    return response.json()["content"]


def handle_message(message: dict) -> None:
    """Обработать одно сообщение из Телеграма."""
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        chats.pop(chat_id, None)  # забыть старый диалог, следующий вопрос начнёт новый
        send_message(chat_id, "Привет! Напишите вопрос — передам модели.")
        return

    if not text:
        send_message(chat_id, "Я понимаю только текст.")
        return

    send_message(chat_id, ask_agent(chat_id, text))


def main() -> None:
    if not settings.telegram_bot_token:
        raise SystemExit("Не задан TELEGRAM_BOT_TOKEN в .env — токен выдаёт @BotFather")

    print(f"Бот запущен, API: {settings.api_base_url}. Ctrl+C — остановить.")

    offset = 0  # с какого update_id забирать следующую порцию
    while True:
        for update in get_updates(offset):
            # Подтверждаем Телеграму, что этот update обработан: иначе он
            # пришлёт его снова.
            offset = update["update_id"] + 1

            if "message" not in update:
                continue  # нас интересуют только сообщения (не правки, не реакции)

            try:
                handle_message(update["message"])
            except Exception as exc:
                # Один упавший запрос не должен убивать бота целиком.
                print("Ошибка при обработке сообщения:", exc)


if __name__ == "__main__":
    main()
