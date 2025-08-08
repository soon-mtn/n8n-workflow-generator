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

### Setup and Development
```bash
# Complete setup (run once) - workflow database auto-populates on first startup
./scripts/setup.sh

# Start all services
docker compose up -d

# Stop services
docker compose down

# Test installation
./scripts/test-workflow.sh

# Validate configuration (run before development)
node scripts/validate-config.js

# Check service health
curl http://localhost:8000/health

# View logs (for debugging)
docker-compose logs -f [service-name]    # Specific service
docker-compose logs -f                   # All services

# Rebuild services (after code changes)
docker-compose build
docker-compose up -d
```

### MCP Server Management
```bash
# Check MCP server status
claude mcp list                    # View all server status
claude mcp get n8n-mcp            # Check n8n-mcp server details
claude mcp get context7           # Check context7 server
claude mcp get workflow-templates # Check template search server

# Test MCP connectivity
claude --help mcp                  # MCP command help
```

### Database Operations
```bash
# Template database management
cd mcp-servers/workflow-templates
python api_server.py --populate      # Populate database from templates
python api_server.py --force-reindex # Force complete reindex
python api_server.py --stats         # Show database statistics

# Manual database initialization (if needed)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -c "from api_server import init_database; init_database()"
```

### Troubleshooting
```bash
# If services fail to start
docker compose down
docker system prune -f              # Clean up containers
docker compose build --no-cache     # Rebuild from scratch
docker compose up -d

# If template API is not responding
curl http://localhost:8000/health    # Check API health
docker-compose logs workflow-templates-api  # Check logs

# If MCP servers are not connecting
docker network ls | grep n8n-automation     # Check network exists
docker compose ps                           # Check service status
```

## Configuration Files

### Multi-Agent Support
The system now supports **Claude Code**, **Gemini CLI**, and **Cursor AI** with dedicated configuration files:

- **`.claude/settings.local.json`**: Claude Code MCP configuration and settings
- **`.claude/system-prompt.md`**: Expert system prompt for Claude Code
- **`.gemini/settings.json`**: Gemini CLI MCP configuration and settings  
- **`.gemini/system-prompt.md`**: Expert system prompt for Gemini CLI
- **`.cursor/mcp.json`**: Cursor AI MCP server configuration
- **`.cursor/system-prompt.md`**: Expert system prompt for Cursor AI
- **`.env`**: Environment variables (N8N_API_URL, N8N_API_KEY, Redis credentials)
- **`.env.example`**: Template for environment variables with documentation
- **`docker-compose.yml`**: Multi-service orchestration with 4 services

## Service Architecture

### Service Dependencies
```
Claude Code
    ↓ (MCP connections)
┌─────────────────────────────────────────────────────────────────────┐
│ n8n-automation-network (Docker Network)                            │
├─────────────────┬─────────────────┬─────────────────┬──────────────┤
│   n8n-mcp       │  context7-mcp   │ workflow-       │ workflow-    │
│   (official)    │  (official)     │ templates-api   │ templates-   │
│                 │                 │ (FastAPI)       │ mcp          │
│                 │                 │     ↓           │ (Python)     │
│                 │                 │ SQLite + FTS5   │              │
└─────────────────┴─────────────────┴─────────────────┴──────────────┘
```

### Service Endpoints
- **Template API**: `http://localhost:8000/api/*`
  - `/api/search` - POST: Search templates with FTS5 full-text search
  - `/api/categories` - GET: List 13 categories with template counts
  - `/api/template/{id}` - GET: Get detailed template metadata
  - `/api/popular` - GET: Most popular templates by complexity
  - `/api/stats` - GET: Database statistics and system info
  - `/health` - GET: Health check endpoint

### MCP Server Endpoints
- **n8n-mcp**: Docker container with official n8n MCP server (35+ tools)
- **context7**: Node.js container with Context7 MCP server (2 tools)
- **workflow-templates-mcp**: Python container for template search (4 tools)

