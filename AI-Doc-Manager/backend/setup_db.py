#!/usr/bin/env python
"""Setup database schema from SQLAlchemy models for local SQLite development."""

import sys

from app.core.db import Base, get_engine


def setup_database() -> int:
    """Create all tables from Base metadata."""
    engine = get_engine()
    try:
        print("Creating database schema...")
        Base.metadata.create_all(engine)
        print("Database schema created successfully.")
        return 0
    except Exception as exc:
        print(f"Error creating schema: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(setup_database())
