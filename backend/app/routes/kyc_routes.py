
from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil

from app.services import kyc_service
from app.models.kyc_models import VerifyRequest

router = APIRouter(prefix="/kyc", tags=["KYC"])

UPLOAD_DIR = Path("uploads")


@router.post("/submit")
async def submit_kyc(
    name: str = Form(...),
    dob: str = Form(...),
    address: str = Form(...),
    documentId: str = Form(...),
    file: UploadFile = File(...)
):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    payload = {
        "name": name,
        "dob": dob,
        "address": address,
        "documentId": documentId,
    }

    kyc_id = kyc_service.submit_kyc(payload, str(file_path))
    return {"kycId": kyc_id}


@router.get("/pending")
def get_pending():
    return {"pending": kyc_service.get_pending_kycs()}


@router.post("/verify/{kyc_id}")
def verify(kyc_id: str, req: VerifyRequest):
    kyc_service.verify_kyc(kyc_id, req.decision)
    return {"message": "updated"}


@router.get("/status/{kyc_id}")
def status(kyc_id: str):
    return {"status": kyc_service.get_kyc_status(kyc_id)}

@router.get("/{kyc_id}")
def get_kyc_details(kyc_id: str):
    data = kyc_service.get_kyc_details(kyc_id)

    if not data:
        return {"error": "KYC not found"}

    return {
        "kycId": kyc_id,
        **data
    }
