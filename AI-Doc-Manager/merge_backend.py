#!/usr/bin/env python3
"""
Merge script: Copy backend from atna-doc-backend into monorepo AI-Doc-Manager/backend/

Run this from the root directory:
    python merge_backend.py
"""

import shutil
import sys
from pathlib import Path

def main():
    src = Path("../atna-doc-backend")
    dst = Path("./backend")
    
    if not src.exists():
        print(f"❌ Source directory not found: {src.resolve()}")
        return 1
    
    print(f"📦 Merging backend from {src.resolve()}")
    print(f"   → to {dst.resolve()}\n")
    
    # Create backend directory
    dst.mkdir(exist_ok=True, parents=True)
    print(f"✓ Created {dst}")
    
    # Files and directories to copy
    items = [
        ("app", True),
        ("scripts", True),
        ("Dockerfile", False),
        ("pyproject.toml", False),
        ("alembic.ini", False),
        (".dockerignore", False),
        (".env.example", False),
        ("README.md", False),
    ]
    
    ignore_patterns = shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.pytest_cache', '.venv', '*.egg-info')
    
    for item, is_dir in items:
        src_path = src / item
        dst_path = dst / item
        
        if not src_path.exists():
            print(f"⚠ {item} not found in source")
            continue
        
        try:
            if is_dir:
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path, ignore=ignore_patterns)
                print(f"✓ Copied {item}/ (directory)")
            else:
                shutil.copy2(src_path, dst_path)
                print(f"✓ Copied {item}")
        except Exception as e:
            print(f"❌ Failed to copy {item}: {e}")
            return 1
    
    print(f"\n✅ Backend merge complete!")
    print(f"\n📂 Monorepo structure:")
    print(f"   backend/")
    print(f"   ├── app/")
    print(f"   ├── scripts/")
    print(f"   ├── Dockerfile")
    print(f"   ├── pyproject.toml")
    print(f"   ├── alembic.ini")
    print(f"   ├── .env.example")
    print(f"   ├── .dockerignore")
    print(f"   └── README.md")
    print(f"\n🚀 Next steps:")
    print(f"   1. Review docker-compose.yml - already configured")
    print(f"   2. Review .env.example - has frontend & backend vars")
    print(f"   3. Copy .env.example → .env and customize if needed")
    print(f"   4. Run: docker compose up --build")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
