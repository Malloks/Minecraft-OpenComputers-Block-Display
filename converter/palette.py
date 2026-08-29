from __future__ import annotations


def quantize(colors: list[tuple[int, int, int]], k: int = 3) -> tuple[list[tuple[int, int, int]], dict[tuple[int, int, int], int]]:
    if not colors:
        return [(255, 255, 255)] * k, {}
    unique = sorted(set(colors))
    if len(unique) <= k:
        palette = unique + [unique[-1]] * (k - len(unique))
    else:
        seeds = [unique[0], unique[len(unique) // 2], unique[-1]][:k]
        centers = [tuple(map(float, c)) for c in seeds]
        for _ in range(12):
            buckets = [[] for _ in centers]
            for color in colors:
                idx = nearest(color, centers)
                buckets[idx].append(color)
            new_centers = []
            for old, bucket in zip(centers, buckets):
                if not bucket:
                    new_centers.append(old)
                else:
                    new_centers.append(tuple(sum(c[i] for c in bucket) / len(bucket) for i in range(3)))
            if new_centers == centers:
                break
            centers = new_centers
        palette = [tuple(int(round(v)) for v in c) for c in centers]
    palette = sorted(palette, key=lambda c: sum(c))
    mapping = {color: nearest(color, palette) + 1 for color in unique}
    return palette, mapping


def nearest(color: tuple[int, int, int], palette: list[tuple[float, float, float]]) -> int:
    return min(range(len(palette)), key=lambda i: sum((color[j] - palette[i][j]) ** 2 for j in range(3)))
