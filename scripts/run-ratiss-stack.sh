#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRIDGE="$ROOT/integrations/prime-openwebui-bridge"
WEBUI="$ROOT/integrations/open-webui-webview"

cleanup() {
  [[ -n "${BRIDGE_PID:-}" ]] && kill "$BRIDGE_PID" 2>/dev/null || true
  [[ -n "${WEBUI_PID:-}" ]] && kill "$WEBUI_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$ROOT"
if ! command -v prime-agent >/dev/null 2>&1 && [[ -z "${PRIME_AGENT_BIN:-}" ]]; then
  echo "[INFO] prime-agent n'est pas dans le PATH ; définissez PRIME_AGENT_BIN avant d'envoyer une tâche."
fi

(cd "$BRIDGE" && node --experimental-strip-types src/server.ts) &
BRIDGE_PID=$!

(cd "$WEBUI" && VITE_RATISS_BRIDGE_URL="${VITE_RATISS_BRIDGE_URL:-http://127.0.0.1:8787}" npm run dev) &
WEBUI_PID=$!

echo "Ratiss bridge : http://127.0.0.1:8787"
echo "Open WebUI frontend : voir l'URL Vite affichée ci-dessous"
echo "Open WebUI doit être configuré avec http://127.0.0.1:8787/v1 comme endpoint OpenAI."
wait -n "$BRIDGE_PID" "$WEBUI_PID"
