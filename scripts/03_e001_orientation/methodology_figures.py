#!/usr/bin/env python3
"""Create didactic methodology figures for the E-001 scientific report.

The figures explain the frozen protocol; they do not recompute or alter the
experiment results. Run from any directory with::

    .venv/bin/python scripts/03_e001_orientation/methodology_figures.py
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np

from e001_orientation import WIND_PATH, bin_indices, local_xy_km, rotate_motion


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs" / "03_e001_orientation"

INK = "#21323d"
MUTED = "#647783"
BLUE = "#3178a8"
TEAL = "#2a8c82"
ORANGE = "#d8862f"
RED = "#b84b45"
PURPLE = "#7653a6"
LIGHT = "#eef3f5"
GRID = "#cbd5da"
WHITE = "#ffffff"

REAL_EXAMPLE_TRACK_ID = 20100059
REAL_EXAMPLE_TIME = "2010-01-22 12:00:00"


def save(figure: plt.Figure, filename: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT / filename, dpi=190, bbox_inches="tight", facecolor=WHITE)
    plt.close(figure)


def workflow_figure() -> None:
    figure, axis = plt.subplots(figsize=(15.5, 7.2))
    axis.set_xlim(0, 15.5)
    axis.set_ylim(0, 7.2)
    axis.axis("off")

    nodes = [
        (0.35, 4.65, 3.0, 1.45, "1 · Pergunta e H2", "A rotação reduz a\ndispersão espacial?", BLUE),
        (4.15, 4.65, 3.0, 1.45, "2 · Protocolo congelado", "q95 · bins de 50 km\npeso por estado · heading ≥ 5", PURPLE),
        (7.95, 4.65, 3.0, 1.45, "3 · População elegível", "mesmos ciclones, estados,\ncélulas, suporte e flags", TEAL),
        (11.75, 4.65, 3.0, 1.45, "4 · Duas orientações", "QUADRANTES FIXOS  ↔  ROTACIONADOS\na única mudança é a rotação", ORANGE),
        (11.75, 1.15, 3.0, 1.45, "5 · Grade comum", "44 × 44 bins · 1.936 células\nsem smoothing", BLUE),
        (7.95, 1.15, 3.0, 1.45, "6 · Avaliação", "entropia · A50/75/90 · RMS\ncentroide · anisotropia", PURPLE),
        (4.15, 1.15, 3.0, 1.45, "7 · Incerteza", "500 réplicas pareadas\nreamostradas por track_id", TEAL),
        (0.35, 1.15, 3.0, 1.45, "8 · Decisão", "consistência entre métricas,\nfases, bootstrap e suporte", RED),
    ]
    for x, y, width, height, title, detail, color in nodes:
        box = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.025,rounding_size=0.08",
            linewidth=1.4, edgecolor=color, facecolor=WHITE,
        )
        axis.add_patch(box)
        axis.add_patch(Rectangle((x, y + height - 0.18), width, 0.18, facecolor=color, edgecolor="none"))
        axis.text(x + 0.18, y + height - 0.39, title, ha="left", va="top", color=INK, fontsize=11.5, fontweight="bold")
        axis.text(x + width / 2, y + 0.47, detail, ha="center", va="center", color=MUTED, fontsize=10.3, linespacing=1.35)

    arrow_pairs = [
        ((3.35, 5.38), (4.15, 5.38)),
        ((7.15, 5.38), (7.95, 5.38)),
        ((10.95, 5.38), (11.75, 5.38)),
        ((13.25, 4.65), (13.25, 2.60)),
        ((11.75, 1.88), (10.95, 1.88)),
        ((7.95, 1.88), (7.15, 1.88)),
        ((4.15, 1.88), (3.35, 1.88)),
    ]
    for start, end in arrow_pairs:
        axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=16, linewidth=1.5, color=INK))

    axis.text(7.75, 6.85, "Fluxo lógico de E-001", ha="center", va="center", color=INK, fontsize=16, fontweight="bold")
    axis.text(7.75, 0.35, "O fluxo separa escolhas feitas antes dos resultados, cálculo das métricas e regra de decisão.", ha="center", va="center", color=MUTED, fontsize=10.5)
    save(figure, "methodology_flow.png")


def real_state_example() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return centered q95 cells and bin indices for one documented real state."""
    source = WIND_PATH.as_posix().replace("'", "''")
    connection = duckdb.connect()
    table = connection.execute(
        f"""
        SELECT lat_center, lon_center, lat, lon
        FROM read_parquet('{source}')
        WHERE track_id = {REAL_EXAMPLE_TRACK_ID}
          AND time = TIMESTAMP '{REAL_EXAMPLE_TIME}'
          AND exceeded_q95
        ORDER BY lat, lon
        """
    ).to_arrow_table()
    connection.close()
    if table.num_rows != 15:
        raise RuntimeError(
            f"Estado real de exemplo deveria ter 15 células q95; encontrou {table.num_rows}"
        )
    x, y = local_xy_km(
        table["lat_center"].to_numpy(),
        table["lon_center"].to_numpy(),
        table["lat"].to_numpy(),
        table["lon"].to_numpy(),
    )
    bins, valid = bin_indices(x, y, 1_100.0, 50.0, 44)
    if not np.all(valid):
        raise RuntimeError("Estado real de exemplo contém célula fora do domínio")
    return x, y, bins


