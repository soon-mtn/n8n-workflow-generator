# N8N Workflow Generator 🚀

**Système automatisé de génération de workflows n8n compatible avec Claude Code, Gemini CLI et Cursor AI grâce à 3 serveurs MCP spécialisés.**

## 🤖 Support Multi-Agent IA

Ce système fonctionne avec **3 agents IA** différents :
- 🎯 **Claude Code** - Configuration native optimisée
- ⚡ **Gemini CLI** - Support complet avec tous les outils MCP
- 🔧 **Cursor AI** - Intégration IDE pour développement

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
├── 🤖 Multi-Agent Support (Claude Code, Gemini CLI, Cursor AI)
│   ├── n8n-mcp (Official)          → 525+ nodes n8n documentés
│   ├── context7-mcp (Official)     → Documentation API temps réel
│   └── workflow-templates          → 2,057+ templates searchables
├── 🗄️ Base SQLite + FTS5           → Recherche < 50ms
├── 🐳 Docker Auto-Orchestration    → Réseau isolé + services
└── 📊 API REST FastAPI             → 7 endpoints + statistiques
```

## 🎯 Utilisation Multi-Agent

### **Avec Claude Code :**
```bash
# Claude Code utilise automatiquement les 3 serveurs MCP
claude code "Créer un workflow Telegram vers Slack avec IA"
# → Recherche dans 2,057+ templates + génération optimisée
```

### **Avec Gemini CLI :**
```bash
# Gemini CLI avec support MCP complet
gemini agent "Générer workflow automation business Slack+OpenAI"
# → Accès aux mêmes 525+ nodes + templates
```

### **Avec Cursor AI :**
```bash
# Dans Cursor IDE : Ctrl+Shift+I puis
"Créer workflow n8n pour automatisation email vers Discord"
# → Génération directe dans l'éditeur + validation
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

## 🔧 Configuration Multi-Agent (Auto-configurée)

Les 3 serveurs MCP sont automatiquement configurés pour chaque agent :

### **Structure de Configuration :**
```
n8n-workflow-generator/
├── .claude/
│   ├── settings.local.json      # Claude Code - Configuration MCP + schéma JSON
│   └── system-prompt.md         # Prompt système spécialisé Claude
├── .gemini/
│   ├── settings.json            # Gemini CLI - Support timeout + trust levels
│   └── system-prompt.md         # Prompt système spécialisé Gemini
├── .cursor/
│   ├── mcp.json                 # Cursor AI - Configuration MCP simplifiée
│   └── system-prompt.md         # Prompt système spécialisé Cursor
```

### **Serveurs MCP Partagés :**
- **n8n-mcp** → Documentation complète 525+ nodes n8n
- **context7** → APIs externes temps réel  
- **workflow-templates** → 2,057+ templates searchables

## 🛠️ Outils MCP Disponibles

### **N8N-MCP (30+ outils) - Serveur Officiel**

#### 📚 **Documentation & Découverte**
- `tools_documentation()` - Documentation de tous les outils MCP (**COMMENCEZ ICI !**)
- `get_node_documentation()` - Documentation parsée depuis n8n-docs
- `get_database_statistics()` - Métriques base de données et couverture
- `n8n_list_available_tools()` - Lister tous les outils de gestion disponibles

#### 🔍 **Recherche & Exploration**
- `list_nodes()` - Liste tous les nodes n8n avec options de filtrage
- `search_nodes()` - Recherche full-text dans toute la documentation
- `get_node_info()` - Informations complètes sur un node spécifique
- `get_node_essentials()` - Propriétés essentielles uniquement (10-20 vs 200+)
- `search_node_properties()` - Trouve des propriétés spécifiques dans les nodes
- `get_property_dependencies()` - Analyser conditions de visibilité des propriétés

#### 🤖 **Outils IA & Templates**
- `list_ai_tools()` - Liste tous les nodes compatibles IA (TOUT node peut être un outil IA !)
- `get_node_as_tool_info()` - Guide pour utiliser n'importe quel node comme outil IA
- `get_node_for_task()` - Configurations pré-définies pour tâches courantes
- `list_tasks()` - Découvrir les templates de tâches disponibles

