from __future__ import annotations

import json
from pathlib import Path

from converter.exporter import write_holo
from converter.jar_reader import ModJar
from converter.model_resolver import ModelResolver
from converter.palette import quantize
from converter.texture_loader import TextureLoader
from converter.voxelizer import layers_text, voxelize


ROOT = Path(__file__).resolve().parent
MODS = ROOT / "Mods"
OUTPUT = ROOT / "output"
DEBUG = OUTPUT / "debug"


LINEUP = [
    {
        "slot": 1,
        "label": "dust",
        "jar": "exnihilocreatio",
        "model": "exnihilocreatio:block_dust",
        "output": "01_dust.holo",
    },
    {
        "slot": 2,
        "label": "4 slot drawer",
        "jar": "StorageDrawers",
        "model": "storagedrawers:basicdrawers_full4_oak",
        "output": "02_storage_drawer_4slot.holo",
    },
    {
        "slot": 3,
        "label": "creative cobble gen",
        "jar": "compacter",
        "model": "compacter:cobbler",
        "model_data": {
            "parent": "minecraft:block/cube_all",
            "textures": {"all": "compacter:blocks/cobbler"},
        },
        "output": "03_creative_cobble_gen.holo",
    },
    {
        "slot": 4,
        "label": "smeltery controller",
        "jar": "TConstruct",
        "model": "tconstruct:smeltery_controller",
        "output": "04_smeltery_controller.holo",
        "optional": True,
    },
    {
        "slot": 5,
        "label": "atomic reconstructor",
        "jar": "ActuallyAdditions",
        "model": "actuallyadditions:block_atomic_reconstructor",
        "output": "05_atomic_reconstructor.holo",
    },
    {
        "slot": 6,
        "label": "ember copper cell",
        "jar": "EmbersRekindled",
        "model": "embers:copper_cell",
        "output": "06_ember_copper_cell.holo",
    },
    {
        "slot": 7,
        "label": "factory layout woot",
        "jar": "woot",
        "model": "woot:layout",
        "output": "07_woot_factory_layout.holo",
    },
    {
        "slot": 8,
        "label": "nether star crux",
        "jar": "MysticalAgradditions",
        "model": "mysticalagradditions:nether_star_crop",
        "output": "08_nether_star_crux.holo",
    },
]


def find_jar(name_part: str) -> Path | None:
    needle = name_part.lower()
    for path in sorted(MODS.glob("*.jar")):
        if needle in path.name.lower():
            return path
    return None


def convert_one(entry: dict) -> bool:
    jar_path = find_jar(entry["jar"])
    if jar_path is None:
        print(f"skip {entry['slot']}: {entry['label']} - missing jar matching {entry['jar']}")
        return False

    jar = ModJar(jar_path)
    try:
        resolver = ModelResolver(jar)
        textures = TextureLoader(jar)
        if "model_data" in entry:
            resolved = resolver._resolve_model(entry["model_data"], [entry["model"]])
            resolved["resolved_from"] = [entry["model"], entry["model_data"].get("parent", "inline")]
            resolved["textures"] = {
                key: resolver.resolve_texture_ref(value, resolved["textures"])
                for key, value in resolved.get("textures", {}).items()
            }
        else:
            resolved = resolver.resolve(entry["model"])
        raw_voxels = voxelize(resolved, textures)
        palette, mapping = quantize(list(raw_voxels.values()), 3)
        indexed_voxels = {pos: mapping[color] for pos, color in raw_voxels.items()}

        out_path = OUTPUT / entry["output"]
        write_holo(out_path, palette, indexed_voxels)

        debug_prefix = f"{entry['slot']:02d}_{entry['label'].replace(' ', '_')}"
        (DEBUG / f"{debug_prefix}_resolved_model.json").write_text(
            json.dumps(resolved, indent=2),
            encoding="utf-8",
        )
        (DEBUG / f"{debug_prefix}_palette.json").write_text(
            json.dumps(palette, indent=2),
            encoding="utf-8",
        )
        (DEBUG / f"{debug_prefix}_voxel_layers.txt").write_text(
            layers_text(indexed_voxels),
            encoding="utf-8",
        )

        print(f"wrote {out_path.relative_to(ROOT)} from {jar_path.name}")
        return True
    finally:
        jar.close()


def main() -> None:
    OUTPUT.mkdir(exist_ok=True)
    DEBUG.mkdir(exist_ok=True)

    written = 0
    for entry in LINEUP:
        try:
            if convert_one(entry):
                written += 1
        except Exception as exc:
            print(f"failed {entry['slot']}: {entry['label']} - {exc}")

    print(f"done, wrote {written} model files")


if __name__ == "__main__":
    main()
