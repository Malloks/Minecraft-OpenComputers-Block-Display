from __future__ import annotations


def centered_runs(voxels: dict[tuple[int, int, int], int]) -> list[list[int]]:
    runs = []
    ox, oy, oz = 16, 8, 16
    for y in range(16):
        for z in range(16):
            x = 0
            while x < 16:
                value = voxels.get((x, y, z), 0)
                if value == 0:
                    x += 1
                    continue
                start = x
                while x < 16 and voxels.get((x, y, z), 0) == value:
                    x += 1
                runs.append([start + ox + 1, y + oy + 1, z + oz + 1, x - start, value])
    return runs


def write_holo(path, palette, voxels) -> None:
    runs = centered_runs(voxels)
    payload = ";".join(",".join(str(v) for v in run) for run in runs)
    chunks = [payload[i:i + 900] for i in range(0, len(payload), 900)]
    lines = ["return {", "  size={16,16,16},", "  offset={16,8,16},", "  palette={"]
    for r, g, b in palette:
        lines.append(f"    {{{r},{g},{b}}},")
    lines += ["  },", "  format=\"rle5-csv\",", "  data="]
    lines += [f"    \"{chunk}\" .." for chunk in chunks[:-1]]
    lines += [f"    \"{chunks[-1] if chunks else ''}\"", "}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
