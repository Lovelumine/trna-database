#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import getpass
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)
FLASK_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if FLASK_ROOT not in sys.path:
    sys.path.insert(0, FLASK_ROOT)

from app import create_app
from app.admin import ensure_admin_tables, upsert_admin_user


def main():
    parser = argparse.ArgumentParser(description="Create or reset an ENSURE admin user.")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--password", default="", help="Initial password; omit to prompt")
    parser.add_argument("--role", default="admin", help="Admin role")
    args = parser.parse_args()

    password = args.password or os.getenv("ENSURE_ADMIN_PASSWORD") or ""
    if not password:
        password = getpass.getpass("Password: ")

    app = create_app()
    with app.app_context():
        ensure_admin_tables()
        user, created = upsert_admin_user(args.username, password, role=args.role)
        print(
            f"{'created' if created else 'updated'} admin user "
            f"{user.username} (role={user.role})"
        )


if __name__ == "__main__":
    main()
