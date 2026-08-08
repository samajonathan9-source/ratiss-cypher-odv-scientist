#!/usr/bin/env python3
from __future__ import annotations

import json
import sys

from capabilities import list_files, manifest, read_file, web_get, write_file


def main() -> int:
    request = json.loads(sys.stdin.readline())
    action = request.get("action")
    if action == "list_files":
        result = list_files(str(request.get("path", ".")))
    elif action == "manifest":
        result = manifest(str(request.get("path", ".")))
    elif action == "read_file":
        result = read_file(str(request["path"]))
    elif action == "write_file":
        result = write_file(str(request["path"]), str(request.get("content", "")))
    elif action == "web_get":
        result = web_get(str(request["url"]), int(request.get("timeout", 20)))
    else:
        raise ValueError(f"Capacité inconnue : {action}")
    print(json.dumps({"ok": True, "action": action, "result": result}, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), flush=True)
        raise SystemExit(1)
