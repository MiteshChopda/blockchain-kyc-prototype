
import json
import os
import uuid
import hashlib
from pathlib import Path
from app.services.blockchain import blockchain

DATA_FILE = Path("data/kyc_data.json")
UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(exist_ok=True)
DATA_FILE.parent.mkdir(exist_ok=True)

if not DATA_FILE.exists():
    DATA_FILE.write_text(json.dumps({}))


def _load_data():
    return json.loads(DATA_FILE.read_text())


def _save_data(data):
    DATA_FILE.write_text(json.dumps(data, indent=2))


def generate_kyc_hash(payload: dict) -> str:
    sorted_json = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(sorted_json.encode()).hexdigest()


def submit_kyc(kyc_payload: dict, file_path: str):
    db = _load_data()

    kyc_id = str(uuid.uuid4())
    kyc_hash = generate_kyc_hash(kyc_payload)

    db[kyc_id] = {
        **kyc_payload,
        "document_path": file_path,
    }
    _save_data(db)

    blockchain.add_block({
        "kycId": kyc_id,
        "kycHash": kyc_hash,
        "event": "KYC_SUBMITTED",
        "status": "PENDING",
    })

    return kyc_id


def get_pending_kycs():
    pending = []

    for block in blockchain.get_full_chain():
        if block.data.get("event") == "KYC_SUBMITTED":
            kyc_id = block.data["kycId"]

            latest = get_kyc_status(kyc_id)
            if latest == "PENDING":
                pending.append(kyc_id)

    return pending


def verify_kyc(kyc_id: str, decision: str):
    blockchain.add_block({
        "kycId": kyc_id,
        "event": "KYC_VERIFIED",
        "status": decision,
    })


def get_kyc_status(kyc_id: str):
    blocks = blockchain.get_blocks_by_kyc_id(kyc_id)
    if not blocks:
        return "NOT_FOUND"

    latest = sorted(blocks, key=lambda b: b.index)[-1]
    return latest.data.get("status", "UNKNOWN")


def get_kyc_details(kyc_id: str):
    db = _load_data()
    return db.get(kyc_id)
