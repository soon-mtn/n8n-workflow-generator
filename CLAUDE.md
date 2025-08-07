# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **n8n Workflow Generator** - a complete system for automated n8n workflow generation using Claude Code and three specialized MCP servers. The system reduces workflow creation time from 45 minutes to 3 minutes with 100% accuracy through multi-level validation.

## Key Architecture Components

### MCP Servers (3 specialized servers)
1. **n8n-mcp**: Official n8n MCP server (Docker: `ghcr.io/czlonkowski/n8n-mcp:latest`)
2. **context7-mcp**: Real-time API documentation server (built from `./mcp-servers/context7/`)
3. **workflow-templates-api**: REST API for template search with SQLite + FTS5 (built from `./mcp-servers/workflow-templates/`)

### Data Sources
- **2,057 validated production templates** stored in SQLite with full-text search
- **525 documented n8n nodes** with 99% coverage
- **Real-time API documentation** via context7 integration

## Essential Commands

### Setup and Installation
```bash
# Complete setup (run once) - workflow database auto-populates on first startup
./scripts/setup.sh

# Start all services
docker compose up -d

# Stop services
docker compose down

# Test installation
./scripts/test-workflow.sh

# Manual database operations (if needed)
cd mcp-servers/workflow-templates
python api_server.py --populate      # Populate database
python api_server.py --force-reindex # Force complete reindex
python api_server.py --stats         # Show database statistics
```

### MCP Configuration
MCP servers are automatically configured with Claude Code:
```bash
# MCP servers configured:
# - n8n-mcp: ✓ Connected (official n8n integration)  
# - context7: Real-time API documentation
# - workflow-templates: Template search with API

# To reconfigure if needed:
claude mcp list                    # View server status
claude mcp get <server-name>       # Server details
```

### Required Environment Variables
```bash
# In .env (already configured):
N8N_API_URL=https://n8n.generateur-workflow-n8n.site
N8N_API_KEY=<your-api-key>
```

### Development Commands
```bash
# Validate configuration
node scripts/validate-config.js

# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f [service-name]

# Rebuild services
docker-compose build
```

### Database Operations
```bash
# Initialize template database
cd mcp-servers/workflow-templates
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from api_server import init_database; init_database()"
```

## Configuration Files

- **`config/claude-code-config.json`**: MCP server configuration for Claude Code
- **`.env`**: Environment variables (N8N_API_URL, N8N_API_KEY, etc.)
- **`docker-compose.yml`**: Multi-service orchestration

## Service Endpoints

- **Template API**: `http://localhost:8000/api/*`
  - `/api/search` - Search templates with FTS5
  - `/api/categories` - List categories with counts
  - `/api/template/{id}` - Get detailed metadata
  - `/api/popular` - Most popular templates

## Working with Templates

Templates are stored in `./workflows/templates/` and indexed in SQLite with full-text search capabilities. The system uses FTS5 for fast searching across:
- Template names and descriptions
- Service integrations
- Use cases and categories

## Network Architecture

All services run on the `n8n-automation-network` Docker network to enable inter-service communication while maintaining isolation.

## Key Features

- **Incremental validation** saves 80-90% of tokens
- **Multi-level validation** ensures 100% accuracy
- **Production-tested** with 2,057 validated templates
- **Real-time documentation** via context7 integration