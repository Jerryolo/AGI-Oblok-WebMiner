import asyncio

from clients.k3 import K3Client


def test_required_tool_choice_is_forwarded(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self): pass
        def json(self): return {"choices": [{"message": {"tool_calls": [{"id": "1"}]}}]}

    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def post(self, url, json, headers):
            captured.update(json)
            return Response()

    monkeypatch.setattr("clients.k3.httpx.AsyncClient", Client)
    asyncio.run(K3Client("http://k3").chat([{"role": "user", "content": "use tool"}],
                                            tools=[{"type": "function"}], tool_choice="required"))
    assert captured["tool_choice"] == "required"
