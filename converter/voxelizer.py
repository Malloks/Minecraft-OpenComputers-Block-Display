from __future__ import annotations

from .texture_loader import TextureLoader


DIRECTIONS = {
    "north": (2, 0), "south": (2, 1), "west": (0, 0), "east": (0, 1), "down": (1, 0), "up": (1, 1),
}


def voxelize(model: dict, textures: TextureLoader) -> dict[tuple[int, int, int], tuple[int, int, int]]:
    voxels: dict[tuple[int, int, int], tuple[int, int, int]] = {}
    texmap = model.get("textures", {})
    for element in model.get("elements", []):
        frm = [int(round(v)) for v in element["from"]]
        to = [int(round(v)) for v in element["to"]]
        for face_name, face in element.get("faces", {}).items():
            tex_ref = face.get("texture", "")
            tex_key = tex_ref[1:] if tex_ref.startswith("#") else tex_ref
            real_tex = texmap.get(tex_key, tex_key)
            uv = face.get("uv") or default_uv(face_name, frm, to)
            paint_face(voxels, face_name, frm, to, uv, real_tex, textures)
    return voxels


def default_uv(face: str, frm: list[int], to: list[int]) -> list[float]:
    if face in ("north", "south"):
        return [frm[0], 16 - to[1], to[0], 16 - frm[1]]
    if face in ("west", "east"):
        return [frm[2], 16 - to[1], to[2], 16 - frm[1]]
    return [frm[0], frm[2], to[0], to[2]]


def paint_face(voxels, face, frm, to, uv, texture_ref, textures: TextureLoader) -> None:
    axis, high = DIRECTIONS[face]
    ranges = [range(frm[i], to[i]) for i in range(3)]
    fixed = to[axis] - 1 if high else frm[axis]
    a1, a2 = [i for i in range(3) if i != axis]
    for p1 in ranges[a1]:
        for p2 in ranges[a2]:
            pos = [0, 0, 0]
            pos[axis] = fixed
            pos[a1] = p1
            pos[a2] = p2
            s = (p1 - frm[a1] + 0.5) / max(1, to[a1] - frm[a1])
            t = (p2 - frm[a2] + 0.5) / max(1, to[a2] - frm[a2])
            if face in ("north", "south", "west", "east"):
                v = uv[1] + t * (uv[3] - uv[1])
                u = uv[0] + s * (uv[2] - uv[0])
            else:
                u = uv[0] + s * (uv[2] - uv[0])
                v = uv[1] + t * (uv[3] - uv[1])
            color = textures.sample(texture_ref, u, v)
            if color:
                voxels[tuple(pos)] = color


def layers_text(voxels: dict[tuple[int, int, int], int]) -> str:
    lines = []
    for y in reversed(range(16)):
        lines.append(f"y={y:02d}")
        for z in range(16):
            lines.append("".join(str(voxels.get((x, y, z), ".")) for x in range(16)))
        lines.append("")
    return "\n".join(lines)