def bin_grid_figure() -> None:
    x, y, bins = real_state_example()
    edges = np.linspace(-1_100.0, 1_100.0, 45)
    centers = (edges[:-1] + edges[1:]) / 2.0
    occupied, counts = np.unique(bins, return_counts=True)

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(15.2, 6.6),
        constrained_layout=True,
        gridspec_kw={"width_ratios": [1.05, 1.35]},
    )
    figure.suptitle(
        "Grade de E-001: 44 × 44 bins de 50 km",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )

    axis = axes[0]
    for edge in edges:
        axis.axvline(edge, color=GRID, linewidth=0.28, alpha=0.72, zorder=0)
        axis.axhline(edge, color=GRID, linewidth=0.28, alpha=0.72, zorder=0)
    axis.add_patch(
        Rectangle(
            (-1_100, -1_100),
            2_200,
            2_200,
            facecolor="none",
            edgecolor=RED,
            linewidth=2.2,
            label="limite externo da grade",
        )
    )
    axis.add_patch(
        Circle(
            (0, 0),
            1_100,
            facecolor="none",
            edgecolor=TEAL,
            linewidth=2.0,
            linestyle="--",
            label="limite radial do suporte (1.100 km)",
        )
    )
    zoom_x0, zoom_y0 = 150.0, -350.0
    axis.add_patch(
        Rectangle(
            (zoom_x0, zoom_y0),
            200,
            100,
            facecolor=ORANGE,
            edgecolor=ORANGE,
            alpha=0.22,
            linewidth=2.5,
            label="região ampliada à direita",
        )
    )
    axis.scatter([0], [0], marker="+", s=95, linewidth=2.0, color=INK, zorder=4)
    axis.text(32, 32, "centro do ciclone", color=INK, fontsize=9.5, ha="left", va="bottom")
    axis.set(
        xlim=(-1_150, 1_150),
        ylim=(-1_150, 1_150),
        aspect="equal",
        xlabel="x relativo (km) · 44 colunas",
        ylabel="y relativo (km) · 44 linhas",
        title="A · Domínio completo: 1.936 bins",
        xticks=[-1_100, -550, 0, 550, 1_100],
        yticks=[-1_100, -550, 0, 550, 1_100],
    )
    axis.legend(loc="upper left", fontsize=8.4, frameon=True)

    axis = axes[1]
    for flat, count in zip(occupied, counts, strict=True):
        ix = int(flat % 44)
        iy = int(flat // 44)
        axis.add_patch(
            Rectangle(
                (edges[ix], edges[iy]),
                50,
                50,
                facecolor=BLUE,
                edgecolor="none",
                alpha=0.14 + 0.055 * count,
            )
        )
    for edge in np.arange(150, 351, 50):
        axis.axvline(edge, color=INK, linewidth=0.9, zorder=1)
    for edge in np.arange(-350, -249, 50):
        axis.axhline(edge, color=INK, linewidth=0.9, zorder=1)
    axis.scatter(x, y, s=42, color=ORANGE, edgecolor=WHITE, linewidth=0.7, zorder=4, label="célula ERA5 que excedeu q95")
    for flat, count in zip(occupied, counts, strict=True):
        ix = int(flat % 44)
        iy = int(flat // 44)
        weight = 100.0 * count / x.size
        axis.text(
            centers[ix],
            edges[iy] + 4,
            f"{count}/15 = {weight:.1f}%".replace(".", ","),
            ha="center",
            va="bottom",
            color=INK,
            fontsize=8.6,
            fontweight="bold",
            bbox={"facecolor": WHITE, "edgecolor": "none", "alpha": 0.78, "pad": 1.2},
            zorder=5,
        )
    axis.set(
        xlim=(145, 355),
        ylim=(-355, -245),
        aspect="equal",
        xlabel="x relativo (km)",
        ylabel="y relativo (km)",
        title="B · Estado real em intensificação · track 20100059 · 22 jan 2010 12 UTC\n15 células q95 em 6 bins; cada ponto vale 1/15 = 6,67%",
        xticks=[150, 200, 250, 300, 350],
        yticks=[-350, -300, -250],
    )
    axis.legend(loc="lower right", fontsize=8.7, frameon=True)
    save(figure, "bin_grid_real_state.png")


def coordinate_frames_figure() -> None:
    heading = np.radians(135.0)
    rng = np.random.default_rng(24)
    cloud = rng.normal(size=(90, 2)) @ np.array([[155.0, 35.0], [25.0, 95.0]])
    cloud += np.array([145.0, -175.0])
    fixed_x, fixed_y = cloud[:, 0], cloud[:, 1]
    rotated_x, rotated_y = rotate_motion(fixed_x, fixed_y, np.full(fixed_x.size, heading))
    move_fixed = np.array([np.sin(heading), np.cos(heading)]) * 470.0
    move_rotated_x, move_rotated_y = rotate_motion(
        np.array([move_fixed[0]]), np.array([move_fixed[1]]), np.array([heading])
    )

    figure, axes = plt.subplots(1, 2, figsize=(13.8, 6.4), constrained_layout=True)
    figure.suptitle(
        "O mesmo estado em quadrantes fixos e rotacionados pelo movimento",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )
    panels = (
        (
            axes[0],
            fixed_x,
            fixed_y,
            move_fixed[0],
            move_fixed[1],
            "A · Quadrantes fixos (centered)",
            ("OESTE", "LESTE", "SUL", "NORTE"),
            "O norte geográfico continua para cima",
        ),
        (
            axes[1],
            rotated_x,
            rotated_y,
            float(move_rotated_x[0]),
            float(move_rotated_y[0]),
            "B · Quadrantes rotacionados (motion-relative)",
            ("ESQUERDA", "DIREITA", "RETAGUARDA", "FRENTE"),
            "O deslocamento passa a apontar para a frente",
        ),
    )
    for axis, px, py, arrow_x, arrow_y, title, labels, note in panels:
        axis.axhline(0, color=INK, linewidth=1.2)
        axis.axvline(0, color=INK, linewidth=1.2)
        axis.scatter(px, py, s=18, color=BLUE, alpha=0.38, edgecolor="none", label="mesmas células q95")
        axis.scatter([0], [0], s=105, marker="o", color=WHITE, edgecolor=INK, linewidth=2.0, zorder=5)
        axis.add_patch(
            FancyArrowPatch(
                (0, 0),
                (arrow_x, arrow_y),
                arrowstyle="-|>",
                mutation_scale=18,
                linewidth=2.5,
                color=ORANGE,
                zorder=6,
                label="direção de deslocamento",
            )
        )
        left, right, bottom, top = labels
        axis.text(-525, 22, left, ha="left", va="bottom", color=MUTED, fontsize=9.5, fontweight="bold")
        axis.text(525, 22, right, ha="right", va="bottom", color=MUTED, fontsize=9.5, fontweight="bold")
        axis.text(15, -525, bottom, ha="left", va="bottom", color=MUTED, fontsize=9.5, fontweight="bold")
        axis.text(15, 525, top, ha="left", va="top", color=MUTED, fontsize=9.5, fontweight="bold")
        axis.set(
            xlim=(-550, 550),
            ylim=(-550, 550),
            aspect="equal",
            xlabel="eixo horizontal relativo (km)",
            ylabel="eixo vertical relativo (km)",
            title=title,
            xticks=[-500, -250, 0, 250, 500],
            yticks=[-500, -250, 0, 250, 500],
        )
        axis.grid(color=GRID, linewidth=0.6, alpha=0.62)
        if "rotacionados" in title:
            axis.text(-515, -455, note, ha="left", va="bottom", color=MUTED, fontsize=9.5)
        else:
            axis.text(-515, 455, note, ha="left", va="top", color=MUTED, fontsize=9.5)
    axes[0].text(330, -430, "movimento para sudeste", ha="center", va="center", color=ORANGE, fontsize=9.5, fontweight="bold")
    axes[1].text(36, 430, "mesmo vetor alinhado\ncom a frente", ha="left", va="center", color=ORANGE, fontsize=9.5, fontweight="bold")
    save(figure, "coordinate_frames_example.png")


def binning_entropy_figure() -> None:
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.9), constrained_layout=True)
    figure.suptitle("Exemplo esquemático · como a entropia responde aos pesos por bin", fontsize=15, fontweight="bold", color=INK)

    compact = np.zeros((4, 4), dtype=float)
    compact[1:3, 1:3] = np.array([[0.10, 0.10], [0.10, 0.70]])
    diffuse = np.zeros((4, 4), dtype=float)
    diffuse[0, 0] = diffuse[0, 3] = diffuse[3, 0] = diffuse[3, 3] = 0.25
    for axis, values, title in (
        (axes[0], compact, "A · Peso mais concentrado"),
        (axes[1], diffuse, "B · Peso distribuído uniformemente"),
    ):
        image = axis.imshow(values, origin="lower", cmap="Blues", vmin=0, vmax=0.70)
        axis.set_xticks(np.arange(-0.5, 4, 1), minor=True)
        axis.set_yticks(np.arange(-0.5, 4, 1), minor=True)
        axis.grid(which="minor", color=WHITE, linewidth=1.5)
        axis.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
        for (row, column), value in np.ndenumerate(values):
            if value > 0:
                axis.text(column, row, f"{value:.2f}", ha="center", va="center", color=WHITE if value >= 0.4 else INK, fontsize=10, fontweight="bold")
        positive = values[values > 0]
        entropy = -float(np.sum(positive * np.log(positive)))
        axis.set_title(title)
        axis.text(1.5, -0.88, f"H = {entropy:.3f} nat", ha="center", va="center", color=INK, fontsize=11, fontweight="bold")
        axis.text(1.5, 4.02, "grade 4 × 4 apenas didática", ha="center", va="bottom", color=MUTED, fontsize=9.5)
    figure.colorbar(image, ax=axes, shrink=0.78, label="proporção pᵢ do peso no bin")
    save(figure, "binning_entropy_example.png")


