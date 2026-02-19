
from pydantic import BaseModel


class KYCSubmit(BaseModel):
    name: str
    dob: str
    address: str
    documentId: str


class VerifyRequest(BaseModel):
    decision: str  # VERIFIED or REJECTED
