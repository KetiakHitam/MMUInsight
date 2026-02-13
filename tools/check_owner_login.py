from __future__ import annotations

"""Quick local check for seeded accounts.

Run:
  py tools/check_owner_login.py

It prints the DB URI, whether owner/admin exist, and whether password123 matches.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from extensions import bcrypt
from models import User


def main() -> None:
    with app.app_context():
        print("DB URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

        candidates = ["password123", "admin", "owner"]

        for email in ("owner@mmu.edu.my", "admin@mmu.edu.my", "mod@mmu.edu.my"):
            user = User.query.filter_by(email=email).first()
            print("\n==", email, "==")
            print("exists:", bool(user))
            if not user:
                continue
            print("role:", user.role, "user_type:", user.user_type)
            print("password_hash type:", type(user.password_hash).__name__)
            try:
                for pw in candidates:
                    ok = bcrypt.check_password_hash(user.password_hash, pw)
                    if ok:
                        print("matches password:", pw)
                        break
                else:
                    print("matches password:", "<none of "+", ".join(candidates)+">")
            except Exception as exc:
                print("bcrypt check failed:", repr(exc))


if __name__ == "__main__":
    main()