def concentration_area_figure() -> None:
    probabilities = np.array([0.30, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05, 0.05])
    cumulative = np.cumsum(probabilities)
    ranks = np.arange(1, probabilities.size + 1)
    area = 2_500
    levels = [(0.50, 2, BLUE, "A50 = 2 bins = 5.000 km²"), (0.75, 4, TEAL, "A75 = 4 bins = 10.000 km²"), (0.90, 6, ORANGE, "A90 = 6 bins = 15.000 km²")]

    figure, axes = plt.subplots(1, 2, figsize=(14.8, 5.0), constrained_layout=True, gridspec_kw={"width_ratios": [1.45, 1.0]})
    figure.suptitle("Exemplo didático · como A50, A75 e A90 são calculadas", fontsize=15, fontweight="bold", color=INK)

    ax = axes[0]
    bars = ax.bar(ranks, probabilities, color=BLUE, alpha=0.80, width=0.72, label="peso pᵢ")
    ax.set(xlabel="bins ordenados do maior para o menor pᵢ", ylabel="proporção do peso no bin pᵢ", xticks=ranks, ylim=(0, 0.34), title="A · Ordenar os bins por peso")
    ax.grid(axis="y", color=GRID, linewidth=0.7, alpha=0.65)
    for bar, value in zip(bars, probabilities, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.009, f"{value:.2f}", ha="center", va="bottom", color=INK, fontsize=9)
    twin = ax.twinx()
    twin.plot(ranks, cumulative, color=RED, marker="o", linewidth=2.2, label="peso acumulado")
    twin.set(ylabel="proporção acumulada do peso", ylim=(0, 1.05), yticks=np.arange(0, 1.01, 0.25))
    for level, required, color, _ in levels:
        twin.axhline(level, color=color, linestyle="--", linewidth=1.1, alpha=0.9)
        twin.axvline(required, color=color, linestyle=":", linewidth=1.1, alpha=0.9)
        twin.scatter([required], [cumulative[required - 1]], s=58, color=color, zorder=5)

    ax = axes[1]
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.05, 0.92, "B · Procurar o menor k", ha="left", va="top", color=INK, fontsize=12, fontweight="bold")
    ax.text(0.05, 0.82, "kq = menor número de bins cuja\nsoma acumulada alcança q", ha="left", va="top", color=MUTED, fontsize=11, linespacing=1.4)
    y_values = [0.62, 0.43, 0.24]
    for (level, required, color, label), y in zip(levels, y_values, strict=True):
        ax.add_patch(FancyBboxPatch((0.05, y - 0.06), 0.88, 0.13, boxstyle="round,pad=0.015,rounding_size=0.025", facecolor=LIGHT, edgecolor=color, linewidth=1.3))
        ax.text(0.10, y, label, ha="left", va="center", color=INK, fontsize=11, fontweight="bold")
    ax.text(0.05, 0.07, f"Cada bin do experimento mede 50 × 50 km;\nlogo, área por bin = {area:,} km².".replace(",", "."), ha="left", va="bottom", color=MUTED, fontsize=10.5, linespacing=1.4)
    save(figure, "concentration_area_example.png")


