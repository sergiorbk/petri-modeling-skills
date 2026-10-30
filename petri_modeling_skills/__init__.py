"""Read the shared modeling guides from installed package resources."""

from __future__ import annotations

import json
import re
from importlib.resources import files
from pathlib import PurePosixPath

_URI_PREFIX = "petri://skills/"


def _manifest() -> dict:
    return json.loads(files(__package__).joinpath("manifest.json").read_text(encoding="utf-8"))


__version__: str = _manifest()["version"]


def _entries() -> list[dict]:
    entries = _manifest()["resources"]
    seen: set[str] = set()
    for entry in entries:
        identifier = entry["id"]
        path = PurePosixPath(entry["path"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier) or identifier in seen:
            raise ValueError(f"Invalid or duplicate resource id: {identifier}")
        if path.is_absolute() or ".." in path.parts or "\\" in entry["path"]:
            raise ValueError(f"Invalid resource path: {entry['path']}")
        seen.add(identifier)
    return entries


def _document(entry: dict) -> tuple[dict[str, str], str]:
    resource = files(__package__).joinpath(*PurePosixPath(entry["path"]).parts)
    content = resource.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not content.startswith("---\n"):
        return {}, content.strip()
    header, separator, body = content[4:].partition("\n---\n")
    if not separator:
        raise ValueError(f"Unclosed skill frontmatter: {entry['id']}")
    metadata: dict[str, str] = {}
    for line in header.splitlines():
        key, colon, value = line.partition(":")
        if colon and key in {"name", "description"}:
            metadata[key] = value.strip()
    if not metadata.get("name") or not metadata.get("description"):
        raise ValueError(f"Skill metadata missing: {entry['id']}")
    return metadata, body.strip()


def catalog() -> list[dict[str, str]]:
    """List the allowlisted resources in their reading order."""
    result = []
    for entry in _entries():
        metadata, _ = _document(entry)
        result.append({
            "id": entry["id"],
            "name": metadata.get("name", entry.get("name", entry["id"])),
            "description": metadata.get("description", entry.get("description", "")),
            "uri": _URI_PREFIX + entry["id"],
        })
    return result


def read_skill(identifier: str) -> str:
    """Read a skill or reference by manifest id, without YAML frontmatter."""
    for entry in _entries():
        if entry["id"] == identifier:
            return _document(entry)[1]
    raise KeyError(f"Unknown modeling skill: {identifier}")


def read_resource(uri: str) -> str:
    """Read only exact canonical resource URIs; filesystem paths are not accepted."""
    if not uri.startswith(_URI_PREFIX):
        raise KeyError(f"Unknown modeling resource: {uri}")
    return read_skill(uri[len(_URI_PREFIX):])


def modeling_guidance() -> str:
    """Assemble the shared guide for a cached application system prompt."""
    return "\n\n".join(_document(entry)[1] for entry in _entries())
