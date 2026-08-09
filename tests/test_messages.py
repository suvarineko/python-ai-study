"""Юнит-тесты эндпоинтов сообщений: POST/GET /conversations/{id}/messages."""

def test_create_message_returns_201_and_body(client, conversation):
    response = client.post(f"/conversations/{conversation['id']}/messages", json={"content": "Как дела?"})

    assert response.status_code == 201
    body = response.json()
    assert body["content"] == "Как дела?"
    assert body["role"] == "user"
    assert body["created_at"]
