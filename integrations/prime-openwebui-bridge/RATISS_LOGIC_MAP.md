# Cartographie logique Ratiss V9 Aeon Prime

## Rôle dans l’architecture unifiée

Ratiss est intégré comme couche scientifique et de validation derrière Prime Agent. Open WebUI ne doit pas réimplémenter ses solveurs ; il doit afficher leurs événements, résultats structurés et artefacts.

## Modules identifiés

| Module | Fonction | Exposition prévue |
|---|---|---|
| `ratiss_v9_aeon_prime/agentic_light.py` | Boucle REACT, outils scientifiques, routage Ollama puis OpenRouter/Nemotron, sortie JSON et historique d’itérations | Sous-agent Ratiss et événements de planification/exécution |
| `ratiss_v9_aeon_prime/backend_pur.py` | Noyau physique local : solveur t-J/Lanczos, homologie persistante, entropie de Shannon, MemoryGuard et reçu ZK simulé | Outil scientifique isolé ; sortie JSON validée |
| `ratiss_v9_aeon_prime/transdipl_y.py` | Routage disciplinaire vers quantique, biologie structurale, cryptographie ou matériaux ; activation du Panthéon cognitif | Étape de planification visible, sans exposer une chaîne de pensée privée |
| `agentic_scientist/connectors/universal_bridge.py` | Contrat de routage théorique vers des connecteurs externes | Adaptateur API contrôlé |
| `ecoute/` | Variante de pont/écoute à examiner avant activation | Ne pas lancer automatiquement |

## Flux logique retenu

1. Prime Agent reçoit la demande depuis le pont OpenAI-compatible.
2. `TransDIPLY.route_task` détecte le domaine et le solveur prévu.
3. `AgenticLight` produit un plan JSON et choisit un outil autorisé.
4. Le noyau `RATISSCorePhysics` exécute le calcul avec contrôle mémoire.
5. Les événements structurés sont diffusés vers `/events` pour la console Linux Open WebUI.
6. Le résultat est normalisé en JSON avec statut, physique, topologie, cryptographie et métadonnées.
7. Les artefacts sont enregistrés dans le workspace de session et présentés comme fichiers téléchargeables.

## Routage des modèles

Le code existant tente d’abord Ollama/Qwen local, puis Nemotron via OpenRouter. Le prompt maître demande une orchestration Nemotron pour la planification et Hermes pour l’exécution. Cette seconde voie doit donc être ajoutée comme configuration explicite et fallback, sans supprimer le mode local existant.

Les identifiants de modèles et les clés API ne doivent jamais être codés en dur. Ils proviennent de variables d’environnement, avec une valeur de secours locale déterministe uniquement pour les tests hors réseau.

## Validation et anti-hallucination

Le format de sortie doit rester JSON et inclure les résultats calculés, les invariants vérifiés, les erreurs, la provenance des appels et les fichiers produits. Le reçu ZK présent dans le noyau actuel est une attestation structurée simulée ; il ne doit pas être présenté comme une preuve RISC Zero réellement générée tant qu’un prover et une vérification indépendants ne sont pas branchés.

L’interface peut afficher les plans, décisions d’outil, observations, journaux et validations. Elle ne doit pas afficher une chaîne de pensée interne brute ; elle affiche un journal d’exécution scientifique vérifiable.

## Sécurité

Les appels HTTP, les connecteurs QPU/Bio/Pharma et les commandes Linux doivent être allowlistés, journalisés et exécutés dans un workspace isolé. Le pont reste lié à localhost par défaut. Les clés doivent être injectées à l’exécution et ne doivent jamais apparaître dans les logs ou les réponses.

## Fichiers manquants ou à vérifier

Le dépôt audité ne contient pas de fichier `zk_prover.py` à l’emplacement attendu par le prompt maître. Le raccordement ZK doit donc rester derrière une interface d’adaptateur jusqu’à identification d’un prover réel et de sa commande de vérification.
