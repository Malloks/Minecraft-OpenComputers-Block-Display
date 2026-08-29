from __future__ import annotations

from io import BytesIO

from PIL import Image

from .jar_reader import ModJar


class TextureLoader:
    def __init__(self, jar: ModJar):
        self.jar = jar
        self.cache: dict[str, Image.Image] = {}

    def load(self, ref: str) -> Image.Image:
        if ref not in self.cache:
            ns, name = ref.split(":", 1) if ":" in ref else ("minecraft", ref)
            path = f"assets/{ns}/textures/{name}.png"
            self.cache[ref] = Image.open(BytesIO(self.jar.read_bytes(path))).convert("RGBA")
        return self.cache[ref]

    def sample(self, ref: str, u: float, v: float) -> tuple[int, int, int] | None:
        img = self.load(ref)
        w, h = img.size
        x = max(0, min(w - 1, int(u / 16.0 * w)))
        y = max(0, min(h - 1, int(v / 16.0 * h)))
        r, g, b, a = img.getpixel((x, y))
        if a < 16:
            return None
        return (r, g, b)
