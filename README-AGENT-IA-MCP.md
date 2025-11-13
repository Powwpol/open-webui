# 🤖 Agent IA avec MCP pour Pulsai

## 📦 Contenu du projet

Ce projet contient un workflow n8n complet pour créer un agent IA conversationnel avec support MCP (Model Context Protocol).

### Fichiers inclus

1. **workflows/agent-ia-mcp-pulsai.json** 
   - Workflow n8n prêt à l'import
   - Agent IA avec Ollama llama3.2
   - 3 outils intégrés (HTTP, Calculator, Code)
   - Interface de chat web

2. **AGENT-IA-MCP-GUIDE.md**
   - Guide complet d'utilisation
   - Instructions d'installation
   - Exemples d'usage
   - Dépannage et configuration avancée

3. **docker-compose.n8n.yaml**
   - Configuration Docker pour n8n classique et n8n-MCP
   - Ports exposés correctement
   - Services prêts à l'emploi

## 🚀 Démarrage Rapide

### Étape 1: Importer le workflow

```bash
# Dans n8n (http://localhost:5678)
1. Workflows > Import from File
2. Sélectionner: workflows/agent-ia-mcp-pulsai.json
3. Cliquer sur "Import"
```

### Étape 2: Activer le workflow

```bash
1. Ouvrir le workflow importé
2. Cliquer sur "Active" en haut à droite
```

### Étape 3: Utiliser le chat

```bash
1. Cliquer sur le node "Chat Trigger"
2. Cliquer sur "Open Chat" 
3. Commencer à discuter ! 💬
```

## ✨ Fonctionnalités

✅ **Chat conversationnel** avec interface web  
✅ **Modèle Ollama local** (llama3.2)  
✅ **Mémoire contextuelle** (10 derniers messages)  
✅ **Outils MCP**:
   - 🌐 Requêtes HTTP/API
   - 🧮 Calculatrice mathématique
   - 💻 Exécution de code JavaScript
   - 🔗 Appels serveurs MCP

## 📊 Architecture

```
Chat Interface → AI Agent → Ollama LLM
                     ↓
            ┌────────┼────────┐
            ▼        ▼        ▼
         HTTP    Calculator  Code
        Request              Tool
```

## 🔧 Prérequis

- ✅ n8n actif (port 5678)
- ✅ Ollama actif (port 11434)  
- ✅ Modèle llama3.2 installé
- ✅ Serveurs MCP (optionnel)

## 📖 Documentation

Consultez **AGENT-IA-MCP-GUIDE.md** pour:
- Instructions détaillées
- Configuration avancée
- Exemples d'utilisation
- Dépannage
- Extensions possibles

## 🐛 Problème d'authentification MCP ?

Si la création automatique via MCP échoue, utilisez l'**import manuel** du fichier JSON. C'est la méthode recommandée et la plus fiable.

## 💡 Exemples d'utilisation

### Calcul simple
```
Vous: Combien font 123 * 456 ?
Agent: Laisse-moi calculer ça... Résultat: 56088
```

### Transformation de données
```
Vous: Convertis ["hello", "world"] en majuscules avec du code
Agent: [Exécute du code JavaScript]
Résultat: ["HELLO", "WORLD"]
```

### Requête API
```
Vous: Appelle l'API JSONPlaceholder pour récupérer le post #1
Agent: [Fait une requête HTTP]
Résultat: Affiche les détails du post
```

## 🎯 Prochaines étapes

1. ✅ Importer et tester le workflow
2. 📝 Personnaliser le message système
3. 🔧 Ajouter vos propres outils
4. 🚀 Déployer en production

## 🆘 Support

- 📚 Consultez AGENT-IA-MCP-GUIDE.md
- 🔍 Vérifiez les logs n8n
- 🐳 Vérifiez les conteneurs Docker

---

**Version**: 1.0.0  
**Date**: 28 octobre 2025  
**Auteur**: Assistant IA Pulsai
