#!/usr/bin/env python3
"""
Merge summary for AI-Doc-Manager repository.
Run this after manually copying backend/ from atna-doc-backend.
"""
import os
from pathlib import Path

def check_merge_status():
    """Check merge status and report."""
    root = Path(r'C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager')
    backend_path = root / 'backend'
    frontend_path = root / 'frontend'
    
    print("=" * 80)
    print("AI-Doc-Manager MERGE STATUS")
    print("=" * 80)
    
    # Check backend
    if backend_path.exists():
        app_path = backend_path / 'app'
        main_py = backend_path / 'app' / 'main.py'
        pyproject = backend_path / 'pyproject.toml'
        print(f"\n✓ Backend directory exists: {backend_path}")
        if main_py.exists():
            print(f"✓ app/main.py found")
        if pyproject.exists():
            print(f"✓ pyproject.toml found")
        # Count files
        file_count = sum(1 for _ in backend_path.rglob('*') if _.is_file())
        print(f"  Total files in backend: {file_count}")
    else:
        print(f"\n✗ Backend directory NOT found: {backend_path}")
        print("  Please copy atna-doc-backend to backend/ directory")
    
    # Check frontend
    if frontend_path.exists():
        package_json = frontend_path / 'package.json'
        print(f"\n✓ Frontend directory exists: {frontend_path}")
        if package_json.exists():
            print(f"✓ package.json found")
        file_count = sum(1 for _ in frontend_path.rglob('*') if _.is_file())
        print(f"  Total files in frontend: {file_count}")
    else:
        print(f"\n✗ Frontend directory NOT found")
    
    # Check root files
    print("\n✓ Root configuration files:")
    for fname in ['docker-compose.yml', '.env.example', 'README.md', '.gitignore', '.dockerignore']:
        fpath = root / fname
        if fpath.exists():
            print(f"  ✓ {fname}")
        else:
            print(f"  ✗ {fname} (missing)")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    if not backend_path.exists():
        print("""
1. Copy backend from atna-doc-backend:
   Option A (Windows PowerShell):
   Copy-Item -Path 'C:\\Users\\ADMIN\\Desktop\\TKTL\\atna-doc-backend' \\
     -Destination 'C:\\Users\\ADMIN\\Desktop\\TKTL\\AI-Doc-Manager\\backend' \\
     -Recurse -Exclude @('.git', '__pycache__', '*.pyc')

   Option B (cmd.exe):
   xcopy "C:\\Users\\ADMIN\\Desktop\\TKTL\\atna-doc-backend\\*" \\
     "C:\\Users\\ADMIN\\Desktop\\TKTL\\AI-Doc-Manager\\backend" /E /I /EXCLUDE:excludefile.txt

2. Then verify again:
   python _check_merge.py
""")
    else:
        print("""
1. Copy .env.example to .env:
   cp .env.example .env

2. Start the stack:
   docker compose up --build

3. Access services:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MinIO Console: http://localhost:9001
   - API Docs: http://localhost:8000/docs

4. Default credentials:
   - Username: admin
   - Password: admin123
""")
    print("=" * 80)

if __name__ == '__main__':
    check_merge_status()
