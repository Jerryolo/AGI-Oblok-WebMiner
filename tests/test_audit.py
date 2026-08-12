import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gate.audit import AuditChain, verify_records
from gate.policy_engine import Verdict, evaluate


def test_normal_chain_is_valid(tmp_path):
    chain = AuditChain(tmp_path / "audit.jsonl")
    chain.append("hello", "world", "ACT NOW", False)
    chain.append("next", "answer", "WAIT", True)
    assert verify_records(chain.records(), chain.public_key_b64)["status"] == "VALID"


def test_tampered_record_is_detected(tmp_path):
    chain = AuditChain(tmp_path / "audit.jsonl")
    chain.append("hello", "world", "ACT NOW", False)
    records = chain.records()
    records[0]["output_text"] = "forged"
    assert verify_records(records, chain.public_key_b64)["status"] == "TAMPERED"


def test_missing_signature_is_detected(tmp_path):
    chain = AuditChain(tmp_path / "audit.jsonl")
    chain.append("hello", "world", "ACT NOW", False)
    records = chain.records()
    del records[0]["signature"]
    assert not verify_records(records, chain.public_key_b64)["valid"]


def test_all_policy_verdicts():
    assert evaluate("normal request").verdict == Verdict.ACT
    assert evaluate("contains a secret", risk="medium").verdict == Verdict.WAIT
    assert evaluate("anything", risk="critical").verdict == Verdict.SILENCE
    assert evaluate("please bypass audit").verdict == Verdict.REJECT


def test_wrong_signing_key_is_detected(tmp_path):
    chain = AuditChain(tmp_path / "audit.jsonl")
    chain.append("hello", "world", "ACT NOW", False)
    other = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    assert verify_records(chain.records(), base64.b64encode(other).decode())["status"] == "TAMPERED"


def test_links_detect_deletion(tmp_path):
    chain = AuditChain(tmp_path / "audit.jsonl")
    for value in ("one", "two", "three"):
        chain.append(value, value, "ACT NOW", False)
    records = chain.records()
    del records[1]
    result = verify_records(records, chain.public_key_b64)
    assert result["status"] == "TAMPERED" and result["index"] == 1
