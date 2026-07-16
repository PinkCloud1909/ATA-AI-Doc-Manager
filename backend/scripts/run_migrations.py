#!/bin/sh
"""": true
# ^ Shebang for sh; the triple-quote block below is a docstring for Python.
#
# Production migration runner for Cloud Run Jobs or CI/CD.
#
# Usage (Cloud Run Job):
#   gcloud run jobs execute dms-migrate --image IMAGE --set-env-vars=...
#
# Usage (local Docker):
#   docker run --rm -e DATABASE_URL=... IMAGE python scripts/run_migrations.py
#
# This script is SAFE to run multiple times — Alembic only applies new
# migrations, and the seed script is idempotent (INSERT ... ON CONFLICT DO
# NOTHING style via the seed functions).
"""
import os
import subprocess

from seed import main as seed_main


def _run(cmd: list[str]) -> None:
    print(f"▶ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True)


def main() -> None:
    """Apply pending migrations, then seed required IAM data."""
    alembic_ini = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")

    # 1. Apply all pending database migrations.
    _run(["alembic", "-c", alembic_ini, "upgrade", "head"])

    # 2. Seed roles, privileges, and the default admin user.
    seed_main()

    print("✅ Migrations and seed data applied successfully.", flush=True)


if __name__ == "__main__":
    main()
