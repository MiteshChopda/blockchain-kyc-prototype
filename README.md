# Blockchain KYC Prototype

A simple KYC (Know Your Customer) verification system using a blockchain-inspired audit trail.

## Stack

- **Backend**: FastAPI + Python 3.12
- **Frontend**: React + Vite

## Project Structure

```
/
├── backend/
│   ├── main.py
│   ├── app/
│   │   ├── models/kyc_models.py
│   │   ├── routes/kyc_routes.py
│   │   └── services/
│   │       ├── blockchain.py
│   │       └── kyc_service.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/kycApi.js
│   │   ├── components/
│   │   ├── pages/
│   │   └── main.jsx
│   └── package.json
└── start.py
```

## Prerequisites

- Python 3.12+
- Node.js 18+
- `uv` or `pip` for Python deps

## Setup & Run

```bash
python start.py
```

This installs dependencies and starts both servers:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Pages

| Route | Description |
|-------|-------------|
| `/` | Submit a new KYC application |
| `/verifier` | View and action pending KYCs |
| `/verifier/:id` | Review and approve/reject a KYC |
| `/status` | Check KYC status by ID |
