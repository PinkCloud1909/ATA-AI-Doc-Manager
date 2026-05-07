#!/bin/bash
# Complete setup from scratch for local development

set -e  # Exit on error

ROOT_DIR="C:\Users\ADMIN\Desktop\TKTL\AI-Doc-Manager"
BACKEND_DIR="$ROOT_DIR\backend"

echo "🚀 AI Document Manager - Complete Setup"
echo "========================================"

# Step 1: Clean old database
echo ""
echo "📋 Step 1: Cleaning old database..."
if [ -f "$BACKEND_DIR\dms_backend.db" ]; then
    rm "$BACKEND_DIR\dms_backend.db"
    echo "✅ Old database removed"
fi

# Step 2: Create database schema
echo ""
echo "📋 Step 2: Creating database schema..."
cd "$BACKEND_DIR"
python setup_db.py

# Step 3: Seed default data
echo ""
echo "📋 Step 3: Seeding default roles and privileges..."
python -c "
from app.core.db import session_scope
from app.modules.iam.application.seed import seed_default_roles
with session_scope() as session:
    seed_default_roles(session)
    print('✅ Default roles and privileges seeded')
" 2>&1 || echo "⚠️  Seeding failed (might already be seeded)"

# Step 4: Start backend
echo ""
echo "📋 Step 4: Starting backend server..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
