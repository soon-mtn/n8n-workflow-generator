#!/bin/bash
set -e

echo "🚀 Setting up n8n Workflow Generator..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }

# Create directories
echo "📁 Creating directory structure..."
mkdir -p config mcp-servers/{context7,workflow-templates} scripts docs examples workflows/templates

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your n8n instance details"
fi

# Build Docker images
echo "🐳 Building Docker images..."
docker compose build

# Initialize workflow database (auto-population will occur on first API startup)
echo "📊 Workflow templates database will auto-populate on first startup..."

# Validate configuration
echo "✅ Validating configuration..."
node scripts/validate-config.js

# Start services
echo "🎯 Starting services..."
docker compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Health check
echo "🏥 Running health checks..."
curl -s http://localhost:8000/health || echo "⚠️  Template API not responding"

echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "1. Edit .env file with your n8n credentials"
echo "2. Configure Claude Code with config/claude-code-config.json"
echo "3. Test with: ./scripts/test-workflow.sh"
echo ""
echo "🚀 Ready to generate workflows!"