"""Build versioned GitHub Release assets from one normalized source tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STAMP = (2024, 1, 1, 0, 0, 0)


def text_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def write_zip(path: Path, entries: dict[str, bytes]) -> None:
    # Stored entries avoid compressor differences between build platforms.
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, contents in sorted(entries.items()):
            info = zipfile.ZipInfo(name, STAMP)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, contents)


def resource_entries(root: Path) -> dict[str, bytes]:
    package = root / "petri_modeling_skills"
    paths = [package / "manifest.json", root / "LICENSE", root / "NOTICE"]
    paths += sorted((package / "skills").rglob("*.md"))
    paths += sorted((package / "schemas").rglob("*.json"))
    return {
        "petri-modeling-skills/" + (p.relative_to(package).as_posix() if p.is_relative_to(package) else p.name): text_bytes(p)
        for p in paths
    }


def build(root: Path, output: Path) -> dict:
    version = re.search(r'^version = "([^"]+)"$', (root / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE)[1]
    manifest = json.loads((root / "petri_modeling_skills/manifest.json").read_text(encoding="utf-8"))
    if version != manifest["version"]:
        raise ValueError("Project and resource manifest versions differ")
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary) / "source"
        for directory in ("petri_modeling_skills", "tests", "scripts"):
            for source in (root / directory).rglob("*"):
                if source.is_file() and source.suffix in {".py", ".md", ".json"}:
                    dest = stage / source.relative_to(root)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(text_bytes(source))
        for filename in ("pyproject.toml", "README.md", "LICENSE", "NOTICE"):
            (stage / filename).write_bytes(text_bytes(root / filename))
        subprocess.run(["uv", "build", str(stage), "--wheel", "--sdist", "--out-dir", str(output.resolve())],
                       check=True, env={**os.environ, "SOURCE_DATE_EPOCH": "1704067200"})
    wheel = output / f"petri_modeling_skills-{version}-py3-none-any.whl"
    with zipfile.ZipFile(wheel) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    write_zip(wheel, entries)
    resources = output / f"petri-modeling-skills-{version}-resources.zip"
    write_zip(resources, resource_entries(root))
    names = [wheel.name, resources.name, f"petri_modeling_skills-{version}.tar.gz"]
    files = []
    for name in names:
        path = output / name
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"name": name, "sha256": checksum, "size": path.stat().st_size})
    result = {"version": version, "files": files}
    (output / "release-assets.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (output / "SHA256SUMS.txt").write_text("".join(f"{f['sha256']}  {f['name']}\n" for f in files), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    print(json.dumps(build(ROOT, args.output), indent=2))
