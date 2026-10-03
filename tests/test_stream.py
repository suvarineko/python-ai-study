def _read_sse(response):
      """Собирает полезную нагрузку всех кадров `data: ...`."""
      chunks = []
      for line in response.iter_lines():
          if line.startswith("data: "):
              chunks.append(line[len("data: "):])
      return chunks


def test_stream_sends_tokens_then_done(client, conversation):
    with client.stream(
        "POST",
        f"/conversations/{conversation['id']}/messages/stream",
        json={"content": "Привет"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        chunks = _read_sse(response)

    assert chunks[-1] == "[DONE]"
    assert "".join(chunks[:-1]) == "Тест дев"


def test_stream_persists_user_and_assistant(client, conversation):
    with client.stream(
        "POST",
        f"/conversations/{conversation['id']}/messages/stream",
        json={"content": "Привет"},
    ) as response:
        list(response.iter_lines())  # дочитать стрим до конца → сработает персист ассистента

    history = client.get(f"/conversations/{conversation['id']}/messages").json()
    assert [(m["role"], m["content"]) for m in history] == [
        ("user", "Привет"),
        ("assistant", "Тест дев"),
    ]


def test_stream_unknown_conversation_returns_404(client):
    with client.stream(
        "POST",
        "/conversations/999/messages/stream",
        json={"content": "Привет"},
    ) as response:
        assert response.status_code == 404
