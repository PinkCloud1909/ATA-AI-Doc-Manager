#!/usr/bin/env python3
"""Merge atna-doc-backend into AI-Doc-Manager"""
import shutil
import os
from pathlib import Path

src = Path(r'C:\Users\ADMIN\Desktop\TKTL\atna-doc-backend')
dst = Path(r'C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager\backend')

# Create backend directory if not exists
dst.parent.mkdir(exist_ok=True)

# Define what to copy
ignore_patterns = shutil.ignore_patterns(
    '.git', '.git/*', '.pytest_cache', '__pycache__', 
    '*.pyc', '.venv', '.egg-info', '*.egg-info'
)

# Copy recursively
if dst.exists():
    print(f"Removing existing {dst}")
    shutil.rmtree(dst)

print(f"Copying {src} -> {dst}")
shutil.copytree(src, dst, ignore=ignore_patterns)

# List copied files
print("\n✓ Backend structure copied:")
for root, dirs, files in os.walk(dst):
    level = root.replace(str(dst), '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files[:3]:  # Show first 3 files per dir
        print(f'{subindent}{file}')
    if len(files) > 3:
        print(f'{subindent}... and {len(files)-3} more files')
    if level > 3:  # Limit depth
        dirs.clear()

print(f"\nTotal files: {sum(len(f) for _, _, f in os.walk(dst))}")
print("✓ Merge complete")
