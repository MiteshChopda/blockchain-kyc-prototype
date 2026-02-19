#!/usr/bin/env python3
"""
start.py — Project launcher for Blockchain KYC Prototype
Starts both the FastAPI backend and Vite frontend reliably.

Usage:
    python start.py              # start everything
    python start.py --no-install # skip dependency install
"""

import subprocess
import sys
import os
import time
import signal
import shutil
import argparse
import socket
from pathlib import Path

# ─────────────────────────────────────────────
# Configuration — adjust these if your layout differs
# ─────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()

# Backend: main.py lives at project root
BACKEND_DIR = ROOT 
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8000

# Frontend: folder containing package.json
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_PORT = 5173

# Dirs the backend needs before starting
REQUIRED_DIRS = [
    ROOT / "uploads",
    ROOT / "data",
]

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"

def log(msg):  print(f"{BOLD}{CYAN}[kyc]{RESET}  {msg}")
def ok(msg):   print(f"{BOLD}{GREEN}[ ok]{RESET}  {msg}")
def warn(msg): print(f"{BOLD}{YELLOW}[warn]{RESET} {msg}")
def die(msg):  print(f"{BOLD}{RED}[err]{RESET}  {msg}"); sys.exit(1)


# ─────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────
def find_exe(*names):
    """Return first executable found on PATH, or None."""
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) != 0


def wait_for_port(port, timeout=30):
    """Block until port is in use (something started listening)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not is_port_free(port):
            return True
        time.sleep(0.5)
    return False


def free_port(port):
    """Kill whatever process is holding a port."""
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["netstat", "-ano"], text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True)
        except Exception:
            pass
    else:
        subprocess.run(
            f"lsof -ti tcp:{port} | xargs kill -9 2>/dev/null || true",
            shell=True
        )
    time.sleep(1)


def run(cmd, cwd=None, label=""):
    """Run a command, raise on failure with a clear message."""
    try:
        subprocess.run(cmd, check=True, cwd=cwd)
    except FileNotFoundError:
        die(f"Command not found: {cmd[0]}\n  Is it installed and on your PATH?")
    except subprocess.CalledProcessError as e:
        die(f"{label or ' '.join(str(c) for c in cmd)} failed (exit {e.returncode})")


# ─────────────────────────────────────────────
# Pre-flight checks
# ─────────────────────────────────────────────
def check_python():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 11):
        die(
            f"Python 3.11+ required, found {major}.{minor}.\n"
            "  Download: https://python.org"
        )
    ok(f"Python {major}.{minor}")


def check_node():
    node = find_exe("node")
    if not node:
        die(
            "Node.js not found.\n"
            "  Download LTS from https://nodejs.org"
        )
    ver = subprocess.check_output([node, "--version"], text=True).strip()
    ok(f"Node {ver}")


def check_npm():
    npm = find_exe("npm")
    if not npm:
        die(
            "npm not found. It ships with Node.js — reinstall from https://nodejs.org"
        )
    ok(f"npm found")
    return npm


def resolve_frontend_dir():
    """Find the frontend dir even if it's not named 'frontend'."""
    if (FRONTEND_DIR / "package.json").exists():
        return FRONTEND_DIR
    # Search one level deep for any package.json
    candidates = [p.parent for p in ROOT.glob("*/package.json")]
    if len(candidates) == 1:
        warn(f"Frontend found at ./{candidates[0].name}/ instead of ./frontend/")
        return candidates[0]
    if len(candidates) > 1:
        die(
            f"Multiple package.json files found: {[str(c) for c in candidates]}\n"
            "  Set FRONTEND_DIR at the top of start.py to the correct one."
        )
    die(
        f"No frontend/package.json found.\n"
        f"  Expected: {FRONTEND_DIR / 'package.json'}\n"
        "  Edit FRONTEND_DIR in start.py if your folder has a different name."
    )


def check_backend():
    if not (BACKEND_DIR / "main.py").exists():
        die(
            f"main.py not found in {BACKEND_DIR}\n"
            "  Edit BACKEND_DIR in start.py if your layout differs."
        )
    ok(f"Backend entry: main.py")


# ─────────────────────────────────────────────
# Dependency installation
# ─────────────────────────────────────────────
def install_backend():
    log("Installing backend dependencies...")

    uv  = find_exe("uv")
    pip = [sys.executable, "-m", "pip"]

    pyproject    = BACKEND_DIR / "pyproject.toml"
    requirements = BACKEND_DIR / "requirements.txt"

    if pyproject.exists():
        if uv:
            run(["uv", "pip", "install", "-e", str(BACKEND_DIR)],
                label="uv pip install (backend)")
        else:
            run(pip + ["install", "-q", "-e", str(BACKEND_DIR)],
                label="pip install (backend)")

    elif requirements.exists():
        if uv:
            run(["uv", "pip", "install", "-r", str(requirements)],
                label="uv pip install -r requirements.txt")
        else:
            run(pip + ["install", "-q", "-r", str(requirements)],
                label="pip install -r requirements.txt")

    else:
        warn("No pyproject.toml or requirements.txt — installing known deps directly")
        run(pip + ["install", "-q",
                   "fastapi[standard]", "uvicorn[standard]", "python-multipart"],
            label="pip install fallback")

    ok("Backend deps ready")


