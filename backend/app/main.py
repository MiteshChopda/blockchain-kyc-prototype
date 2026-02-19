
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes.kyc_routes import router as kyc_router

origins = [
    "http://localhost:5173",
]

app = FastAPI(title="Blockchain KYC Prototype")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REQUIRED for document viewing
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(kyc_router)

