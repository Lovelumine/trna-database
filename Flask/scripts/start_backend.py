#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FLASK_DIR = SCRIPT_DIR.parent
ROOT_DIR = FLASK_DIR.parent
VENV_DIR = FLASK_DIR / ".venv"
REQUIREMENTS = FLASK_DIR / "requirements.txt"


def is_windows() -> bool:
    return os.name == "nt"


def venv_python_path() -> Path:
    if is_windows():
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_venv() -> Path:
    python_path = venv_python_path()
    if python_path.exists():
        return python_path

    print(f"[ENSURE] creating virtual environment at {VENV_DIR}")
    builder = venv.EnvBuilder(with_pip=True, clear=False, upgrade=False)
    builder.create(str(VENV_DIR))
    if not python_path.exists():
        raise RuntimeError(f"virtualenv created but python not found: {python_path}")
    return python_path


def run(cmd: list[str], cwd: Path | None = None):
    print("[ENSURE]", " ".join(str(part) for part in cmd))
    subprocess.check_call(cmd, cwd=str(cwd or ROOT_DIR))


def install_requirements(python_path: Path):
    if not REQUIREMENTS.exists():
        raise FileNotFoundError(f"requirements file not found: {REQUIREMENTS}")
    run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], cwd=FLASK_DIR)
    run([str(python_path), "-m", "pip", "install", "-r", str(REQUIREMENTS)], cwd=FLASK_DIR)


def parse_args():
    parser = argparse.ArgumentParser(description="Start the ENSURE Flask backend.")
    parser.add_argument("--install", "--bootstrap", action="store_true", dest="install", help="Force reinstall backend dependencies")
    parser.add_argument("--no-install", action="store_true", help="Skip dependency installation")
    parser.add_argument("--host", default="127.0.0.1", help="Backend bind host, default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8010, help="Backend bind port, default: 8010")
    return parser.parse_args()


def start_server(python_path: Path, host: str, port: int):
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    env["ENSURE_BACKEND_HOST"] = str(host)
    env["ENSURE_BACKEND_PORT"] = str(port)
    os.chdir(FLASK_DIR)
    print(f"[ENSURE] starting Flask backend on http://{host}:{port}")
    return subprocess.call([str(python_path), "wsgi.py"], cwd=str(FLASK_DIR), env=env)


def main():
    args = parse_args()
    install_flag = bool(args.install)
    no_install_flag = bool(args.no_install)

    python_path = ensure_venv()
    first_boot = not (VENV_DIR / ".deps_installed").exists()

    if install_flag or (first_boot and not no_install_flag):
        install_requirements(python_path)
        (VENV_DIR / ".deps_installed").write_text("ok\n", encoding="utf-8")

    try:
        raise SystemExit(start_server(python_path, host=args.host, port=args.port))
    except KeyboardInterrupt:
        print("\n[ENSURE] backend stopped")
        raise SystemExit(130)


if __name__ == "__main__":
    main()
