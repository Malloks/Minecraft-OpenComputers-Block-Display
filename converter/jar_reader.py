from __future__ import annotations

import json
import zipfile
from pathlib import Path


class ModJar:
    def __init__(self, path: Path):
        self.path = path
        self.zip = zipfile.ZipFile(path)
        self.names = self.zip.namelist()

    def close(self) -> None:
        self.zip.close()

    def namespaces(self) -> list[str]:
        return sorted({p.split("/")[1] for p in self.names if p.startswith("assets/") and len(p.split("/")) > 2})

    def find_assets(self, kind: str, contains: str = "") -> list[str]:
        needle = contains.lower()
        return sorted(
            p for p in self.names
            if p.startswith("assets/") and f"/{kind}/" in p and (not needle or needle in p.lower())
        )

    def read_text(self, path: str) -> str:
        return self.zip.read(path).decode("utf-8-sig")

    def read_json(self, path: str) -> dict:
        return json.loads(self.read_text(path))

    def read_bytes(self, path: str) -> bytes:
        return self.zip.read(path)


def find_mod_jars(mods_dir: Path) -> list[ModJar]:
    return [ModJar(p) for p in sorted(mods_dir.glob("*.jar"))]
