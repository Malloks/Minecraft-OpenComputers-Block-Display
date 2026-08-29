from __future__ import annotations

from copy import deepcopy

from .jar_reader import ModJar


VANILLA_MODELS = {
    "minecraft:block/block": {"textures": {}, "elements": []},
    "minecraft:block/cube": {
        "parent": "minecraft:block/block",
        "elements": [{
            "from": [0, 0, 0],
            "to": [16, 16, 16],
            "faces": {d: {"texture": f"#{d}", "cullface": d} for d in ("down", "up", "north", "south", "west", "east")},
        }],
    },
    "minecraft:block/cube_all": {
        "parent": "minecraft:block/cube",
        "textures": {d: "#all" for d in ("down", "up", "north", "south", "west", "east")},
    },
    "minecraft:block/orientable": {
        "parent": "minecraft:block/block",
        "elements": [{
            "from": [0, 0, 0],
            "to": [16, 16, 16],
            "faces": {
                "down": {"texture": "#down", "cullface": "down"},
                "up": {"texture": "#up", "cullface": "up"},
                "north": {"texture": "#front", "cullface": "north"},
                "south": {"texture": "#side", "cullface": "south"},
                "west": {"texture": "#side", "cullface": "west"},
                "east": {"texture": "#side", "cullface": "east"},
            },
        }],
    },
    "minecraft:block/cross": {
        "parent": "minecraft:block/block",
        "elements": [
            {
                "from": [0, 0, 8],
                "to": [16, 16, 8],
                "faces": {
                    "north": {"texture": "#cross", "uv": [0, 0, 16, 16]},
                    "south": {"texture": "#cross", "uv": [0, 0, 16, 16]},
                },
            },
            {
                "from": [8, 0, 0],
                "to": [8, 16, 16],
                "faces": {
                    "west": {"texture": "#cross", "uv": [0, 0, 16, 16]},
                    "east": {"texture": "#cross", "uv": [0, 0, 16, 16]},
                },
            },
        ],
    },
}


def normalize_model_ref(ref: str, default_ns: str = "minecraft") -> str:
    if ":" not in ref:
        ref = f"{default_ns}:{ref}"
    ns, name = ref.split(":", 1)
    if not name.startswith("block/"):
        name = f"block/{name}"
    return f"{ns}:{name}"


def model_path(ref: str) -> str:
    ns, name = normalize_model_ref(ref).split(":", 1)
    return f"assets/{ns}/models/{name}.json"


class ModelResolver:
    def __init__(self, jar: ModJar):
        self.jar = jar
        self.cache: dict[str, dict] = {}

    def load_model(self, ref: str) -> dict:
        key = normalize_model_ref(ref)
        if key in self.cache:
            return deepcopy(self.cache[key])
        if key in VANILLA_MODELS:
            model = deepcopy(VANILLA_MODELS[key])
        else:
            model = self.jar.read_json(model_path(key))
        self.cache[key] = deepcopy(model)
        return model

    def resolve(self, ref: str) -> dict:
        key = normalize_model_ref(ref)
        model = self.load_model(key)
        chain = [key]
        merged = self._resolve_model(model, chain)
        merged["resolved_from"] = chain
        merged["textures"] = {k: self.resolve_texture_ref(v, merged["textures"]) for k, v in merged.get("textures", {}).items()}
        return merged

    def _resolve_model(self, model: dict, chain: list[str]) -> dict:
        parent_ref = model.get("parent")
        if parent_ref:
            parent_key = normalize_model_ref(parent_ref)
            chain.append(parent_key)
            base = self._resolve_model(self.load_model(parent_key), chain)
        else:
            base = {"textures": {}, "elements": []}

        merged = deepcopy(base)
        merged.setdefault("textures", {}).update(model.get("textures", {}))
        if "elements" in model:
            merged["elements"] = deepcopy(model["elements"])
        for key, value in model.items():
            if key not in {"parent", "textures", "elements"}:
                merged[key] = deepcopy(value)
        return merged

    def resolve_texture_ref(self, value: str, textures: dict[str, str]) -> str:
        seen = set()
        while isinstance(value, str) and value.startswith("#"):
            key = value[1:]
            if key in seen:
                break
            seen.add(key)
            value = textures.get(key, value)
        return value
