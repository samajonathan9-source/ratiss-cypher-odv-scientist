# Ratiss × Open WebUI isolated webview

Cette copie conserve l’interface Svelte et les modules backend d’Open WebUI dans un sous-projet isolé. Aucun fichier du cœur de Prime Agent n’a été remplacé et ce sous-projet n’est pas ajouté aux workspaces `packages/*` de Prime Agent.

Le raccordement avec le cerveau Ratiss doit passer par une frontière d’adaptateur explicite : API ou processus séparé, variables d’environnement dédiées et validation des entrées. La zone `skills done touch` reste indépendante et protégée.

Sources :
- https://github.com/open-webui/open-webui
- https://github.com/PrimeIntellect-ai/prime-agent
- https://github.com/evinajonathan13-max/ratiss-scientist-agent
