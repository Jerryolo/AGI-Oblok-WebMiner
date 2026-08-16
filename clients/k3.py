"""Async OpenAI-compatible K3 client with tools, schema and partial streaming."""
import json
import httpx


class K3Client:
    def __init__(self, base_url: str, api_key: str = "", model: str = "kimi-k3"):
        self.base_url, self.api_key, self.model = base_url.rstrip("/"), api_key, model

    async def chat(self, messages, *, tools=None, tool_choice=None, json_schema=None, partial_mode=False):
        payload = {"model": self.model, "messages": messages, "stream": partial_mode}
        if tools is not None: payload["tools"] = tools
        if tool_choice is not None: payload["tool_choice"] = tool_choice
        if json_schema is not None:
            payload["response_format"] = {"type": "json_schema", "json_schema": json_schema}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            if not partial_mode:
                return response.json()
            # Normalize an SSE stream to the same response shape while preserving
            # partial-mode compatibility for gateways that need one audit record.
            content, tool_calls, model = [], [], None
            for line in response.text.splitlines():
                if not line.startswith("data:") or line[5:].strip() == "[DONE]":
                    continue
                chunk = json.loads(line[5:].strip())
                model = model or chunk.get("model")
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                if delta.get("content"): content.append(delta["content"])
                if delta.get("tool_calls"): tool_calls.extend(delta["tool_calls"])
            return {"model": model, "choices": [{"message": {
                "content": "".join(content), "tool_calls": tool_calls}}]}
