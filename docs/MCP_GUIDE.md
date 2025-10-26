# Pulsai MCP (Model Context Protocols) - Guide Complet

## 🎯 Vue d'ensemble

Le système MCP (Model Context Protocols) de Pulsai permet de connecter des serveurs de contexte externes qui fournissent des outils et des capacités supplémentaires aux modèles IA. Cette architecture flexible supporte plusieurs protocoles de communication.

## 📚 Table des matières

- [Protocoles supportés](#protocoles-supportés)
- [Configuration](#configuration)
- [Interface utilisateur](#interface-utilisateur)
- [Créer un serveur MCP personnalisé](#créer-un-serveur-mcp-personnalisé)
- [API REST](#api-rest)
- [Exemples](#exemples)
- [Dépannage](#dépannage)

---

## 🔌 Protocoles supportés

### 1. **stdio** - Standard I/O
Exécute un processus local qui communique via stdin/stdout.

**Cas d'usage :** Outils Python/Node.js locaux, scripts personnalisés

**Exemple de configuration :**
```yaml
- id: "python-tools"
  name: "Python Tools"
  protocol: "stdio"
  enabled: true
  config:
    command: ["python", "-m", "my_mcp_server"]
    env:
      PYTHONPATH: "/app/tools"
```

**Avantages :** Simple, pas de réseau, exécution locale  
**Inconvénients :** Processus enfant, gestion des dépendances

### 2. **HTTP/HTTPS** - REST API
Communique avec un serveur MCP via HTTP REST.

**Cas d'usage :** Serveurs distants, microservices, APIs externes

**Exemple de configuration :**
```yaml
- id: "remote-mcp"
  name: "Remote MCP Server"
  protocol: "http"
  enabled: true
  config:
    url: "https://mcp.example.com"
    auth_type: "bearer"
    token: "${MCP_TOKEN}"
```

**Avantages :** Scalable, déployable séparément, compatible avec load balancers  
**Inconvénients :** Latence réseau, nécessite gestion des tokens

### 3. **Docker** - Containers
Utilise un container Docker comme serveur MCP.

**Cas d'usage :** Isolation, déploiement reproductible, dépendances complexes

**Exemple de configuration :**
```yaml
- id: "docker-analyzer"
  name: "Code Analyzer (Docker)"
  protocol: "docker"
  enabled: true
  config:
    container_name: "pulsai-code-analyzer"
    port: 8100
```

**Avantages :** Isolation, gestion des dépendances, reproductibilité  
**Inconvénients :** Overhead Docker, gestion des volumes

### 4. **SSE** - Server-Sent Events
Stream en temps réel via Server-Sent Events.

**Cas d'usage :** Notifications temps réel, logs streaming, événements

**Exemple de configuration :**
```yaml
- id: "events-stream"
  name: "Event Stream MCP"
  protocol: "sse"
  enabled: true
  config:
    url: "https://mcp.example.com/events"
```

**Avantages :** Temps réel, push depuis serveur, simple  
**Inconvénients :** Unidirectionnel (serveur → client)

### 5. **WebSocket** - Communication bidirectionnelle
Communication temps réel bidirectionnelle.

**Cas d'usage :** Chat en temps réel, collaboration, jeux

**Exemple de configuration :**
```yaml
- id: "realtime-mcp"
  name: "Real-time MCP"
  protocol: "websocket"
  enabled: true
  config:
    url: "wss://mcp.example.com/ws"
```

**Avantages :** Bidirectionnel, faible latence, temps réel  
**Inconvénients :** Plus complexe, gestion des reconnexions

---

## ⚙️ Configuration

### Fichier YAML principal

Le fichier de configuration se trouve dans `config/mcp-servers.yaml` :

```yaml
servers:
  # Serveur MCP personnalisé Pulsai (stdio)
  - id: "pulsai-stdio-mcp"
    name: "Pulsai Local Stdio MCP"
    protocol: "stdio"
    enabled: true
    config:
      command: ["python", "mcp-server/pulsai_mcp/server.py", "--protocol", "stdio"]
  
  # Serveur HTTP externe
  - id: "external-http-mcp"
    name: "External HTTP MCP"
    protocol: "http"
    enabled: false
    config:
      url: "http://localhost:8100"
      auth_type: "bearer"
      token: "${MCP_EXTERNAL_TOKEN}"
  
  # Container Docker
  - id: "docker-mcp"
    name: "Dockerized MCP"
    protocol: "docker"
    enabled: false
    config:
      container_name: "my-mcp-container"
      port: 8102
```

### Variables d'environnement

Les variables d'environnement peuvent être utilisées dans la configuration :

```yaml
config:
  token: "${MCP_TOKEN}"           # Remplacé par la variable d'environnement
  api_key: "${MCP_API_KEY}"
  url: "${MCP_BASE_URL}"
```

### Hot-reload

La configuration est rechargée automatiquement toutes les 30 secondes. Vous pouvez aussi forcer un rechargement :

- **Via UI :** Cliquez sur "🔄 Recharger YAML" dans les paramètres MCP
- **Via API :** `POST /api/v1/mcp/reload`

---

## 🎨 Interface utilisateur

### Accès

Settings → Admin Settings → MCP Servers

### Fonctionnalités

#### 📋 Liste des serveurs
- Visualisation de tous les serveurs configurés
- Indicateurs de statut (activé/désactivé, santé)
- Actions rapides : Activer, Désactiver, Tester, Modifier, Supprimer

#### ➕ Ajouter un serveur
1. Cliquez sur "➕ Ajouter un serveur"
2. Choisissez un protocole
3. Remplissez les champs requis
4. Testez la connexion
5. Enregistrez

#### 🔍 Tester une connexion
- Vérifie que le serveur est accessible
- Affiche la latence (en ms)
- Retourne les erreurs détaillées

#### 🔧 Explorateur d'outils
- Visualise tous les outils disponibles de tous les serveurs
- Recherche par nom ou description
- Test interactif des outils avec formulaires générés dynamiquement
- Affichage des résultats en JSON formaté

---

## 🛠️ Créer un serveur MCP personnalisé

### Architecture

Un serveur MCP doit implémenter 3 endpoints principaux :

```
GET  /tools    → Liste des outils disponibles
GET  /models   → Liste des modèles (optionnel)
POST /message  → Exécute un outil ou traite un message
```

### Exemple : Serveur FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title="My Custom MCP Server")

class Tool(BaseModel):
    name: str
    description: str
    parameters: List[Dict[str, Any]]

class MCPMessage(BaseModel):
    type: str
    payload: Dict[str, Any]

@app.get("/tools", response_model=List[Tool])
async def get_tools():
    return [
        {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": [
                {
                    "name": "expression",
                    "type": "string",
                    "description": "Mathematical expression to evaluate",
                    "required": True
                }
            ]
        }
    ]

@app.post("/message")
async def handle_message(message: MCPMessage):
    if message.type == "tool_call":
        tool_name = message.payload.get("name")
        parameters = message.payload.get("parameters", {})
        
        if tool_name == "calculate":
            try:
                result = eval(parameters["expression"])
                return {"type": "tool_result", "payload": {"result": result}}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
    
    return {"type": "error", "payload": {"message": "Unsupported message type"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
```

### Serveur stdio (Python)

```python
import sys
import json
import asyncio

async def handle_message(message):
    if message["type"] == "get_tools":
        return {
            "type": "tools_list",
            "payload": {
                "tools": [
                    {
                        "name": "echo",
                        "description": "Echo back the input",
                        "parameters": [
                            {"name": "text", "type": "string", "required": True}
                        ]
                    }
                ]
            }
        }
    elif message["type"] == "tool_call":
        tool_name = message["payload"]["name"]
        if tool_name == "echo":
            return {
                "type": "tool_result",
                "payload": {"output": message["payload"]["parameters"]["text"]}
            }
    
    return {"type": "error", "payload": {"message": "Unknown command"}}

async def main():
    while True:
        line = await asyncio.to_thread(sys.stdin.readline)
        if not line:
            break
        
        try:
            message = json.loads(line)
            response = await handle_message(message)
            print(json.dumps(response), flush=True)
        except Exception as e:
            error_response = {"type": "error", "payload": {"message": str(e)}}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8100

CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8100"]
```

---

## 🌐 API REST

### Endpoints disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/v1/mcp/servers` | Liste tous les serveurs MCP |
| `GET` | `/api/v1/mcp/servers/{id}` | Détails d'un serveur |
| `POST` | `/api/v1/mcp/servers` | Ajouter un serveur |
| `PUT` | `/api/v1/mcp/servers/{id}` | Modifier un serveur |
| `DELETE` | `/api/v1/mcp/servers/{id}` | Supprimer un serveur |
| `POST` | `/api/v1/mcp/servers/{id}/test` | Tester la connexion |
| `POST` | `/api/v1/mcp/servers/{id}/enable` | Activer un serveur |
| `POST` | `/api/v1/mcp/servers/{id}/disable` | Désactiver un serveur |
| `GET` | `/api/v1/mcp/servers/{id}/tools` | Outils d'un serveur |
| `GET` | `/api/v1/mcp/tools` | Tous les outils (tous serveurs) |
| `POST` | `/api/v1/mcp/tools/execute` | Exécuter un outil |
| `POST` | `/api/v1/mcp/reload` | Recharger la configuration |

### Exemple d'utilisation (curl)

```bash
# Lister les serveurs
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/v1/mcp/servers

# Ajouter un serveur
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-mcp",
    "name": "My MCP Server",
    "protocol": "http",
    "config": {"url": "http://localhost:8100"},
    "enabled": true
  }' \
  http://localhost:8080/api/v1/mcp/servers

# Tester une connexion
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/api/v1/mcp/servers/my-mcp/test

# Exécuter un outil
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "my-mcp",
    "tool_name": "calculate",
    "parameters": {"expression": "2 + 2"}
  }' \
  http://localhost:8080/api/v1/mcp/tools/execute
```

---

## 📝 Exemples

### Serveur de calcul mathématique

```python
# math_mcp/server.py
from fastapi import FastAPI
import math

app = FastAPI()

@app.get("/tools")
def get_tools():
    return [
        {
            "name": "sqrt",
            "description": "Calculate square root",
            "parameters": [
                {"name": "number", "type": "number", "required": True}
            ]
        },
        {
            "name": "factorial",
            "description": "Calculate factorial",
            "parameters": [
                {"name": "n", "type": "integer", "required": True}
            ]
        }
    ]

@app.post("/message")
def handle_message(message: dict):
    tool = message["payload"]["name"]
    params = message["payload"]["parameters"]
    
    if tool == "sqrt":
        result = math.sqrt(params["number"])
    elif tool == "factorial":
        result = math.factorial(params["n"])
    else:
        return {"type": "error", "payload": {"message": "Unknown tool"}}
    
    return {"type": "tool_result", "payload": {"result": result}}
```

**Configuration :**
```yaml
- id: "math-mcp"
  name: "Mathematical Tools"
  protocol: "http"
  enabled: true
  config:
    url: "http://localhost:8100"
```

---

## 🔧 Dépannage

### Problème : Serveur non accessible

**Symptômes :** "Connection failed" lors du test

**Solutions :**
1. Vérifier que le serveur est démarré : `docker ps` ou `ps aux | grep mcp`
2. Vérifier l'URL et le port
3. Tester manuellement : `curl http://localhost:8100/tools`
4. Vérifier les logs du serveur MCP

### Problème : Outils non visibles

**Symptômes :** Le serveur est connecté mais l'explorateur d'outils est vide

**Solutions :**
1. Vérifier que le serveur est activé (enabled: true)
2. Tester l'endpoint `/tools` : `curl http://localhost:8100/tools`
3. Recharger la configuration : UI ou `POST /api/v1/mcp/reload`
4. Vérifier les logs Pulsai : `docker logs pulsai-backend`

### Problème : Erreur d'exécution d'outil

**Symptômes :** L'outil apparaît mais échoue à l'exécution

**Solutions :**
1. Vérifier les paramètres requis dans la définition de l'outil
2. Consulter les logs du serveur MCP
3. Tester l'outil directement via l'API du serveur MCP
4. Vérifier la validation des paramètres côté serveur

### Problème : stdio process died

**Symptômes :** "Process exited" dans les logs

**Solutions :**
1. Vérifier que la commande est correcte : `command: ["python", "server.py"]`
2. Tester manuellement : `python server.py`
3. Vérifier les dépendances Python (requirements.txt)
4. Consulter stderr du processus dans les logs

---

## 📚 Ressources

- [Spécification MCP](https://modelcontextprotocol.io)
- [Pulsai Custom MCP Server](../mcp-server/README.md)
- [Exemples de serveurs MCP](https://github.com/modelcontextprotocol/servers)
- [API Reference](./API_DOCUMENTATION.md)

---

## 🤝 Contribuer

Pour contribuer au système MCP de Pulsai :

1. Fork le repository
2. Créez un serveur MCP de démonstration
3. Ajoutez des tests
4. Soumettez une Pull Request

---

**Dernière mise à jour :** 19 octobre 2025  
**Version Pulsai :** 0.7.0

