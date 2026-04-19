#!/bin/bash
# NOIR GATEWAY DEPLOYER v7.2
# ==========================

echo "🚀 Starting Noir Gateway Deployment to Cloudflare..."

# Pindah ke direktori gateway
cd noir-gateway

# Check if wrangler is installed
if ! command -v npx &> /dev/null
then
    echo "❌ Error: npx (npm) not found. Please install Node.js."
    exit 1
fi

# Deploying
echo "📡 Pushing to Cloudflare Workers..."
npx wrangler deploy

# Update Secrets from .env
echo "🔑 Synchronizing Secrets..."
# Membaca .env dan mengirimkan NOIR_API_KEY ke Cloudflare
if [ -f ../.env ]; then
    API_KEY=$(grep NOIR_API_KEY ../.env | cut -d '=' -f2)
    echo $API_KEY | npx wrangler secret put NOIR_API_KEY
else
    echo "⚠️ Warning: .env not found. Secrets not updated."
fi

echo "✅ Gateway Deployment Complete!"