#### ✅ **Validation & Qualité**
- `validate_node_operation()` - Validation complète des configurations node
- `validate_node_minimal()` - Validation rapide des champs requis uniquement
- `validate_workflow()` - Validation complète workflow + connexions IA
- `validate_workflow_connections()` - Vérifier structure et connexions IA
- `validate_workflow_expressions()` - Valider expressions n8n incluant $fromAI()
- `n8n_validate_workflow()` - Valider workflows existants dans n8n par ID (**NOUVEAU v2.6.3**)

#### 🛠️ **Gestion des Workflows**
- `n8n_create_workflow()` - Créer nouveaux workflows avec nodes et connexions
- `n8n_get_workflow()` - Récupérer workflow complet par ID
- `n8n_get_workflow_details()` - Workflow avec statistiques d'exécution
- `n8n_get_workflow_structure()` - Structure simplifiée du workflow
- `n8n_get_workflow_minimal()` - Info minimale (ID, nom, statut actif)
- `n8n_list_workflows()` - Lister workflows avec filtres et pagination
- `n8n_update_full_workflow()` - Mise à jour complète (remplacement total)
- `n8n_update_partial_workflow()` - Mise à jour via opérations diff (**NOUVEAU v2.7.0!**)
- `n8n_delete_workflow()` - Supprimer workflows définitivement

#### ⚡ **Exécutions & Déclenchement**
- `n8n_trigger_webhook_workflow()` - Déclencher workflows via URL webhook
- `n8n_get_execution()` - Détails d'exécution par ID
- `n8n_list_executions()` - Lister exécutions avec filtres de statut
- `n8n_delete_execution()` - Supprimer enregistrements d'exécution

#### 🏥 **Système & Diagnostic**
- `n8n_health_check()` - Vérifier connectivité API n8n et fonctionnalités
- `n8n_diagnostic()` - Diagnostic outils de gestion et configuration

### **Context7-MCP (2 outils) - Documentation Temps Réel**  
- `resolve_library_id()` - Résout IDs bibliothèques vers format Context7
- `get_library_docs()` - Documentation API à jour en temps réel

### **Workflow-Templates (4 outils) - Recherche Intelligente**
- `search_templates()` - Recherche FTS5 dans 2,057+ templates validés
- `get_template_metadata()` - Détails complets et métadonnées
- `list_categories()` - 13 catégories avec compteurs de templates
- `list_popular_templates()` - Top templates par complexité et usage

## 📁 Structure du Projet

```
n8n-workflow-generator/
├── .claude/                      # Configuration Claude Code
│   ├── settings.local.json      # MCP + schéma JSON + permissions
│   └── system-prompt.md         # Prompt expert spécialisé
├── .gemini/                      # Configuration Gemini CLI  
│   ├── settings.json            # MCP + timeout + trust
│   └── system-prompt.md         # Prompt expert spécialisé
├── .cursor/                      # Configuration Cursor AI
│   ├── mcp.json                 # MCP simple + clean
│   └── system-prompt.md         # Prompt expert spécialisé
├── mcp-servers/
│   └── workflow-templates/        # Serveur templates + API
│       ├── api_server.py         # API REST + MCP server
│       ├── def_categories.json   # 13 catégories automatiques
│       └── workflow_search_mcp.py # Serveur MCP Python
├── scripts/
│   ├── setup.sh                 # Installation complète multi-agent
│   ├── test-workflow.sh         # Tests fonctionnels
│   └── validate-config.js       # Validation toutes configs
├── workflows/templates/          # 2,057+ workflows JSON validés
└── docker-compose.yml           # Orchestration 4 services
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
# Pour Claude Code
claude mcp list

# Pour Gemini CLI  
gemini mcp status

# Pour Cursor AI
# Voir MCP Logs dans Output panel (Ctrl+Shift+U)
```

## 📈 Statistiques Système

Une fois démarré, accédez aux statistiques :
- **API Health** : http://localhost:8000/health
- **Catégories** : http://localhost:8000/api/categories  
- **Stats complètes** : http://localhost:8000/api/stats
