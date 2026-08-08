# Pont Ratiss Prime Agent ↔ Open WebUI

Ce sous-projet expose Prime Agent comme un backend local compatible avec l’API OpenAI. Open WebUI reste la façade : il affiche le chat, les fichiers, l’historique et le panneau `Ratiss Linux Console`. Prime Agent garde la responsabilité du raisonnement, des skills et des outils.

## Démarrage

Depuis ce dossier :

```bash
npm start
```

Le pont écoute par défaut sur `http://127.0.0.1:8787`. Le binaire Prime Agent utilisé peut être remplacé avec `PRIME_AGENT_BIN=/chemin/vers/prime-agent`.

## Connexion dans Open WebUI

Dans les connexions OpenAI d’Open WebUI, ajouter :

- **URL de base** : `http://127.0.0.1:8787/v1`
- **Modèle** : `prime-agent-ratiss`
- **Clé API** : aucune clé locale n’est requise par le pont ; si Open WebUI exige une valeur, utiliser une valeur locale arbitraire et ne pas l’exposer sur Internet.

La console contextuelle se connecte à `http://127.0.0.1:8787/events`. Elle apparaît sur `agent_start` et pendant les événements d’outils, affiche les sorties Linux, puis se replie après `agent_end`.

## Limites actuelles

Le pont gère une tâche active à la fois afin de préserver l’ordre des événements RPC. L’authentification et l’exposition distante ne sont volontairement pas activées. Pour un déploiement multi-utilisateur, il faudra ajouter une authentification forte, une isolation de workspace et une file de sessions avant d’ouvrir le port hors de localhost.
