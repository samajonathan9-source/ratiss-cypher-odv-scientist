# Contrat d’intégration Open WebUI × Prime Agent × Ratiss

## Rôle des composants

Open WebUI est la façade web principale : conversations, modèles, fichiers, historique, navigation et présentation des résultats. Prime Agent est le moteur agentique principal : raisonnement, sous-agents, skills, sessions persistantes, commandes et exécution des outils. Ratiss reste le cerveau scientifique spécialisé, conservé dans `skills done touch/ratiss/` et appelé uniquement par un adaptateur explicite.

## Flux principal

1. Open WebUI envoie une requête au pont local compatible OpenAI.
2. Le pont traduit le dernier message utilisateur en commande RPC `prompt` pour Prime Agent.
3. Les événements RPC sont convertis en flux SSE compatible OpenAI pour la réponse du chat.
4. Les événements `tool_execution_start`, `tool_execution_update` et `tool_execution_end` sont également diffusés sur un flux de télémétrie distinct destiné à la console Linux contextuelle.
5. Quand Prime Agent émet `agent_end`, la console passe en état replié et Open WebUI conserve le résultat dans le chat.

## Capacités web et fichiers

Le pont fournit un exécuteur JSON dans `src/capability_runner.py`. Les actions disponibles sont `web_get`, `list_files`, `manifest`, `read_file` et `write_file`. Les fichiers sont résolus sous `RATISS_WORKSPACE`, avec protection contre la traversée de chemin et une taille maximale configurable. Les requêtes web autorisent uniquement HTTP(S) et refusent les adresses loopback, privées, réservées et link-local. Les clés d’API ne sont jamais écrites dans le workspace ni dans les journaux.

L’accès web ne signifie pas une exécution aveugle des instructions trouvées sur une page. Le contenu distant est une donnée à analyser ; toute commande, écriture ou action sensible doit passer par une autorisation explicite et un outil local contrôlé.

## Sécurité

Le pont ne doit jamais exécuter directement une commande reçue du navigateur. Les commandes sont envoyées à Prime Agent, qui reste l’unique moteur d’exécution. L’accès réseau du pont doit être limité à la machine locale par défaut. Ratiss ne doit pas être exposé directement au navigateur.

## Contrat minimal

- `GET /health` : état du pont.
- `GET /v1/models` : modèle logique exposé à Open WebUI.
- `POST /v1/chat/completions` : conversation compatible OpenAI, avec support du streaming SSE.
- `GET /events` : événements de tâche pour la console contextuelle.
- `POST /control/abort` : demande d’arrêt du travail actif.

## États de la console

La console est masquée au repos, visible pendant `agent_start` et `tool_execution_*`, puis repliée après `agent_end` ou `abort`. Un utilisateur peut la rouvrir pour consulter les dernières sorties sans interrompre la conversation.
