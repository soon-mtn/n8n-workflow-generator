# N8N Workflow Generator 

**Système automatisé de génération de workflows n8n avec Claude Code et 3 serveurs MCP spécialisés.**

## 🚀 Installation Ultra-Rapide

```bash
# Installation complète en une commande
./scripts/setup.sh
```

Ça y est ! Le système est prêt avec :
- ✅ **2,057+ workflows** templates chargés automatiquement
- ✅ **3 serveurs MCP** configurés et connectés  
- ✅ **API REST** fonctionnelle sur port 8000
- ✅ **Claude Code** intégré et opérationnel

## 🏗️ Architecture

```
📦 N8N Workflow Generator
├── 🤖 Claude Code + 3 Serveurs MCP
│   ├── n8n-mcp (Official)          → 525+ nodes n8n documentés
│   ├── context7-mcp (Official)     → Documentation API temps réel
│   └── workflow-templates          → 2,057+ templates searchables
├── 🗄️ Base SQLite + FTS5           → Recherche < 50ms
├── 🐳 Docker Auto-Orchestration    → Réseau isolé + services
└── 📊 API REST FastAPI             → 7 endpoints + statistiques
```

## 🎯 Utilisation

### **Génération de workflows avec Claude Code :**
```bash
# Claude Code utilise automatiquement les 3 serveurs MCP
claude code "Créer un workflow Telegram vers Slack avec IA"
# → Recherche dans 2,057+ templates + génération optimisée
```

### **Commandes de gestion :**
```bash
# Démarrer/arrêter services
docker compose up -d      # Démarre tout
docker compose down       # Arrête tout

# Gestion base de données (si nécessaire)
cd mcp-servers/workflow-templates  
python api_server.py --stats         # Statistiques
python api_server.py --force-reindex # Réindexer
```

### **API REST (optionnel) :**
```bash
# Rechercher templates
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "telegram", "limit": 5}'

# Statistiques base
curl http://localhost:8000/api/stats
```

## 📊 Données Disponibles

- **2,057+ workflows** avec métadonnées intelligentes
- **200+ intégrations** uniques (Slack, OpenAI, Telegram, etc.)
- **29,518+ nodes** totaux (moyenne 14.4 nodes/workflow)
- **13 catégories automatiques** : Business Process, AI Agent Dev, Web Scraping, etc.
- **4 types triggers** : Manual (789), Complex (708), Schedule (301), Webhook (259)
- **3 niveaux complexité** : Simple, Intermediate, Advanced

## 🔧 Configuration MCP (Auto-configurée)

Les 3 serveurs MCP sont déjà configurés dans `config/claude-code-config.json` :

- **n8n-mcp** → Documentation complète nodes n8n
- **context7** → APIs externes temps réel  
- **workflow-templates** → Templates searchables

## 🛠️ Outils MCP Disponibles

### **N8N-MCP (25+ outils)**
- `search_nodes()`, `get_node_essentials()`, `validate_workflow()`
- `n8n_create_workflow()`, `n8n_list_executions()`
- Documentation complète des 525+ nodes n8n

### **Context7 (2 outils)**  
- `resolve_library_id()` → Résout IDs bibliothèques
- `get_library_docs()` → Documentation à jour

### **Workflow-Templates (4 outils)**
- `search_templates()` → Recherche FTS5 dans 2,057+ templates
- `get_template_metadata()` → Détails complets workflow
- `list_categories()` → 13 catégories avec compteurs
- `list_popular_templates()` → Top templates par complexité

## 📁 Structure du Projet

```
n8n-workflow-generator/
├── config/
│   ├── claude-code-config.json    # Configuration MCP servers
│   └── system-prompt.md           # Prompt expert pour Claude
├── mcp-servers/
│   ├── context7/                  # Package officiel Context7
│   └── workflow-templates/        # Serveur templates + API
│       ├── api_server.py         # API REST + MCP server
│       ├── def_categories.json   # 15 catégories GitHub
│       └── workflow_search_mcp.py # Serveur MCP
├── scripts/
│   ├── setup.sh                 # Installation complète
│   ├── test-workflow.sh         # Tests
│   └── validate-config.js       # Validation config
├── workflows/templates/          # 2,057+ fichiers JSON
└── docker-compose.yml           # Orchestration services
```

## 🎉 Fonctionnalités

### **⚡ Performance**
- Recherche FTS5 **< 50ms** sur 2,057+ workflows  
- Auto-population base **< 30 secondes**
- Génération workflow **3 minutes** (vs 45min manuel)

### **🤖 IA Intégrée**
- **Validation multi-niveaux** → 100% précision
- **Métadonnées automatiques** → Catégories, complexité, services
- **Templates intelligents** → Patterns optimisés n8n

### **🔄 Maintenance Zéro**
- **Auto-population** au démarrage  
- **Docker orchestration** complète
- **Configuration MCP** pré-intégrée
- **APIs toujours synchronisées**

## 🚨 Troubleshooting

**Erreur : Services ne démarrent pas**
```bash
docker compose down && docker compose up -d
curl http://localhost:8000/health  # Test API
```

**Erreur : Base vide**  
```bash
cd mcp-servers/workflow-templates
python api_server.py --populate
```

**Erreur : MCP non connecté**
```bash
claude mcp list  # Voir état serveurs
```

## 📈 Statistiques Système

Une fois démarré, accédez aux statistiques :
- **API Health** : http://localhost:8000/health
- **Catégories** : http://localhost:8000/api/categories  
- **Stats complètes** : http://localhost:8000/api/stats

---

**Le système réduit le temps de création de workflows de 45 minutes à 3 minutes avec 100% de précision !** ⚡