"""Orchestration contrôlée des modèles de planification et d'exécution Ratiss."""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelConfig:
    planner: str = os.getenv("RATISS_OPENROUTER_PLANNER", "nvidia/nemotron-3-ultra-550b-a55b:free")
    executor: str = os.getenv("RATISS_OPENROUTER_EXECUTOR", "nousresearch/hermes-3-llama-3.1-405b:free")
    endpoint: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
    timeout: int = int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "30"))


class OpenRouterOrchestrator:
    """Planifie puis exécute avec deux rôles distincts, sans divulguer les secrets."""

    def __init__(self, config: ModelConfig | None = None):
        self.config = config or ModelConfig()
        self.api_key = os.getenv("OPENROUTER_API_KEY")

    @staticmethod
    def _json_content(payload: dict[str, Any]) -> dict[str, Any]:
        content = payload.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        if "```" in content:
            content = content.split("```", 2)[1]
            content = content.removeprefix("json").strip()
        return json.loads(content)

    def _call(self, model: str, system: str, task: str) -> dict[str, Any]:
        if not self.api_key:
            return {"status": "fallback", "model": model, "task": task, "message": "OpenRouter indisponible : fallback local."}
        body = json.dumps({
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": task}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }).encode()
        req = urllib.request.Request(self.config.endpoint, data=body, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://127.0.0.1"),
            "X-Title": "Ratiss Prime Open WebUI",
        })
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                return {"status": "ok", "model": model, "output": self._json_content(json.loads(response.read()))}
        except Exception as exc:  # réseau externe non fiable : le pipeline reste local
            return {"status": "fallback", "model": model, "error": str(exc), "message": "Fallback local activé."}

    def plan(self, task: str) -> dict[str, Any]:
        return self._call(
            self.config.planner,
            "Tu es le planificateur Ratiss. Retourne uniquement du JSON avec domain, steps, tools, validation.",
            task,
        )

    def execute(self, task: str, plan: dict[str, Any]) -> dict[str, Any]:
        return self._call(
            self.config.executor,
            "Tu es l'exécuteur Ratiss. Retourne uniquement du JSON avec actions, observations, risks et final.",
            json.dumps({"task": task, "plan": plan}, ensure_ascii=False),
        )

    def run(self, task: str) -> dict[str, Any]:
        plan = self.plan(task)
        execution = self.execute(task, plan)
        return {"planner": plan, "executor": execution}
