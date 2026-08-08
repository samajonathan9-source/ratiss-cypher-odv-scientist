# Ratiss Cypher ODV Scientist — architecture d’intégration

Le dépôt conserve Prime Agent comme noyau principal. Le cerveau scientifique Ratiss se trouve dans `skills done touch/ratiss/` et sa consigne de protection dans `skills done touch/DO_NOT_TOUCH.md`. L’interface Open WebUI est greffée comme sous-projet autonome dans `integrations/open-webui-webview/`.

Cette organisation évite une fusion directe de runtimes incompatibles : Prime Agent reste un monorepo TypeScript/Node, tandis qu’Open WebUI conserve son frontend Svelte/Vite et son backend Python. Le raccordement futur doit utiliser un adaptateur contractuel et ne doit pas importer directement les dépendances Open WebUI dans les workspaces Prime.