def install_frontend(frontend_dir, npm):
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        log("Syncing frontend dependencies (npm install)...")
    else:
        log("Installing frontend dependencies (first run — may take a minute)...")

    run([npm, "install"], cwd=frontend_dir, label="npm install")
    ok("Frontend deps ready")


# ─────────────────────────────────────────────
# Process management
# ─────────────────────────────────────────────
processes = []  # list of (label, Popen)


def start_backend():
    log(f"Starting backend → http://{BACKEND_HOST}:{BACKEND_PORT}")

    uvicorn_bin = find_exe("uvicorn")
    cmd = (
        [uvicorn_bin] if uvicorn_bin
        else [sys.executable, "-m", "uvicorn"]
    ) + [
        "main:app",
        "--host", BACKEND_HOST,
        "--port", str(BACKEND_PORT),
        "--reload",
    ]

    p = subprocess.Popen(cmd, cwd=BACKEND_DIR)
    processes.append(["backend", p])

    if wait_for_port(BACKEND_PORT, timeout=25):
        ok(f"Backend ready → http://{BACKEND_HOST}:{BACKEND_PORT}")
    else:
        p.kill()
        die(
            "Backend didn't start within 25 s.\n"
            "  Run manually to see the error:\n"
            f"    cd {BACKEND_DIR} && uvicorn main:app --reload"
        )
    return p


def start_frontend(frontend_dir, npm):
    log(f"Starting frontend → http://localhost:{FRONTEND_PORT}")

    p = subprocess.Popen([npm, "run", "dev"], cwd=frontend_dir)
    processes.append(["frontend", p])

    if wait_for_port(FRONTEND_PORT, timeout=30):
        ok(f"Frontend ready → http://localhost:{FRONTEND_PORT}")
    else:
        warn("Frontend taking longer than expected — check output above")
    return p


def shutdown(sig=None, frame=None):
    print()
    log("Shutting down...")
    for label, p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            p.kill()
        ok(f"{label} stopped")
    sys.exit(0)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Start Blockchain KYC Prototype"
    )
    parser.add_argument(
        "--no-install", action="store_true",
        help="Skip npm/pip install (use when deps are already installed)"
    )
    args = parser.parse_args()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"\n{BOLD}{'─' * 50}{RESET}")
    print(f"{BOLD}  Blockchain KYC — starting up{RESET}")
    print(f"{BOLD}{'─' * 50}{RESET}\n")

    # ── 1. Environment checks ────────────────────
    log("Checking environment...")
    check_python()
    check_node()
    npm = check_npm()
    check_backend()
    frontend_dir = resolve_frontend_dir()
    print()

    # ── 2. Create required runtime dirs / files ──
    for d in REQUIRED_DIRS:
        d.mkdir(parents=True, exist_ok=True)

    kyc_data = ROOT / "data" / "kyc_data.json"
    if not kyc_data.exists():
        kyc_data.write_text("{}")
        ok("Created data/kyc_data.json")

    # ── 3. Handle port conflicts ─────────────────
    for port in [BACKEND_PORT, FRONTEND_PORT]:
        if not is_port_free(port):
            warn(f"Port {port} already in use — freeing it...")
            free_port(port)
            if not is_port_free(port):
                die(
                    f"Port {port} is still occupied.\n"
                    "  Close the process using it and retry."
                )
            ok(f"Port {port} freed")

    # ── 4. Install dependencies ──────────────────
    if not args.no_install:
        install_backend()
        install_frontend(frontend_dir, npm)
        print()
    else:
        warn("Skipping dependency install (--no-install)")

    # ── 5. Launch ────────────────────────────────
    start_backend()
    start_frontend(frontend_dir, npm)

    print(f"\n{BOLD}{'─' * 50}{RESET}")
    print(f"{BOLD}{GREEN}  All systems go!{RESET}")
    print(f"  App       →  http://localhost:{FRONTEND_PORT}")
    print(f"  API       →  http://localhost:{BACKEND_PORT}")
    print(f"  API docs  →  http://localhost:{BACKEND_PORT}/docs")
    print(f"{BOLD}  Ctrl+C to stop both servers{RESET}")
    print(f"{BOLD}{'─' * 50}{RESET}\n")

    # ── 6. Watch & auto-restart if a server crashes ──
    while True:
        time.sleep(3)
        for entry in processes:
            label, p = entry
            if p.poll() is not None:  # process exited unexpectedly
                warn(f"{label} exited (code {p.returncode}) — restarting...")
                if label == "backend":
                    new_p = start_backend()
                else:
                    new_p = start_frontend(frontend_dir, npm)
                entry[1] = new_p


if __name__ == "__main__":
    main()
