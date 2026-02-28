#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

import metrikz


def parse_qualities(raw):
    values = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        value = int(token)
        if value < 1 or value > 100:
            raise ValueError("Quality values must be in [1, 100]")
        values.append(value)
    if not values:
        raise ValueError("At least one quality value is required")
    return sorted(set(values))


def luminance_entropy(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
    prob = hist / max(hist.sum(), 1.0)
    prob = prob[prob > 0]
    return float(-(prob * np.log2(prob)).sum())


def laplacian_variance(image_bgr):
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(lap.var())


def chroma_variance(image_bgr):
    ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb).astype(np.float64)
    cr_var = ycrcb[:, :, 1].var()
    cb_var = ycrcb[:, :, 2].var()
    return float((cr_var + cb_var) / 2.0)


def nearest_quality(target, available):
    return min(available, key=lambda q: (abs(q - target), q))


def compression_region_comment(original_bgr, target_bgr):
    gray_orig = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    gray_target = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    abs_err = np.abs(gray_orig - gray_target)

    lap = np.abs(cv2.Laplacian(gray_orig, cv2.CV_64F))
    threshold = np.percentile(lap, 75)
    edge_mask = lap >= threshold
    smooth_mask = ~edge_mask

    edge_mean = float(abs_err[edge_mask].mean()) if np.any(edge_mask) else 0.0
    smooth_mean = float(abs_err[smooth_mask].mean()) if np.any(smooth_mask) else 0.0

    ratio = edge_mean / max(smooth_mean, 1e-9)
    if ratio > 1.15:
        region_text = "L'error es concentra sobretot en vores i textures fines."
    elif ratio < 0.87:
        region_text = "L'error apareix més en transicions suaus i degradats."
    else:
        region_text = "L'error està relativament repartit entre vores i zones suaus."
    return region_text, edge_mean, smooth_mean


def top_error_blocks(original_bgr, target_bgr, block_size=32, top_k=3):
    diff = np.abs(
        original_bgr.astype(np.float64) - target_bgr.astype(np.float64)
    ).mean(axis=2)
    h, w = diff.shape
    blocks = []
    for y in range(0, h - block_size + 1, block_size):
        for x in range(0, w - block_size + 1, block_size):
            score = float(diff[y : y + block_size, x : x + block_size].mean())
            blocks.append((score, x, y))
    blocks.sort(reverse=True, key=lambda t: t[0])
    return blocks[:top_k]


