# Lolo Agents Team

Une équipe d'agents CrewAI spécialisés dans la prospection d'entreprises, l'analyse SOA et la recherche d'informations commerciales.

## 🚀 Agents Disponibles

### 1. **Biz Sniper** - Agent de Prospection d'Entreprises
- **Rôle** : Prospecteur d'entreprises françaises
- **Fonctionnalités** :
  - Recherche d'entreprises par secteur et localisation
  - Filtrage par taille d'effectif
  - Intégration MCP avec l'API recherche-entreprises
  - Génération de listes exploitables pour la prospection

### 2. **Fiche Prospection** - Agent de Recherche et Outreach
- **Rôle** : Créateur de fiches de prospection
- **Fonctionnalités** :
  - Recherche approfondie d'entreprises
  - Génération de messages d'outreach personnalisés
  - Création de rapports de prospection

### 3. **SOA Agent** - Agent d'Analyse SOA
- **Rôle** : Analyste d'architecture orientée services
- **Fonctionnalités** :
  - Analyse d'architectures SOA
  - Génération de rapports d'analyse
  - Recommandations d'amélioration

## 🛠️ Installation

### Prérequis
- Python 3.9+
- Node.js (pour les outils MCP)
- Git

### Installation des dépendances

```bash
# Cloner le dépôt
git clone https://github.com/Lofp34/lolo_agents_team.git
cd lolo_agents_team

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances Python
pip install -r requirements.txt

# Installer les dépendances Node.js pour MCP
cd biz_sniper
npm install
cd ..
```

## 🎯 Utilisation

### Biz Sniper - Recherche d'entreprises

```bash
cd biz_sniper
python3 crew_mcp_recherche.py
```

**Exemple de requête** :
```
"entreprises du secteur informatique sur Montpellier entre 20 et 250 collaborateurs"
```

### Fiche Prospection

```bash
cd fiche_prospection
python3 src/fiche_prospection/main.py
```

### SOA Agent

```bash
cd soa_agent
python3 src/soa_agent/main.py
```

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# API Keys (si nécessaire)
OPENAI_API_KEY=your_openai_api_key_here

# Configuration MCP
MCP_SERVER_TIMEOUT=60
```

### Configuration des agents

Chaque agent a ses propres fichiers de configuration :
- `config/agents.yaml` - Configuration des agents
- `config/tasks.yaml` - Configuration des tâches

## 🏗️ Architecture

```
lolo_agents_team/
├── biz_sniper/           # Agent de prospection d'entreprises
│   ├── src/
│   ├── mcp_adapter.py    # Adaptateur MCP personnalisé
│   └── crew_mcp_recherche.py
├── fiche_prospection/    # Agent de recherche et outreach
│   └── src/
├── soa_agent/           # Agent d'analyse SOA
│   └── src/
├── venv/                # Environnement virtuel Python
└── README.md
```

## 🔌 Intégration MCP

Le projet utilise le protocole MCP (Model Context Protocol) pour l'intégration avec des services externes :

- **Adaptateur MCP personnalisé** : `mcp_adapter.py` remplace `MCPServerAdapter` manquant
- **Serveur MCP** : `mcp-recherche-entreprises` pour la recherche d'entreprises françaises
- **Outils disponibles** :
  - `rechercher_entreprise` - Recherche générale d'entreprises
  - `rechercher_entreprise_geographiques` - Recherche géographique

## 📝 Exemples d'utilisation

### Recherche d'entreprises par secteur

```python
# Dans crew_mcp_recherche.py
result = crew.kickoff(inputs={
    "user_query": "entreprises du secteur informatique sur Montpellier entre 20 et 250 collaborateurs"
})
```

### Filtrage par effectif

L'agent gère automatiquement les tranches d'effectif SIRENE :
- `'12'` = 20-49 salariés
- `'21'` = 50-99 salariés  
- `'22'` = 100-199 salariés
- `'31'` = 200-249 salariés

## 🐛 Dépannage

### Problème d'import MCPServerAdapter

Si vous rencontrez l'erreur `ImportError: cannot import name 'MCPServerAdapter'`, le projet utilise un adaptateur MCP personnalisé dans `biz_sniper/mcp_adapter.py`.

### Problème de connexion MCP

Vérifiez que :
- Node.js est installé et accessible
- Le package `mcp-recherche-entreprises` est disponible via npx
- La connexion réseau fonctionne

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub ou contactez l'équipe de développement.

---

**Développé avec ❤️ par l'équipe Lolo Agents**
