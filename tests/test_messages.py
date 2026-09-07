"""Юнит-тесты эндпоинтов сообщений: POST/GET /conversations/{id}/messages."""

def test_create_message_returns_201_and_body(client, conversation):
    response = client.post(f"/conversations/{conversation['id']}/messages", json={"content": "Как дела?"})

    assert response.status_code == 201
    body = response.json()
    assert body["role"] == "assistant"
    assert body["created_at"]

    history = client.get(f"/conversations/{conversation['id']}/messages").json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert history[0]["content"] == "Как дела?"

def test_create_message_returns_ai_dev_response(client, conversation):
    response = client.post(f"/conversations/{conversation['id']}/messages", json={"content": "Проверка для дев стаба"})

    assert response.status_code == 201
    body = response.json()
    assert body["content"] == "Тест дев"
    assert body["role"] == "assistant"
