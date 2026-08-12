# API v1

## `POST /v1/k3/chat`

Żądanie zawiera `input_text`, `agent_id`, `operation` (`CHAT|TRANSACT`), `risk`, opcjonalne `tools`, `tool_choice`, `json_schema`, `partial_mode` i `approval_signature`. Podpis TRANSACT to base64 podpisu Ed25519 nad bajtami UTF-8 `input_text`. Odpowiedź: tekst, werdykt, powód, tryb, stan blokady i `record_id`.

W `shadow` polityka jest obserwowana, ale K3 jest wywoływany; `advisory` zwraca ostrzeżenia; `enforcing` nie wywołuje K3 dla WAIT/SILENCE/REJECT. Awaria K3 daje HTTP 502 i podpisany REJECT (fail-closed). `tool_choice="required"` jest przesyłane do K3, a brak `tool_calls` jest błędem.

## Audyt i sterowanie

- `GET /v1/audit/chain?offset=0&limit=100` — stronicowane rekordy i publiczny klucz bramki.
- `POST /v1/audit/verify` — weryfikuje przekazane `records`/`public_key` albo bieżący łańcuch.
- `POST /v1/control/stop` — trwały human override; blokuje nowe operacje.
- `POST /v1/control/resume` — świadome wznowienie operatora (w produkcji chronić RBAC/MFA).
- `GET /healthz` — tryb i stan STOP.

Pełne schematy i przykłady są dostępne w `/docs` (OpenAPI).
