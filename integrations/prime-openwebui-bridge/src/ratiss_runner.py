#!/usr/bin/env python3
"""Adaptateur de démonstration contrôlé pour le noyau Ratiss intégré."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RATISS = ROOT / "skills done touch" / "ratiss"
AGENTIC = RATISS / "agentic_scientist"
AEON = RATISS / "ratiss_v9_aeon_prime"
sys.path.insert(0, str(AGENTIC))
sys.path.insert(0, str(AEON))


def emit(event: str, **payload: object) -> None:
    print(json.dumps({"type": event, **payload}, ensure_ascii=False), flush=True)


def main() -> int:
    raw = sys.stdin.readline()
    if not raw:
        return 2
    request = json.loads(raw)
    task = str(request.get("task", ""))
    emit("ratiss_log", stream="ratiss", message="[RATISS] Initialisation du routeur scientifique")

    try:
        from transdipl_y import TransDIPLY
        route = TransDIPLY().route_task(task)
        emit("ratiss_route", route=route)
        emit(
            "ratiss_log",
            stream="ratiss",
            message=f"[RATISS] Domaine={route['detected_domain']} | solveur={route['solver']} | hardware={route['hardware']}",
        )

        if os.getenv("OPENROUTER_API_KEY"):
            from openrouter_orchestrator import OpenRouterOrchestrator
            emit("ratiss_log", stream="openrouter", message="[OPENROUTER] Planification Nemotron activée")
            orchestration = OpenRouterOrchestrator().run(task)
            emit("ratiss_openrouter", result=orchestration)
            emit("ratiss_log", stream="openrouter", message="[OPENROUTER] Exécution Hermes terminée")

        # Le pipeline local reste déterministe et sans appel externe par défaut.
        # Les connecteurs API ne sont activés que par une future allowlist explicite.
        from backend_pur import RATISSCorePhysics
        emit("ratiss_log", stream="ratiss", message="[RATISS] Contrôle MemoryGuard avant calcul")
        coordinates = [[i * 1.5, i * 2.1, (i % 3) * 0.9] for i in range(32)]
        result = RATISSCorePhysics().execute_complete_pipeline(coordinates, num_sites=8)
        emit("ratiss_result", result=result)
        workspace = Path(os.getenv("RATISS_WORKSPACE", "./workspace")).resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        artifact = workspace / f"ratiss_result_{int(time.time() * 1000)}.json"
        artifact.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        emit("ratiss_artifact", path=str(artifact), name=artifact.name, kind="json")
        emit(
            "ratiss_log",
            stream="ratiss",
            message=f"[RATISS] Pipeline terminé : status={result.get('status')} | ZK={result.get('cryptography', {}).get('verified', False)}",
        )
        return 0
    except Exception as exc:  # noqa: BLE001 - l’adaptateur doit retourner une erreur JSON
        emit("ratiss_error", error=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