def build_visual_error(original_bgr, target_bgr, output_path):
    gray_orig = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    gray_target = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    abs_err = np.abs(gray_orig - gray_target)
    if abs_err.max() > 0:
        heatmap = (abs_err / abs_err.max() * 255.0).astype(np.uint8)
    else:
        heatmap = np.zeros_like(abs_err, dtype=np.uint8)
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_INFERNO)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    orig_rgb = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2RGB)
    target_rgb = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2RGB)

    blocks = top_error_blocks(original_bgr, target_bgr, block_size=32, top_k=3)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.ravel()

    axes[0].imshow(orig_rgb)
    axes[0].set_title("Original")
    axes[0].axis("off")

    axes[1].imshow(target_rgb)
    axes[1].set_title("JPEG")
    axes[1].axis("off")

    axes[2].imshow(heatmap)
    axes[2].set_title("Mapa d'error absolut")
    axes[2].axis("off")

    for i in range(3):
        ax = axes[3 + i]
        if i < len(blocks):
            score, x, y = blocks[i]
            c1 = orig_rgb[y : y + 32, x : x + 32]
            c2 = target_rgb[y : y + 32, x : x + 32]
            pair = np.concatenate([c1, c2], axis=1)
            ax.imshow(pair)
            ax.set_title(f"Crop {i + 1} (x={x}, y={y}, err={score:.2f})")
        else:
            ax.imshow(np.zeros((32, 64, 3), dtype=np.uint8))
            ax.set_title(f"Crop {i + 1}")
        ax.axis("off")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_curves(records, output_path, y_key, y_label, title):
    by_image = defaultdict(list)
    for rec in records:
        by_image[rec["image"]].append(rec)

    markers = ["o", "s", "^", "D", "v", "X", "P", "*", "h", "<", ">"]
    plt.figure(figsize=(10, 6))
    for idx, image_name in enumerate(sorted(by_image.keys())):
        rows = sorted(by_image[image_name], key=lambda r: r["quality"])
        x = [r["quality"] for r in rows]
        y = [r[y_key] for r in rows]
        plt.plot(
            x,
            y,
            marker=markers[idx % len(markers)],
            linewidth=1.8,
            markersize=5,
            label=image_name,
        )
    plt.xlabel("Quality")
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="Anàlisi de compressió JPEG: MSE i ratio de compressió."
    )
    parser.add_argument("--input-dir", default="Codi_Imatges")
    parser.add_argument("--output-dir", default="Codi_Imatges/results_jpeg")
    parser.add_argument("--qualities", default="1,10,20,30,40,50,60,70,80,90,100")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    qualities = parse_qualities(args.qualities)

    png_paths = sorted(input_dir.glob("*.png"))
    if not png_paths:
        raise RuntimeError(f"No PNG files found in: {input_dir}")

    jpeg_root = output_dir / "jpeg"
    visual_root = output_dir / "visual_error"
    output_dir.mkdir(parents=True, exist_ok=True)
    jpeg_root.mkdir(parents=True, exist_ok=True)
    visual_root.mkdir(parents=True, exist_ok=True)
    for old_plot in visual_root.glob("*.png"):
        old_plot.unlink()

    records = []
    image_info = {}
    loaded_images = {}

    for png_path in png_paths:
        image_name = png_path.stem
        original = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
        if original is None:
            print(f"[WARN] Could not read image: {png_path}")
            continue

        loaded_images[image_name] = original
        image_info[image_name] = {
            "entropy": luminance_entropy(original),
            "lap_var": laplacian_variance(original),
            "chroma_var": chroma_variance(original),
            "png_size": png_path.stat().st_size,
        }

        image_jpeg_dir = jpeg_root / image_name
        image_jpeg_dir.mkdir(parents=True, exist_ok=True)

        for quality in qualities:
            jpg_path = image_jpeg_dir / f"q{quality}.jpg"
            ok = cv2.imwrite(
                str(jpg_path), original, [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
            )
            if not ok:
                print(f"[WARN] Could not write JPEG: {jpg_path}")
                continue

            target = cv2.imread(str(jpg_path), cv2.IMREAD_COLOR)
            if target is None:
                print(f"[WARN] Could not read JPEG after write: {jpg_path}")
                continue

            png_size = image_info[image_name]["png_size"]
            jpg_size = jpg_path.stat().st_size
            if jpg_size <= 0:
                print(f"[WARN] JPEG size is zero: {jpg_path}")
                continue

            mse_value = float(metrikz.mse(original, target))
            ratio = float(png_size / jpg_size)

            records.append(
                {
                    "image": image_name,
                    "quality": int(quality),
                    "mse": mse_value,
                    "compression_ratio": ratio,
                    "png_size_bytes": int(png_size),
                    "jpg_size_bytes": int(jpg_size),
                }
            )

    if not records:
        raise RuntimeError("No valid records generated.")

    by_image = defaultdict(list)
    for rec in records:
        by_image[rec["image"]].append(rec)

    best_quality = {}
    for image_name, rows in by_image.items():
        mse_vals = np.array([r["mse"] for r in rows], dtype=np.float64)
        cr_vals = np.array([r["compression_ratio"] for r in rows], dtype=np.float64)
        min_mse, max_mse = float(mse_vals.min()), float(mse_vals.max())
        min_cr, max_cr = float(cr_vals.min()), float(cr_vals.max())
        eps = 1e-12

        for r in rows:
            mse_norm = (r["mse"] - min_mse) / (max_mse - min_mse + eps)
            cr_norm = (r["compression_ratio"] - min_cr) / (max_cr - min_cr + eps)
            r["score"] = float(0.6 * mse_norm + 0.4 * (1.0 - cr_norm))

        best = min(rows, key=lambda r: (r["score"], -r["quality"]))
        best_quality[image_name] = int(best["quality"])

    csv_path = output_dir / "metrics.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image",
                "quality",
                "mse",
                "compression_ratio",
                "png_size_bytes",
                "jpg_size_bytes",
                "score",
            ],
        )
        writer.writeheader()
        for rec in sorted(records, key=lambda r: (r["image"], r["quality"])):
            writer.writerow(rec)

    plot_curves(
        records,
        output_dir / "figure1_mse_vs_quality.png",
        y_key="mse",
        y_label="MSE",
        title="Figura 1: MSE vs Quality",
    )

    plot_curves(
        records,
        output_dir / "figure2_cr_vs_quality.png",
        y_key="compression_ratio",
        y_label="Ratio de compressió (PNG/JPEG)",
        title="Figura 2: Ratio de compressió vs Quality",
    )

    record_lookup = {
        (r["image"], int(r["quality"])): r for r in records
    }

    report_lines = []
    report_lines.append("# Anàlisi de compressió JPEG")
    report_lines.append("")
    report_lines.append("## Resum executiu")
    report_lines.append(
        f"- Imatges processades: {len(by_image)} de {len(png_paths)} disponibles."
    )
    report_lines.append(f"- Qualitats analitzades: {qualities}")
    report_lines.append(f"- Figura 1: `figure1_mse_vs_quality.png`")
    report_lines.append(f"- Figura 2: `figure2_cr_vs_quality.png`")
    report_lines.append("")

    report_lines.append("## (c) Possibles raons de diferències de MSE entre imatges")
    report_lines.append(
        "- En general, imatges amb més detall fi (textures/vores) i més variabilitat cromàtica pateixen més error JPEG a quality fixa."
    )
    report_lines.append(
        "- Imatges amb zones uniformes solen donar MSE menor perquè la quantització DCT introdueix menys artefactes visibles."
    )
    report_lines.append(
        "- Comparativa quantitativa a quality de referència q=50:"
    )
    report_lines.append("")

    qref = nearest_quality(50, qualities)
    for image_name in sorted(by_image.keys()):
        rec = record_lookup.get((image_name, qref))
        if rec is None:
            continue
        info = image_info[image_name]
        report_lines.append(
            f"- `{image_name}`: MSE@q{qref}={rec['mse']:.3f}, "
            f"entropia={info['entropy']:.3f}, LapVar={info['lap_var']:.3f}, "
            f"var cromàtica={info['chroma_var']:.3f}."
        )
    report_lines.append("")

    report_lines.append("## (d) Diferències d'error dins de cada imatge")
    report_lines.append(
        "- Per cada imatge es generen visuals per q=30, q=best i q=90 amb: original, JPEG, mapa d'error absolut i 3 crops amb error màxim."
    )
    report_lines.append("")

    for image_name in sorted(by_image.keys()):
        orig = loaded_images[image_name]
        q_targets = [
            ("q30", 30),
            ("qbest", best_quality[image_name]),
            ("q90", 90),
        ]

        report_lines.append(f"### {image_name}")
        report_lines.append(
            f"- Qualitat recomanada (compromís CR/MSE): **q={best_quality[image_name]}**"
        )

        for label, q_target in q_targets:
            q = q_target if q_target in qualities else nearest_quality(q_target, qualities)
            jpg_path = jpeg_root / image_name / f"q{q}.jpg"
            target = cv2.imread(str(jpg_path), cv2.IMREAD_COLOR)
            if target is None:
                report_lines.append(
                    f"- {label} (q={q}): no s'ha pogut carregar el JPEG."
                )
                continue

            vis_path = visual_root / f"{image_name}_{label}_q{q}.png"
            build_visual_error(orig, target, vis_path)
            region_text, edge_mean, smooth_mean = compression_region_comment(orig, target)
            rec = record_lookup.get((image_name, q))
            if rec is None:
                report_lines.append(f"- {label} (q={q}): sense mètriques disponibles.")
                continue
            report_lines.append(
                f"- {label} (q={q}): MSE={rec['mse']:.3f}, CR={rec['compression_ratio']:.3f}, "
                f"err_vores={edge_mean:.3f}, err_suau={smooth_mean:.3f}. {region_text} "
                f"(visual: `{vis_path.name}`)"
            )
        report_lines.append("")

    plain_report_lines = []
    for line in report_lines:
        plain_line = line
        if plain_line.startswith("### "):
            plain_line = f"Imatge: {plain_line[4:]}"
        elif plain_line.startswith("## "):
            plain_line = plain_line[3:]
        elif plain_line.startswith("# "):
            plain_line = plain_line[2:]

        if plain_line.startswith("- "):
            plain_line = plain_line[2:]

        plain_line = plain_line.replace("`", "").replace("**", "")
        plain_report_lines.append(plain_line)

    report_text = "\n".join(plain_report_lines)

    print(f"Done. Output directory: {output_dir}")
    print(f"- Metrics CSV: {csv_path}")
    print(f"- Figure 1: {output_dir / 'figure1_mse_vs_quality.png'}")
    print(f"- Figure 2: {output_dir / 'figure2_cr_vs_quality.png'}")
    print("- Report (console):")
    print(report_text)


if __name__ == "__main__":
    main()
