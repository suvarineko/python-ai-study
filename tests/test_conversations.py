"""Юнит-тесты эндпоинтов диалогов: POST/GET/DELETE /conversations."""

def test_create_conversation_returns_201_and_body(client):
    response = client.post("/conversations", json={"title": "Про юнит-тесты"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Про юнит-тесты"
    assert isinstance(body["id"], int)
    assert body["created_at"]
    assert "messages" not in body


def test_get_conversation_returns_detail_with_messages(client, conversation):
    client.post(f"/conversations/{conversation['id']}/messages", json={"content": "Привет"})

    response = client.get(f"/conversations/{conversation['id']}")

    assert response.status_code == 200
    body = response.json()
    assert [message["content"] for message in body["messages"]] == ["Привет"]


def test_get_unknown_conversation_returns_404(client):
    response = client.get("/conversations/999")

    assert response.status_code == 404


def test_delete_conversation_returns_204_and_removes_it(client, conversation):
    response = client.delete(f"/conversations/{conversation['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/conversations/{conversation['id']}").status_code == 404
    assert client.get("/conversations").json() == []


def test_delete_conversation_removes_its_messages(client, conversation):
    client.post(f"/conversations/{conversation['id']}/messages", json={"content": "Привет"})

    client.delete(f"/conversations/{conversation['id']}")

    assert client.get(f"/conversations/{conversation['id']}/messages").status_code == 404
