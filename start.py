import subprocess
import sys
import os
import time
import shutil

def install_backend(backend_dir):
    """Checks for dependencies and installs them if needed."""
    print("🔍 Checking Backend dependencies...")
    
    # Check if using uv (based on uv.lock presence)
    if os.path.exists(os.path.join(backend_dir, "uv.lock")):
        print("📦 Found uv.lock. Running 'uv sync'...")
        subprocess.run(["uv", "sync"], cwd=backend_dir, check=True)
    
    # Fallback to requirements.txt if uv is not used but exists
    elif os.path.exists(os.path.join(backend_dir, "requirements.txt")):
        print("📦 Found requirements.txt. Running pip install...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=backend_dir, check=True)
    else:
        print("⚠️ No dependency lockfile found (uv.lock or requirements.txt). Skipping install.")

def install_frontend(frontend_dir):
    """Checks if node_modules exists, installs if missing."""
    node_modules = os.path.join(frontend_dir, "node_modules")
    
    # Detect package manager
    if os.path.exists(os.path.join(frontend_dir, "pnpm-lock.yaml")):
        manager = "pnpm"
    elif os.path.exists(os.path.join(frontend_dir, "yarn.lock")):
        manager = "yarn"
    else:
        manager = "npm"

    # Only install if node_modules is missing
    if not os.path.exists(node_modules):
        print(f"📦 node_modules not found. Installing with {manager}...")
        # shell=True is often safer for npm commands on Windows
        subprocess.run(f"{manager} install", cwd=frontend_dir, shell=True, check=True)
    else:
        print(f"✅ Frontend dependencies appear installed ({manager}).")

    return manager

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    # 1. Install Dependencies
    try:
        install_backend(backend_dir)
        pkg_manager = install_frontend(frontend_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return

    # 2. Define Commands
    # If using uv, we should ideally use `uv run` or ensure the venv is active. 
    # For simplicity, we assume `uv sync` created a .venv and we use that python.
    
    venv_python = os.path.join(backend_dir, ".venv", "Scripts", "python.exe") if os.name == 'nt' else os.path.join(backend_dir, ".venv", "bin", "python")
    
    # Fallback to system python if venv doesn't exist (unlikely if uv sync ran)
    python_exec = venv_python if os.path.exists(venv_python) else sys.executable

    backend_cmd = [python_exec, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"]
    frontend_cmd = f"{pkg_manager} run dev"

    # 3. Start Servers
    print("\n🚀 Starting FastAPI Backend...")
    backend_process = subprocess.Popen(backend_cmd, cwd=backend_dir)

    print(f"🚀 Starting Vite Frontend ({pkg_manager})...")
    # shell=True required for npm/pnpm on Windows
    frontend_process = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=True)

    # 4. Monitor Loop
    try:
        while True:
            time.sleep(1)
            # If a process crashes, exit
            if backend_process.poll() is not None:
                print("❌ Backend crashed!")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend crashed!")
                break
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_process.terminate()
        # On Windows, terminating the shell doesn't always kill the child node process
        if os.name == 'nt':
            subprocess.run(f"taskkill /F /T /PID {frontend_process.pid}", shell=True, stderr=subprocess.DEVNULL)
        else:
            frontend_process.terminate()
        
        print("✅ Servers stopped.")

if __name__ == "__main__":
    main()
