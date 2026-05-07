#!/usr/bin/env python
"""
Setup database schema từ SQLAlchemy models (bypass Alembic).
Dùng cho local development với SQLite.
"""
import sys
from app.core.db import Base, get_engine

def setup_database():
    """Create all tables from Base metadata."""
    engine = get_engine()
    try:
        print("🔧 Creating database schema...")
        Base.metadata.create_all(engine)
        print("✅ Database schema created successfully!")
        return 0
    except Exception as e:
        print(f"❌ Error creating schema: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(setup_database())
