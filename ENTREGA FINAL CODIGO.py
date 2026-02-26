from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image


PNG_FILES = [Path(f"image{i}.png") for i in range(1, 9)]
TOP_N = 8

##EXERCICI 3
def gif_bits_per_pixel(num_colors: int) -> int:
    if num_colors <= 2:
        return 1
    if num_colors <= 4:
        return 2
    if num_colors <= 16:
        return 4
    return 8


def ensure_gif_exists(png_path: Path) -> Path:
    gif_path = png_path.with_suffix(".gif")
    if not gif_path.exists():
        with Image.open(png_path) as png:
            png.save(gif_path, format="GIF")
    return gif_path


def get_gif_stats(gif_path: Path) -> Dict:
    with Image.open(gif_path) as gif:
        if gif.mode != "P":
            gif = gif.convert("P")
        palette = gif.getpalette()
        counts = Counter(gif.getdata())
        used = sorted(counts.keys())
        colors = []
        for idx in used:
            rgb = tuple(palette[idx * 3: idx * 3 + 3])
            colors.append((rgb, counts[idx]))
        colors_sorted = sorted(colors, key=lambda x: (-x[1], x[0]))
        n_colors = len(used)
        bits = gif_bits_per_pixel(n_colors)
        return {
            "unique": n_colors,
            "bpp": bits / 8,
            "top": colors_sorted[:TOP_N],
            "bottom": colors_sorted[-TOP_N:] if len(colors_sorted) > TOP_N else [],
        }


def get_png_stats(png_path: Path) -> Dict:
    with Image.open(png_path) as png:
        rgb = png.convert("RGB")
        counts = Counter(rgb.getdata())
        items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        return {
            "unique": len(counts),
            "bpp": 3.0,
            "top": items[:TOP_N],
            "bottom": items[-TOP_N:] if len(items) > TOP_N else [],
        }


def collect_summaries(png_files: List[Path] = PNG_FILES) -> List[Tuple[Path, Path, Dict, Dict]]:
    summaries = []
    for png in png_files:
        if not png.exists():
            continue
        gif = ensure_gif_exists(png)
        gstats = get_gif_stats(gif)
        pstats = get_png_stats(png)
        summaries.append((png, gif, gstats, pstats))
    return summaries


def build_af_answers(summaries: List[Tuple[Path, Path, Dict, Dict]]) -> Dict[str, List[str]]:
    answers: Dict[str, List[str]] = {}

    answers["a"] = [f"{png.name} -> {gif.name} (fet)" for png, gif, _, _ in summaries]

    b_lines = []
    for _, gif, gstats, _ in summaries:
        b_lines.append(
            f"{gif.name}: {gstats['unique']} colors; "
            f"mes frequent {gstats['top'][0][0]} ({gstats['top'][0][1]} vegades)"
        )
    b_lines.append("Detall complet de la paleta al bloc de detall de l'informe.")
    answers["b"] = b_lines

    answers["c"] = [f"{gif.name}: {gstats['bpp']:.3f} B/px" for _, gif, gstats, _ in summaries]

    d_lines = []
    for png, _, _, pstats in summaries:
        d_lines.append(
            f"{png.name}: {pstats['unique']} colors; "
            f"mes frequent {pstats['top'][0][0]} ({pstats['top'][0][1]} vegades)"
        )
    d_lines.append("Llistat acotat: Top 8 i Bottom 8 colors per imatge.")
    answers["d"] = d_lines

    answers["e"] = [f"{png.name}: {pstats['bpp']:.3f} B/px" for png, _, _, pstats in summaries]

    answers["f"] = [
        "GIF: paleta indexada fins a 256 colors; en aquest conjunt surt 1.000 B/px.",
        "PNG RGB: mes colors i 3.000 B/px.",
        "Visualment, el GIF pot perdre suavitat en gradients/textures per quantitzacio.",
    ]

    return answers


if __name__ == "__main__":
    data = collect_summaries()
    af = build_af_answers(data)
    for letter in ("a", "b", "c", "d", "e", "f"):
        print(f"{letter})")
        for line in af[letter]:
            print(f"- {line}")
