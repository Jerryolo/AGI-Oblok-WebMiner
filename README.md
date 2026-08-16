# K3 Proof-of-Silence™ Gate

Produkcyjny, samodzielny gateway dla wielu agentów Kimi K3. Każde wywołanie przechodzi przez silnik polityk i zostaje dopisane do podpisanego łańcucha SHA-256. System działa w trybach `shadow`, `advisory` i `enforcing`, domyślnie **fail-closed**.

## Przepływ

`Agent → API Gateway → Policy Engine → Audit Gate → K3 → Audit Gate → Agent`

Werdykty to `ACT NOW`, `WAIT`, `SILENCE` i `REJECT`. Operacja `TRANSACT` wymaga podpisu Ed25519 człowieka nad tekstem wejściowym. STOP blokuje nowe wywołania w trybie enforcing. SQLite przechowuje stan STOP, a append-only JSONL jest przenośnym dowodem audytowym.

## Szybki start

```bash
cp .env.example .env
docker compose up --build
# panel: http://localhost:8080; OpenAPI: http://localhost:8000/docs
```

Bez `K3_BASE_URL` uruchamiany jest deterministyczny adapter lokalny (wyłącznie development). W produkcji ustaw zgodny z OpenAI endpoint K3 i sekret. Klucz podpisujący jest automatycznie tworzony w wolumenie danych; można dostarczyć `POS_PRIVATE_KEY` jako base64 surowych 32 bajtów.

## Development

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
pytest -q
python scripts/verify_chain.py data/audit.jsonl --public-key "$PUBLIC_KEY_BASE64"
```

Frontend statyczny używa `API_BASE` (domyślnie `http://localhost:8000`). Szczegóły: [API](docs/API.md), [architektura](docs/ARCHITECTURE.md), [EU AI Act](docs/EU-AI-ACT-MAP.md), [cennik](docs/PRICING.md) i [wdrożenie](docs/DEPLOYMENT.md).

## Konfiguracja bezpieczeństwa

| Zmienna | Znaczenie |
|---|---|
| `POS_MODE` | `shadow`, `advisory`, `enforcing` |
| `POS_AUDIT_PATH` | ścieżka append-only JSONL |
| `POS_PRIVATE_KEY` | base64 prywatnego klucza Ed25519 |
| `HUMAN_PUBLIC_KEY` | base64 klucza akceptującego TRANSACT |
| `K3_BASE_URL`, `K3_API_KEY`, `K3_MODEL` | adapter K3 |
| `ALLOWED_ORIGINS` | lista originów CORS rozdzielona przecinkami |

## Granice zaufania

Podpis audytowy dowodzi integralności artefaktu, nie prawdziwości odpowiedzi modelu. Dostęp do pliku, kluczy i endpointów należy ograniczyć IAM/mTLS, wykonywać kopie WORM oraz rotować klucze. Decyzje wysokiego ryzyka pozostają pod nadzorem człowieka. Projekt nie stanowi samodzielnej gwarancji zgodności prawnej.

## Licencja komercyjna

Copyright © 2026 NEON AI · Jerzy Skiba. Proof-of-Silence™ jest znakiem projektu. Warunki ofertowe znajdują się w `docs/PRICING.md`; brak domyślnej licencji open-source.
