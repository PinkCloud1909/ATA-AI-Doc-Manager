#!/usr/bin/env python3
"""
Verify monorepo structure after backend merge

Run this after executing merge_backend.py to validate the merge was successful.
"""

import sys
from pathlib import Path

def check_file(path, description):
    """Check if a file exists."""
    if Path(path).exists():
        size = Path(path).stat().st_size
        print(f"✓ {description:<50} ({size:,} bytes)")
        return True
    else:
        print(f"✗ {description:<50} NOT FOUND")
        return False

def check_dir(path, description, min_files=1):
    """Check if a directory exists and has files."""
    p = Path(path)
    if p.exists() and p.is_dir():
        files = list(p.rglob('*'))
        count = len([f for f in files if f.is_file()])
        if count >= min_files:
            print(f"✓ {description:<50} ({count} files)")
            return True
        else:
            print(f"✗ {description:<50} Only {count} files (expected >= {min_files})")
            return False
    else:
        print(f"✗ {description:<50} NOT FOUND")
        return False

def main():
    print("=" * 80)
    print("🔍 MONOREPO STRUCTURE VERIFICATION")
    print("=" * 80)
    print()
    
    # Check root files
    print("📂 ROOT CONFIGURATION FILES")
    print("-" * 80)
    root_checks = [
        ("docker-compose.yml", "Docker Compose configuration"),
        (".env.example", "Environment variables template"),
        (".gitignore", "Git ignore patterns"),
        (".dockerignore", "Docker ignore patterns"),
        ("README.md", "Root documentation"),
        ("merge_backend.py", "Backend merge script"),
        ("MERGE_SUMMARY.md", "Merge documentation"),
    ]
    
    root_ok = sum(check_file(f, d) for f, d in root_checks)
    print()
    
    # Check backend structure
    print("📂 BACKEND STRUCTURE")
    print("-" * 80)
    backend_checks = [
        ("backend/Dockerfile", "Backend Dockerfile"),
        ("backend/pyproject.toml", "Python dependencies"),
        ("backend/alembic.ini", "Database migrations config"),
        ("backend/.env.example", "Backend env template"),
        ("backend/.dockerignore", "Backend Docker ignore"),
        ("backend/README.md", "Backend documentation"),
    ]
    
    backend_config_ok = sum(check_file(f, d) for f, d in backend_checks)
    
    # Check for app directory (most important)
    backend_dirs = [
        ("backend/app", "Application source", 5),
        ("backend/scripts", "Script utilities", 1),
    ]
    
    backend_dir_ok = sum(check_dir(d, desc, files) for d, desc, files in backend_dirs)
    print()
    
    # Check frontend exists
    print("📂 FRONTEND STRUCTURE")
    print("-" * 80)
    frontend_ok = check_dir("frontend", "Frontend source", 1)
    print()
    
    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("-" * 80)
    
    total_ok = root_ok + backend_config_ok + backend_dir_ok + frontend_ok
    total_checks = len(root_checks) + len(backend_checks) + len(backend_dirs) + 1
    
    print(f"Checks passed: {total_ok}/{total_checks}")
    print()
    
    if total_ok == total_checks:
        print("✅ ALL CHECKS PASSED - Monorepo structure is complete!")
        print()
        print("🚀 Next steps:")
        print("   1. cp .env.example .env")
        print("   2. docker compose up --build")
        print("   3. docker compose exec backend alembic upgrade head")
        print("   4. docker compose exec backend python scripts/seed.py")
        return 0
    else:
        print(f"⚠️  {total_checks - total_ok} check(s) failed")
        print()
        print("❌ Backend copy appears incomplete.")
        print("   Run: python merge_backend.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
