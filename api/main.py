from __future__ import annotations

import base64
import os
import sqlite3
from pathlib import Path
from typing import Any, Literal

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from clients.k3 import K3Client
from gate.audit import AuditChain, verify_records
from gate.policy_engine import Verdict, evaluate

AUDIT_PATH = os.getenv("POS_AUDIT_PATH", "data/audit.jsonl")
STATE_DB = os.getenv("POS_STATE_DB", "data/state.db")
MODE = os.getenv("POS_MODE", "enforcing")
if MODE not in {"shadow", "advisory", "enforcing"}:
    raise RuntimeError("POS_MODE must be shadow, advisory or enforcing")

chain = AuditChain(AUDIT_PATH, os.getenv("POS_PRIVATE_KEY") or None)
k3 = K3Client(os.getenv("K3_BASE_URL", ""), os.getenv("K3_API_KEY", ""), os.getenv("K3_MODEL", "kimi-k3"))


def db() -> sqlite3.Connection:
    Path(STATE_DB).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(STATE_DB)
    connection.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    return connection


def stopped() -> bool:
    with db() as connection:
        row = connection.execute("SELECT value FROM state WHERE key='stopped'").fetchone()
    return bool(row and row[0] == "1")


class ChatRequest(BaseModel):
    input_text: str = Field(min_length=1, max_length=100_000)
    agent_id: str = Field(default="default", max_length=128)
    operation: Literal["CHAT", "TRANSACT"] = "CHAT"
    risk: Literal["low", "medium", "high", "critical"] = "low"
    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, Any] | None = None
    json_schema: dict[str, Any] | None = None
    partial_mode: bool = False
    approval_signature: str | None = None


class VerifyRequest(BaseModel):
    records: list[dict[str, Any]] | None = None
    public_key: str | None = None


def valid_human_signature(request: ChatRequest) -> bool:
    public = os.getenv("HUMAN_PUBLIC_KEY", "")
    if request.operation != "TRANSACT":
        return False
    if not public or not request.approval_signature:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(base64.b64decode(public)).verify(
            base64.b64decode(request.approval_signature), request.input_text.encode())
        return True
    except (ValueError, InvalidSignature):
        return False


async def call_model(request: ChatRequest) -> tuple[str, dict[str, Any]]:
    if not k3.base_url:  # Explicit development adapter, never an implicit production call.
        return f"[local K3 adapter] {request.input_text}", {"adapter": "local", "tool_calls": []}
    response = await k3.chat([{"role": "user", "content": request.input_text}], tools=request.tools,
                             tool_choice=request.tool_choice, json_schema=request.json_schema,
                             partial_mode=request.partial_mode)
    choice = response.get("choices", [{}])[0].get("message", {})
    if request.tool_choice == "required" and not choice.get("tool_calls"):
        raise RuntimeError("K3 failed required tool choice")
    return choice.get("content") or "", {"model": response.get("model"), "tool_calls": choice.get("tool_calls", [])}


app = FastAPI(title="K3 Proof-of-Silence Gate", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(","),
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Authorization"])


@app.get("/healthz")
def health():
    return {"status": "ok", "mode": MODE, "stopped": stopped()}


@app.post("/v1/k3/chat")
async def chat(request: ChatRequest):
    decision = evaluate(request.input_text, request.operation, request.risk)
    human = valid_human_signature(request)
    if request.operation == "TRANSACT" and not human:
        decision = type(decision)(Verdict.REJECT, "TRANSACT requires a valid human Ed25519 signature")
    if stopped():
        decision = type(decision)(Verdict.REJECT, "human STOP is active")

    blocking = decision.verdict != Verdict.ACT and MODE == "enforcing"
    output, model_meta = "", {}
    if not blocking:
        try:
            output, model_meta = await call_model(request)
        except Exception as exc:
            record = chain.append(request.input_text, "", Verdict.REJECT.value, human,
                                  {"agent_id": request.agent_id, "mode": MODE, "reason": "K3 unavailable"})
            raise HTTPException(502, detail={"message": "K3 unavailable; failed closed", "record_id": record["record_id"]}) from exc

    record = chain.append(request.input_text, output, decision.verdict.value, human,
                          {"agent_id": request.agent_id, "mode": MODE, "reason": decision.reason, **model_meta})
    return {"output_text": output, "verdict": decision.verdict.value, "reason": decision.reason,
            "blocked": blocking, "mode": MODE, "record_id": record["record_id"]}


@app.get("/v1/audit/chain")
def audit_chain(offset: int = 0, limit: int = 100):
    records = chain.records()
    return {"records": records[offset:offset + min(limit, 1000)], "total": len(records),
            "public_key": chain.public_key_b64}


@app.post("/v1/audit/verify")
def audit_verify(request: VerifyRequest):
    return verify_records(request.records if request.records is not None else chain.records(),
                          request.public_key or chain.public_key_b64)


@app.post("/v1/control/stop")
def stop():
    with db() as connection:
        connection.execute("INSERT OR REPLACE INTO state(key,value) VALUES('stopped','1')")
    return {"stopped": True}


@app.post("/v1/control/resume")
def resume():
    with db() as connection:
        connection.execute("INSERT OR REPLACE INTO state(key,value) VALUES('stopped','0')")
    return {"stopped": False}
