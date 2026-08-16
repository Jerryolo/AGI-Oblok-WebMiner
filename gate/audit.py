"""Append-only, Ed25519-signed SHA-256 audit chain."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

GENESIS = "0" * 64


def canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def _raw_public(key: Ed25519PublicKey) -> bytes:
    return key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)


class AuditChain:
    def __init__(self, path: str | Path, private_key_b64: str | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.private_key = (Ed25519PrivateKey.from_private_bytes(base64.b64decode(private_key_b64))
                            if private_key_b64 else Ed25519PrivateKey.generate())

    @property
    def public_key_b64(self) -> str:
        return base64.b64encode(_raw_public(self.private_key.public_key())).decode()

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self._lock, self.path.open(encoding="utf-8") as stream:
            return [json.loads(line) for line in stream if line.strip()]

    def append(self, input_text: str, output_text: str, verdict: str,
               human_accountable: bool, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        with self._lock:
            existing = self.records()
            body = {
                "record_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "input_text": input_text,
                "output_text": output_text,
                "verdict": verdict,
                "human_accountable": human_accountable,
                "previous_hash": existing[-1]["record_hash"] if existing else GENESIS,
                "metadata": metadata or {},
            }
            record_hash = hashlib.sha256(canonical(body)).hexdigest()
            record = {**body, "record_hash": record_hash,
                      "signature": base64.b64encode(self.private_key.sign(bytes.fromhex(record_hash))).decode()}
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            return record


def verify_records(records: list[dict[str, Any]], public_key_b64: str) -> dict[str, Any]:
    try:
        key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64, validate=True))
    except (ValueError, TypeError) as exc:
        return {"status": "TAMPERED", "valid": False, "index": None, "reason": f"invalid public key: {exc}"}
    previous = GENESIS
    required = {"record_id", "timestamp", "input_text", "output_text", "verdict",
                "human_accountable", "previous_hash", "record_hash", "signature"}
    for index, record in enumerate(records):
        try:
            if not required.issubset(record) or record["previous_hash"] != previous:
                raise ValueError("missing field or broken link")
            body = {k: v for k, v in record.items() if k not in {"record_hash", "signature"}}
            expected = hashlib.sha256(canonical(body)).hexdigest()
            if expected != record["record_hash"]:
                raise ValueError("hash mismatch")
            key.verify(base64.b64decode(record["signature"]), bytes.fromhex(expected))
            previous = expected
        except (ValueError, KeyError, InvalidSignature, TypeError) as exc:
            return {"status": "TAMPERED", "valid": False, "index": index, "reason": str(exc)}
    return {"status": "VALID", "valid": True, "records": len(records), "head": previous}


def verify_file(path: str | Path, public_key_b64: str) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        return verify_records([json.loads(line) for line in stream if line.strip()], public_key_b64)
