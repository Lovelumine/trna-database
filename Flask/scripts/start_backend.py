#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FLASK_DIR = SCRIPT_DIR.parent
ROOT_DIR = FLASK_DIR.parent
REQUIREMENTS = FLASK_DIR / "requirements.txt"
DEPS_MARKER = FLASK_DIR / ".deps_installed.system"
REQUIREMENTS_HASH_FILE = FLASK_DIR / ".requirements.system.sha256"


def is_windows() -> bool:
    return os.name == "nt"


def current_python_path() -> Path:
    return Path(sys.executable).resolve()


def run(cmd: list[str], cwd: Path | None = None):
    print("[ENSURE]", " ".join(str(part) for part in cmd))
    subprocess.check_call(cmd, cwd=str(cwd or ROOT_DIR))


def requirements_sha256() -> str:
    if not REQUIREMENTS.exists():
        raise FileNotFoundError(f"requirements file not found: {REQUIREMENTS}")
    return hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()


def needs_dependency_install() -> bool:
    if not DEPS_MARKER.exists():
        return True
    if not REQUIREMENTS_HASH_FILE.exists():
        return True
    try:
        return REQUIREMENTS_HASH_FILE.read_text(encoding="utf-8").strip() != requirements_sha256()
    except OSError:
        return True


def install_requirements(python_path: Path):
    if not REQUIREMENTS.exists():
        raise FileNotFoundError(f"requirements file not found: {REQUIREMENTS}")
    run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], cwd=FLASK_DIR)
    run([str(python_path), "-m", "pip", "install", "-r", str(REQUIREMENTS)], cwd=FLASK_DIR)
    DEPS_MARKER.write_text("ok\n", encoding="utf-8")
    REQUIREMENTS_HASH_FILE.write_text(requirements_sha256() + "\n", encoding="utf-8")


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

    python_path = current_python_path()
    deps_missing_or_changed = needs_dependency_install()

    if install_flag or (deps_missing_or_changed and not no_install_flag):
        install_requirements(python_path)

    try:
        raise SystemExit(start_server(python_path, host=args.host, port=args.port))
    except KeyboardInterrupt:
        print("\n[ENSURE] backend stopped")
        raise SystemExit(130)


if __name__ == "__main__":
    main()
