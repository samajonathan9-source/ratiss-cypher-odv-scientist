"""Capacités web et fichiers pour Ratiss, limitées au workspace de session."""
from __future__ import annotations

import ipaddress
import json
import os
import socket
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(os.getenv("RATISS_WORKSPACE", "./workspace")).resolve()
MAX_READ_BYTES = int(os.getenv("RATISS_MAX_READ_BYTES", str(5 * 1024 * 1024)))


def _safe_path(relative: str) -> Path:
    candidate = (WORKSPACE_ROOT / relative).resolve()
    if candidate != WORKSPACE_ROOT and WORKSPACE_ROOT not in candidate.parents:
        raise ValueError("Chemin hors du workspace interdit")
    return candidate


def list_files(relative: str = ".") -> list[dict[str, Any]]:
    folder = _safe_path(relative)
    if not folder.is_dir():
        raise ValueError("Le chemin demandé n'est pas un dossier")
    return [{"name": item.name, "path": str(item.relative_to(WORKSPACE_ROOT)), "directory": item.is_dir(), "size": item.stat().st_size if item.is_file() else None} for item in sorted(folder.iterdir())]


def read_file(relative: str) -> str:
    path = _safe_path(relative)
    if not path.is_file():
        raise ValueError("Fichier introuvable")
    if path.stat().st_size > MAX_READ_BYTES:
        raise ValueError("Fichier trop volumineux pour une lecture directe")
    return path.read_text(encoding="utf-8", errors="replace")


def write_file(relative: str, content: str) -> dict[str, Any]:
    path = _safe_path(relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"path": str(path.relative_to(WORKSPACE_ROOT)), "size": path.stat().st_size}


def _public_host(hostname: str) -> bool:
    for info in socket.getaddrinfo(hostname, None):
        address = ipaddress.ip_address(info[4][0])
        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
            return False
    return True


def web_get(url: str, timeout: int = 20) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Seules les URLs HTTP(S) publiques sont autorisées")
    if not _public_host(parsed.hostname):
        raise ValueError("Accès aux hôtes privés ou locaux interdit")
    request = urllib.request.Request(url, headers={"User-Agent": "Ratiss-Cypher-ODV/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_READ_BYTES + 1)
        if len(body) > MAX_READ_BYTES:
            raise ValueError("Réponse web trop volumineuse")
        return {"url": url, "status": response.status, "content_type": response.headers.get("content-type", ""), "body": body.decode("utf-8", errors="replace")}


def manifest(relative: str = ".") -> str:
    return json.dumps({"workspace": str(WORKSPACE_ROOT), "files": list_files(relative)}, ensure_ascii=False, indent=2)