## Template Database Architecture

### Storage Structure
- **Location**: `./workflows/templates/` (2,057+ JSON files)
- **Database**: SQLite with FTS5 extension in Docker volume `workflow-data`
- **Indexing**: Automatic population on first API startup, <30 seconds
- **Search**: Sub-50ms FTS5 queries across all metadata

### Template Metadata Structure
Each template includes:
```json
{
  "id": "0001",
  "name": "Workflow Name",
  "nodes": [...],
  "connections": {...},
  "metadata": {
    "category": "AI Agent Development",
    "trigger_type": "webhook",
    "complexity": "Advanced",
    "services": ["telegram", "openai", "slack"],
    "node_count": 27,
    "use_cases": ["chatbot", "automation"]
  }
}
```

## Network Architecture

All services run on the `n8n-automation-network` Docker network to enable:
- **Inter-service communication** between MCP servers and template API
- **Network isolation** from host system
- **Container resolution** by service name
- **Port mapping** only for template API (8000:8000)

## Development Workflow Patterns

### Working with MCP Tools
Always start workflow generation with these tools in this order:
1. **Discovery**: 
   - `tools_documentation()` - Documentation des outils n8n-mcp uniquement (35+ outils)
   - `list_categories()` - Découvrir les 13 catégories de templates disponibles
   - Les outils context7 et workflow-templates n'ont pas de documentation centralisée
2. **Search**: Use `search_templates()` to find similar existing workflows
3. **Research**: Use `search_nodes()` and `get_node_essentials()` for required nodes
4. **Validation**: Use `validate_node_minimal()` then `validate_workflow()` before deployment

### Available MCP Tools by Server
**n8n-mcp (35+ outils)**: `tools_documentation()` covers all n8n-related tools
**context7 (2 outils)**: `resolve_library_id()`, `get_library_docs()`
**workflow-templates (4 outils)**: `search_templates()`, `get_template_metadata()`, `list_categories()`, `list_popular_templates()`

### Common Development Tasks

#### Adding New Templates
```bash
# 1. Add JSON files to workflows/templates/
# 2. Rebuild and restart template services
docker-compose build workflow-templates-api
docker-compose up -d workflow-templates-api
# 3. Force reindex if needed
cd mcp-servers/workflow-templates && python api_server.py --force-reindex
```

#### Debugging MCP Connection Issues
```bash
# 1. Check Docker network
docker network ls | grep n8n-automation
# 2. Test individual services
docker-compose ps
docker-compose logs n8n-mcp
docker-compose logs context7-mcp
docker-compose logs workflow-templates-mcp
# 3. Test MCP servers from Claude Code
claude mcp list
```

#### Testing Template Search
```bash
# Test API directly
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "telegram chatbot", "limit": 5}'

# Check database stats
curl http://localhost:8000/api/stats
```

### File Modification Guidelines

#### When editing docker-compose.yml:
- Always use `n8n-automation-network` for service communication
- Maintain volume mounts for data persistence
- Keep environment variables in `.env` file
- Use `stdin_open: true` and `tty: true` for MCP servers

#### When editing MCP configurations:
- Update `config/claude-code-config.json` for Claude Code integration
- Ensure Docker network names match between compose and config
- Test connectivity after changes with `claude mcp list`

#### When editing template processing:
- Templates must be valid n8n workflow JSON
- Metadata extraction happens in `mcp-servers/workflow-templates/api_server.py`
- Categories defined in `mcp-servers/workflow-templates/def_categories.json`

## Key Features

- **Incremental validation** saves 80-90% of tokens
- **Multi-level validation** ensures 100% accuracy  
- **Production-tested** with 2,057 validated templates
- **Real-time documentation** via context7 integration
- **Full-text search** with SQLite FTS5 for sub-50ms queries
- **Docker orchestration** with isolated network and persistent volumes