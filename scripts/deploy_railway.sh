#!/usr/bin/env bash
# ==============================================================================
# Railway One-Click Redeployment Script
# Uploads and redeploys local code changes directly to Railway (no GitHub needed).
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

echo "======================================================="
echo " 🚀 Deploying Kewargen to Railway"
echo "======================================================="

# 1. Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Error: Railway CLI is not installed."
    echo "   Install it with: brew install railway"
    exit 1
fi

# 2. Check login status
echo "🔍 Checking authentication..."
if ! railway whoami &> /dev/null; then
    echo "⚠️  Not logged in to Railway. Running 'railway login'..."
    railway login
fi

# 3. Ensure service is linked
echo "🔗 Verifying service link..."
railway service link kewargen &> /dev/null || true

# 4. Parse optional deploy message
MSG="${1:-Deploying latest updates}"

# 5. Upload and deploy
echo "📦 Uploading and deploying project (Message: '$MSG')..."
railway up --message "$MSG"

echo ""
echo "======================================================="
echo " ✅ Deployment complete!"
echo " 🌐 Live URL: https://kewargen-production.up.railway.app"
echo " 📊 Dashboard: Run 'railway open' to view deployment details"
echo "======================================================="

