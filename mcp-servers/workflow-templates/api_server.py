#!/usr/bin/env python3
"""FastAPI server for n8n workflow templates."""

import json
import os
import sqlite3
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import re

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configuration
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "./data/workflows.db"))
TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", "./templates"))

# FastAPI app
app = FastAPI(
    title="n8n Workflow Templates API",
    description="Search and retrieve n8n workflow templates",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Models
class WorkflowTemplate(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    nodes_count: int
    services: List[str]
    trigger_type: Optional[str]
    complexity: str
    use_cases: List[str]
    
class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    trigger_type: Optional[str] = None
    limit: int = 20

class TemplateMetadata(BaseModel):
    id: str
    name: str
    description: str
    workflow_json: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    statistics: Dict[str, int]

# Database connection
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def load_categories_mapping():
    """Load category definitions from def_categories.json."""
    try:
        categories_file = Path("def_categories.json")
        if categories_file.exists():
            with open(categories_file, 'r', encoding='utf-8') as f:
                return json.loads(f.read())
    except Exception as e:
        print(f"Warning: Could not load def_categories.json: {e}")
    
    # Fallback to built-in categories
    return {
        "AI Agent Development": ["ai", "openai", "gpt", "llm", "anthropic", "claude", "langchain", "agent", "chatbot"],
        "Marketing & Advertising Automation": ["mailchimp", "hubspot", "sendgrid", "campaign", "marketing", "advertising"],
        "Technical Infrastructure & DevOps": ["github", "gitlab", "jenkins", "docker", "kubernetes", "aws", "devops"],
        "Communication & Messaging": ["slack", "email", "discord", "telegram", "teams", "sms", "communication"],
        "Cloud Storage & File Management": ["s3", "drive", "dropbox", "storage", "file", "backup"],
        "Project Management": ["notion", "airtable", "trello", "asana", "todoist", "project", "task"],
        "CRM & Sales": ["salesforce", "hubspot", "pipedrive", "crm", "sales", "customer"],
        "Data Processing & Analysis": ["database", "postgres", "mysql", "mongodb", "transform", "analytics"],
        "Financial & Accounting": ["stripe", "paypal", "quickbooks", "financial", "accounting", "payment"],
        "Web Scraping & Data Extraction": ["http", "webhook", "scraping", "extraction", "api", "rss"],
        "E-commerce & Retail": ["shopify", "woocommerce", "stripe", "square", "ecommerce", "retail"],
        "Business Process Automation": ["automation", "process", "workflow", "trigger", "schedule"],
        "Content Management & Publishing": ["wordpress", "ghost", "medium", "content", "publishing", "blog"],
        "Social Media Management": ["facebook", "twitter", "instagram", "linkedin", "social", "media"],
        "General": []
    }

def extract_services_from_nodes(nodes: List[Dict]) -> set:
    """Extract service names from node types with improved logic."""
    services = set()
    
    for node in nodes:
        node_type = node.get("type", "")
        
        # Handle different node type formats
        if "." in node_type:
            # Standard format: "n8n-nodes-base.slack" -> "Slack"
            service_part = node_type.split(".")[-1]
            
            # Clean up service name
            service = service_part.replace("-", " ").title()
            
            # Handle special cases
            if service.lower() == "httprequest":
                service = "HTTP Request"
            elif service.lower() == "webhook":
                service = "Webhook"
            elif "trigger" in service.lower() and service.lower() != "trigger":
                service = service.replace("Trigger", "").strip()
                
            services.add(service)
        elif node_type:
            # Direct node type
            services.add(node_type.title())
    
    return services

def detect_trigger_type(nodes: List[Dict]) -> str:
    """Detect trigger type with improved logic."""
    for node in nodes:
        node_type = node.get("type", "").lower()
        
        if "webhook" in node_type:
            return "webhook"
        elif "schedule" in node_type or "cron" in node_type:
            return "schedule"
        elif "trigger" in node_type:
            if "manual" in node_type:
                return "manual"
            elif "interval" in node_type:
                return "schedule"
            else:
                return "complex"
    
    return "manual"  # Default if no trigger found

def categorize_workflow(services: set, nodes: List[Dict], categories_mapping: Dict) -> str:
    """Categorize workflow using services and node analysis."""
    # Prepare text for analysis
    services_text = ' '.join([s.lower() for s in services])
    nodes_text = ' '.join([n.get("type", "").lower() for n in nodes])
    all_text = f"{services_text} {nodes_text}"
    
    # Score each category
    category_scores = {}
    
    for category, keywords in categories_mapping.items():
        if category == "General":
            continue
            
        score = 0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Direct service match gets higher score
            if keyword_lower in services_text:
                score += 10
            # Node type match gets medium score
            elif keyword_lower in nodes_text:
                score += 5
            # General text match gets lower score
            elif keyword_lower in all_text:
                score += 1
        
        if score > 0:
            category_scores[category] = score
    
    # Return highest scoring category or General
    if category_scores:
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    return "General"

def generate_intelligent_name(workflow_json: Dict, filename: str, services: set, trigger_type: str) -> str:
    """Generate intelligent workflow name following GitHub pattern."""
    # Try to get name from workflow JSON first
    name = workflow_json.get("name", "")
    if name and name.strip():
        return name.strip()
    
    # Parse filename if it follows the pattern: [ID]_[Service1]_[Service2]_[Purpose]_[Trigger].json
    filename_base = Path(filename).stem
    parts = filename_base.split('_')
    
    if len(parts) >= 3:
        # Remove ID (first part if it's numeric)
        if parts[0].isdigit():
            parts = parts[1:]
        
        # Join parts and clean up
        name_parts = []
        for part in parts:
            # Convert to title case and handle common abbreviations
            if part.lower() in ['api', 'ai', 'crm', 'sms', 'rss', 'http', 'aws']:
                name_parts.append(part.upper())
            else:
                name_parts.append(part.title())
        
        return ' '.join(name_parts)
    
    # Fallback: generate from services and trigger
    if services:
        service_list = list(services)[:2]  # Limit to 2 main services
        base_name = ' & '.join(service_list)
        
        if trigger_type and trigger_type != "manual":
            base_name += f" {trigger_type.title()} Automation"
        else:
            base_name += " Workflow"
        
        return base_name
    
    # Ultimate fallback
    return filename_base.replace('_', ' ').replace('-', ' ').title()

def extract_workflow_metadata(workflow_json: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Extract metadata from workflow JSON with improved logic."""
    nodes = workflow_json.get("nodes", [])
    
    # Load categories mapping
    categories_mapping = load_categories_mapping()
    
    # Extract services with improved logic
    services = extract_services_from_nodes(nodes)
    
    # Detect trigger type with improved logic
    trigger_type = detect_trigger_type(nodes)
    
    # Determine complexity based on node count and types
    node_count = len(nodes)
    has_code = any("code" in n.get("type", "").lower() for n in nodes)
    has_ai = any(any(keyword in str(n).lower() for keyword in ["ai", "openai", "gpt", "llm", "claude", "anthropic", "langchain"]) for n in nodes)
    has_webhook = trigger_type == "webhook"
    
    # Enhanced complexity classification
    if node_count > 15 or (has_ai and node_count > 5):
        complexity = "advanced"
    elif node_count > 8 or has_code or has_ai or (has_webhook and node_count > 3):
        complexity = "intermediate"
    else:
        complexity = "simple"
    
    # Generate intelligent name
    name = generate_intelligent_name(workflow_json, filename, services, trigger_type)
    
    # Generate enhanced description
    description = workflow_json.get("description", "")
    if not description:
        if services:
            service_list = list(services)[:3]
            if trigger_type == "webhook":
                description = f"Real-time automation connecting {', '.join(service_list)} via webhook triggers"
            elif trigger_type == "schedule":
                description = f"Scheduled automation workflow for {', '.join(service_list)} integration"
            else:
                description = f"Workflow automation connecting {', '.join(service_list)}"
            
            if has_ai:
                description += " with AI-powered processing"
    
    # Categorize workflow with improved logic
    category = categorize_workflow(services, nodes, categories_mapping)
    
    # Generate enhanced use cases
    use_cases = []
    if trigger_type == "webhook":
        use_cases.append("Real-time event processing")
    elif trigger_type == "schedule":
        use_cases.append("Automated recurring tasks")
    elif trigger_type == "complex":
        use_cases.append("Complex workflow automation")
    
    if has_ai:
        use_cases.append("AI-powered automation")
    if has_code:
        use_cases.append("Custom data transformation")
    if len(services) > 3:
        use_cases.append("Multi-service integration")
    if has_webhook and has_ai:
        use_cases.append("Intelligent real-time processing")
    
    return {
        "name": name,
        "description": description,
        "category": category,
        "nodes_count": node_count,
        "services": list(services),
        "trigger_type": trigger_type,
        "complexity": complexity,
        "use_cases": use_cases,
        "workflow_json": workflow_json
    }

# Initialize database
def init_database():
    """Initialize SQLite database with FTS5 for fast search."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                nodes_count INTEGER,
                services TEXT,
                trigger_type TEXT,
                complexity TEXT,
                use_cases TEXT,
                workflow_json TEXT,
                file_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE VIRTUAL TABLE IF NOT EXISTS workflows_fts USING fts5(
                id, name, description, services, use_cases,
                content=workflows
            );
            
            CREATE TRIGGER IF NOT EXISTS workflows_ai AFTER INSERT ON workflows BEGIN
                INSERT INTO workflows_fts(id, name, description, services, use_cases)
                VALUES (new.id, new.name, new.description, new.services, new.use_cases);
            END;
            
            CREATE TRIGGER IF NOT EXISTS workflows_au AFTER UPDATE ON workflows BEGIN
                UPDATE workflows_fts 
                SET name = new.name,
                    description = new.description,
                    services = new.services,
                    use_cases = new.use_cases
                WHERE id = new.id;
            END;
            
            CREATE INDEX IF NOT EXISTS idx_workflows_category ON workflows(category);
            CREATE INDEX IF NOT EXISTS idx_workflows_trigger ON workflows(trigger_type);
            CREATE INDEX IF NOT EXISTS idx_workflows_complexity ON workflows(complexity);
        """)

def populate_database(force_reindex=False):
    """Populate database with workflow templates from templates directory."""
    templates_dir = Path(os.getenv("TEMPLATES_DIR", "./templates"))
    
    if not templates_dir.exists():
        print(f"Creating templates directory: {templates_dir}")
        templates_dir.mkdir(parents=True, exist_ok=True)
        return
        
    json_files = list(templates_dir.glob("*.json"))
    print(f"Found {len(json_files)} workflow files")
    
    if not json_files:
        print("No workflow files found. Database remains empty.")
        return
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        imported = 0
        updated = 0
        skipped = 0
        
        for json_file in json_files:
            try:
                # Read file
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    workflow_json = json.loads(content)
                
                # Calculate file hash
                file_hash = hashlib.md5(content.encode()).hexdigest()
                
                # Generate ID from filename
                workflow_id = json_file.stem
                
                # Check if needs update
                cursor.execute("SELECT file_hash FROM workflows WHERE id = ?", (workflow_id,))
                existing = cursor.fetchone()
                
                if existing and existing[0] == file_hash and not force_reindex:
                    skipped += 1
                    continue
                
                # Extract metadata
                metadata = extract_workflow_metadata(workflow_json, str(json_file))
                
                # Prepare data
                data = (
                    workflow_id,
                    metadata["name"],
                    metadata["description"],
                    metadata["category"],
                    metadata["nodes_count"],
                    json.dumps(metadata["services"]),
                    metadata["trigger_type"],
                    metadata["complexity"],
                    json.dumps(metadata["use_cases"]),
                    json.dumps(workflow_json),
                    file_hash
                )
                
                if existing:
                    # Update existing
                    cursor.execute("""
                        UPDATE workflows 
                        SET name=?, description=?, category=?, nodes_count=?, 
                            services=?, trigger_type=?, complexity=?, use_cases=?,
                            workflow_json=?, file_hash=?, updated_at=CURRENT_TIMESTAMP
                        WHERE id=?
                    """, data[1:] + (workflow_id,))
                    updated += 1
                else:
                    # Insert new
                    cursor.execute("""
                        INSERT INTO workflows 
                        (id, name, description, category, nodes_count, services, 
                         trigger_type, complexity, use_cases, workflow_json, file_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, data)
                    imported += 1
                    
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
        
        conn.commit()
        
        # Print statistics
        cursor.execute("SELECT COUNT(*) FROM workflows")
        total = cursor.fetchone()[0]
        
        print(f"\nDatabase population complete:")
        print(f"  Total workflows: {total}")
        print(f"  Imported: {imported}")
        print(f"  Updated: {updated}")
        print(f"  Skipped: {skipped}")
        
        # Show category distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM workflows 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        print("\nCategories:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Show trigger type distribution
        cursor.execute("""
            SELECT trigger_type, COUNT(*) as count 
            FROM workflows 
            WHERE trigger_type IS NOT NULL
            GROUP BY trigger_type 
            ORDER BY count DESC
        """)
        
        print("\nTrigger Types:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        # Show complexity distribution
        cursor.execute("""
            SELECT complexity, COUNT(*) as count 
            FROM workflows 
            GROUP BY complexity 
            ORDER BY 
                CASE complexity 
                    WHEN 'simple' THEN 1 
                    WHEN 'intermediate' THEN 2 
                    WHEN 'advanced' THEN 3 
                END
        """)
        
        print("\nComplexity Distribution:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_database()
    # Auto-populate if database is empty
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM workflows")
        count = cursor.fetchone()[0]
        if count == 0:
            print("Database is empty, auto-populating...")
            populate_database()
    
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "database": DATABASE_PATH.exists()}

@app.post("/api/search", response_model=List[WorkflowTemplate])
async def search_templates(request: SearchRequest):
    """Search workflow templates with FTS5."""
    with get_db() as conn:
        # If no search query, return all with filters
        if not request.query or request.query.strip() == "":
            query_parts = ["SELECT * FROM workflows WHERE 1=1"]
            params = []
        else:
            # Build FTS5 search query
            query_parts = ["""
                SELECT w.* FROM workflows w
                JOIN workflows_fts fts ON w.id = fts.id
                WHERE workflows_fts MATCH ?
            """]
            params = [request.query]
        
        # Add filters
        if request.category:
            query_parts.append(" AND w.category = ?" if "w." in query_parts[0] else " AND category = ?")
            params.append(request.category)
        if request.trigger_type:
            query_parts.append(" AND w.trigger_type = ?" if "w." in query_parts[0] else " AND trigger_type = ?")
            params.append(request.trigger_type)
            
        # Add ordering and limit
        query_parts.append(" ORDER BY nodes_count DESC LIMIT ?")
        params.append(request.limit)
        
        # Execute query
        query = " ".join(query_parts)
        cursor = conn.execute(query, params)
        
        # Format results
        results = []
        for row in cursor:
            results.append(WorkflowTemplate(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                category=row["category"],
                nodes_count=row["nodes_count"],
                services=json.loads(row["services"]) if row["services"] else [],
                trigger_type=row["trigger_type"],
                complexity=row["complexity"],
                use_cases=json.loads(row["use_cases"]) if row["use_cases"] else []
            ))
            
        return results

@app.get("/api/template/{template_id}", response_model=TemplateMetadata)
async def get_template_metadata(template_id: str):
    """Get detailed metadata for a specific template."""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM workflows WHERE id = ?",
            (template_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Template not found")
            
        # Parse workflow JSON
        workflow_json = json.loads(row["workflow_json"])
        
        # Extract nodes and connections
        nodes = workflow_json.get("nodes", [])
        connections = workflow_json.get("connections", {})
        
        # Calculate statistics
        node_types = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
            
        return TemplateMetadata(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            workflow_json=workflow_json,
            nodes=nodes,
            connections=connections,
            statistics={
                "total_nodes": len(nodes),
                "connection_count": sum(len(c) for c in connections.values()),
                "unique_node_types": len(node_types),
                **node_types
            }
        )

@app.get("/api/categories")
async def list_categories():
    """List all available categories with counts."""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT category, COUNT(*) as count 
            FROM workflows 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        return {
            "categories": [
                {"name": row["category"], "count": row["count"]}
                for row in cursor
            ]
        }

@app.get("/api/triggers")
async def list_trigger_types():
    """List all trigger types with counts."""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT trigger_type, COUNT(*) as count 
            FROM workflows 
            WHERE trigger_type IS NOT NULL
            GROUP BY trigger_type 
            ORDER BY count DESC
        """)
        
        return {
            "triggers": [
                {"type": row["trigger_type"], "count": row["count"]}
                for row in cursor
            ]
        }

@app.get("/api/services")
async def list_services():
    """List all services/integrations with counts."""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT services 
            FROM workflows 
            WHERE services IS NOT NULL AND services != '[]'
        """)
        
        # Count services across all workflows
        service_counts = {}
        for row in cursor:
            try:
                services = json.loads(row["services"])
                for service in services:
                    service_counts[service] = service_counts.get(service, 0) + 1
            except:
                continue
        
        # Sort by count
        sorted_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "services": [
                {"name": service, "count": count}
                for service, count in sorted_services[:50]  # Top 50 services
            ],
            "total_unique_services": len(service_counts)
        }

@app.get("/api/stats")
async def get_database_stats():
    """Get comprehensive database statistics."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total workflows
        cursor.execute("SELECT COUNT(*) FROM workflows")
        total_workflows = cursor.fetchone()[0]
        
        # Category distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM workflows 
            GROUP BY category 
            ORDER BY count DESC
        """)
        categories = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Trigger distribution
        cursor.execute("""
            SELECT trigger_type, COUNT(*) as count 
            FROM workflows 
            WHERE trigger_type IS NOT NULL
            GROUP BY trigger_type 
            ORDER BY count DESC
        """)
        triggers = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Complexity distribution
        cursor.execute("""
            SELECT complexity, COUNT(*) as count 
            FROM workflows 
            GROUP BY complexity
        """)
        complexity = [{"level": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Average nodes per workflow
        cursor.execute("SELECT AVG(nodes_count) FROM workflows")
        result = cursor.fetchone()
        avg_nodes = round(result[0], 1) if result and result[0] else 0
        
        # Total nodes across all workflows
        cursor.execute("SELECT SUM(nodes_count) FROM workflows")
        total_nodes = cursor.fetchone()[0] or 0
        
        return {
            "total_workflows": total_workflows,
            "total_nodes": total_nodes,
            "average_nodes_per_workflow": avg_nodes,
            "categories": categories,
            "trigger_types": triggers,
            "complexity_distribution": complexity
        }

@app.get("/api/popular", response_model=List[WorkflowTemplate])
async def list_popular_templates(limit: int = Query(10, le=50)):
    """Get most popular templates based on complexity, AI features, and node count."""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM workflows 
            ORDER BY 
                CASE complexity 
                    WHEN 'advanced' THEN 3 
                    WHEN 'intermediate' THEN 2 
                    ELSE 1 
                END DESC,
                CASE 
                    WHEN workflow_json LIKE '%ai%' OR workflow_json LIKE '%openai%' OR workflow_json LIKE '%gpt%' THEN 1
                    ELSE 0
                END DESC,
                nodes_count DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor:
            results.append(WorkflowTemplate(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                category=row["category"],
                nodes_count=row["nodes_count"],
                services=json.loads(row["services"]) if row["services"] else [],
                trigger_type=row["trigger_type"],
                complexity=row["complexity"],
                use_cases=json.loads(row["use_cases"]) if row["use_cases"] else []
            ))
            
        return results

# Command line interface for database management
def cli():
    import argparse
    
    parser = argparse.ArgumentParser(description="n8n Workflow Templates API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--init-db", action="store_true", help="Initialize database only")
    parser.add_argument("--populate", action="store_true", help="Populate database with workflows")
    parser.add_argument("--force-reindex", action="store_true", help="Force reindex all workflows")
    parser.add_argument("--stats", action="store_true", help="Show database statistics only")
    
    args = parser.parse_args()
    
    if args.init_db:
        print("Initializing database...")
        init_database()
        print("Database initialized.")
        return
        
    if args.stats:
        print("Database statistics:")
        init_database()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM workflows")
            total = cursor.fetchone()[0]
            print(f"  Total workflows: {total}")
            
            cursor.execute("SELECT category, COUNT(*) FROM workflows GROUP BY category ORDER BY COUNT(*) DESC")
            print("  Categories:")
            for row in cursor.fetchall():
                print(f"    {row[0]}: {row[1]}")
        return
    
    if args.populate or args.force_reindex:
        print("Populating database...")
        init_database()
        populate_database(force_reindex=args.force_reindex)
        print("Database populated.")
        return
    
    # Start server
    uvicorn.run(
        "api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=os.getenv("LOG_LEVEL", "info")
    )

# Run server
if __name__ == "__main__":
    cli()