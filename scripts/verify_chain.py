#!/usr/bin/env python3
import argparse
import json
import sys

from gate.audit import verify_file

parser = argparse.ArgumentParser(description="Offline Proof-of-Silence chain verifier")
parser.add_argument("jsonl")
parser.add_argument("--public-key", required=True, help="base64 raw Ed25519 public key")
args = parser.parse_args()
result = verify_file(args.jsonl, args.public_key)
print(json.dumps(result, indent=2))
sys.exit(0 if result["valid"] else 2)