def geometry_metrics_figure() -> None:
    rng = np.random.default_rng(8)
    angle = np.radians(28)
    rotation = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    base = rng.normal(size=(850, 2)) @ np.diag([250.0, 105.0])
    points = base @ rotation.T + np.array([130.0, -90.0])
    weights = np.full(points.shape[0], 1.0 / points.shape[0])
    centroid = np.sum(points * weights[:, None], axis=0)
    centered = points - centroid
    covariance = (centered * weights[:, None]).T @ centered
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    rms = float(np.sqrt(np.trace(covariance)))
    axis_ratio = float(np.sqrt(eigenvalues[1] / eigenvalues[0]))
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    ellipse_angle = np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0]))

    figure, axis = plt.subplots(figsize=(8.2, 7.0))
    axis.scatter(points[:, 0], points[:, 1], s=8, color=BLUE, alpha=0.18, edgecolor="none", label="peso espacial hipotético")
    axis.scatter([0], [0], marker="+", s=160, color=INK, linewidths=2.2, label="centro do ciclone")
    axis.scatter([centroid[0]], [centroid[1]], marker="X", s=100, color=RED, edgecolor=WHITE, linewidth=0.8, zorder=5, label="centroide ponderado")
    axis.add_patch(Circle(centroid, rms, facecolor="none", edgecolor=TEAL, linewidth=2.0, linestyle="--", label=f"raio RMS = {rms:.0f} km"))
    ellipse = Ellipse(centroid, 4 * np.sqrt(eigenvalues[0]), 4 * np.sqrt(eigenvalues[1]), angle=ellipse_angle, facecolor="none", edgecolor=ORANGE, linewidth=2.2, label=f"covariância · razão = {axis_ratio:.2f}")
    axis.add_patch(ellipse)
    for value, vector, color in zip(eigenvalues, eigenvectors.T, (ORANGE, PURPLE), strict=True):
        span = 2 * np.sqrt(value) * vector
        axis.plot([centroid[0] - span[0], centroid[0] + span[0]], [centroid[1] - span[1], centroid[1] + span[1]], color=color, linewidth=2.0)
    axis.axhline(0, color=GRID, linewidth=0.9)
    axis.axvline(0, color=GRID, linewidth=0.9)
    axis.set(xlim=(-750, 900), ylim=(-750, 650), aspect="equal", xlabel="x relativo (km)", ylabel="y relativo (km)", title="Exemplo didático · centroide, RMS e anisotropia")
    axis.grid(color=GRID, linewidth=0.55, alpha=0.55)
    axis.legend(loc="lower right", frameon=True, fontsize=9.5)
    axis.text(-710, 585, "Centroide: média espacial ponderada\nRMS: dispersão ao redor do centroide\nAutovalores: comprimentos dos eixos principais", ha="left", va="top", color=MUTED, fontsize=10.5, linespacing=1.4)
    save(figure, "geometric_metrics_example.png")


def main() -> None:
    workflow_figure()
    bin_grid_figure()
    coordinate_frames_figure()
    binning_entropy_figure()
    concentration_area_figure()
    geometry_metrics_figure()
    for filename in (
        "methodology_flow.png",
        "bin_grid_real_state.png",
        "coordinate_frames_example.png",
        "binning_entropy_example.png",
        "concentration_area_example.png",
        "geometric_metrics_example.png",
    ):
        print(f"Wrote {(OUTPUT / filename).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
