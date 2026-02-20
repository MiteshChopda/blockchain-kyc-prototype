# Blockchain KYC Prototype

A full-stack prototype application for submitting, reviewing, and tracking Know Your Customer (KYC) documents. The backend features a mock blockchain implementation to maintain an immutable log of KYC events and status changes.

## Tech Stack

* **Backend:** FastAPI, Python 3.12, `uv` (Package Manager)
* **Frontend:** React, Vite, `pnpm` (Package Manager)

## Prerequisites

Ensure you have the following installed on your system:
* [Python 3.12+](https://www.python.org/downloads/)
* [Node.js](https://nodejs.org/)
* [`uv`](https://docs.astral.sh/uv/) (Python package manager)
* [`pnpm`](https://pnpm.io/) (Node package manager)

## Quick Start

The project includes a unified startup script that automatically handles dependency installation and starts both servers concurrently.

1. Open a terminal in the root directory of the project.
2. Run the start script:

   ```bash
   python start.py
