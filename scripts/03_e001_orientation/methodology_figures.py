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
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch, FancyBboxPatch, Patch, Rectangle
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
    figure, axis = plt.subplots(figsize=(18.0, 10.4))
    axis.set_xlim(0, 18.0)
    axis.set_ylim(0, 10.4)
    axis.axis("off")

    def stage_box(
        x: float,
        y: float,
        width: float,
        height: float,
        title: str,
        detail: str,
        color: str,
    ) -> None:
        box = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.025,rounding_size=0.08",
            linewidth=1.4, edgecolor=color, facecolor=WHITE,
        )
        axis.add_patch(box)
        axis.add_patch(Rectangle((x, y + height - 0.18), width, 0.18, facecolor=color, edgecolor="none"))
        axis.text(x + 0.16, y + height - 0.35, title, ha="left", va="top", color=INK, fontsize=10.6, fontweight="bold")
        axis.text(x + width / 2, y + 0.42, detail, ha="center", va="center", color=MUTED, fontsize=9.4, linespacing=1.3)

    stage_box(0.35, 7.65, 2.40, 1.45, "1 · Pergunta e H2", "A rotação reduz a\ndispersão espacial?", BLUE)
    stage_box(3.12, 7.65, 2.40, 1.45, "2 · Protocolo", "q95 · bins de 50 km\npeso por estado · heading ≥ 5", PURPLE)
    stage_box(5.89, 7.65, 2.40, 1.45, "3 · População", "mesmos ciclones, estados,\ncélulas, suporte e flags", TEAL)

    orientation_x, orientation_y = 8.66, 6.85
    orientation_width, orientation_height = 4.35, 3.05
    orientation = FancyBboxPatch(
        (orientation_x, orientation_y), orientation_width, orientation_height,
        boxstyle="round,pad=0.035,rounding_size=0.10",
        linewidth=1.6, edgecolor=ORANGE, facecolor=LIGHT,
    )
    axis.add_patch(orientation)
    axis.text(
        orientation_x + 0.20, orientation_y + orientation_height - 0.25,
        "4 · Duas análises de orientação",
        ha="left", va="top", color=INK, fontsize=10.8, fontweight="bold",
    )
    branch_specs = (
        (orientation_y + 1.35, "ANÁLISE A · QUADRANTES FIXOS", "norte geográfico para cima"),
        (orientation_y + 0.30, "ANÁLISE B · ROTACIONADOS", "movimento para a frente"),
    )
    for child_y, child_title, child_detail in branch_specs:
        child = FancyBboxPatch(
            (orientation_x + 0.72, child_y), 3.20, 0.78,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=1.1, edgecolor=ORANGE, facecolor=WHITE,
        )
        axis.add_patch(child)
        axis.text(orientation_x + 0.88, child_y + 0.52, child_title, ha="left", va="center", color=INK, fontsize=9.1, fontweight="bold")
        axis.text(orientation_x + 0.88, child_y + 0.20, child_detail, ha="left", va="center", color=MUTED, fontsize=8.8)
    split_x = orientation_x + 0.38
    axis.plot([orientation_x, split_x], [8.25, 8.25], color=INK, linewidth=1.2)
    axis.plot([split_x, split_x], [7.54, 8.59], color=INK, linewidth=1.2)
    for target_y in (8.59, 7.54):
        axis.add_patch(FancyArrowPatch((split_x, target_y), (orientation_x + 0.72, target_y), arrowstyle="-|>", mutation_scale=12, linewidth=1.2, color=INK))

    stage_box(13.48, 7.65, 2.72, 1.45, "5 · Grade comum", "44 × 44 bins · duas\ndistribuições comparáveis", BLUE)

    evaluation_x, evaluation_y = 11.44, 1.60
    evaluation_width, evaluation_height = 6.16, 4.95
    evaluation = FancyBboxPatch(
        (evaluation_x, evaluation_y), evaluation_width, evaluation_height,
        boxstyle="round,pad=0.035,rounding_size=0.10",
        linewidth=1.6, edgecolor=PURPLE, facecolor=LIGHT,
    )
    axis.add_patch(evaluation)
    axis.text(
        evaluation_x + 0.22, evaluation_y + evaluation_height - 0.25,
        "6 · Avaliação · o que cada métrica mostra",
        ha="left", va="top", color=INK, fontsize=10.8, fontweight="bold",
    )
    evaluations = (
        ("Uniformidade dos pesos", "→  Entropia"),
        ("Área mínima para cobertura", "→  A50 · A75 · A90"),
        ("Escala ao redor do centroide", "→  RMS"),
        ("Posição média", "→  Centroide"),
        ("Alongamento direcional", "→  Anisotropia"),
        ("Cobertura observacional", "→  Suporte"),
    )
    for index, (question, metric) in enumerate(evaluations):
        column = index % 2
        row = index // 2
        child_x = evaluation_x + 0.24 + column * 2.94
        child_y = evaluation_y + 2.92 - row * 1.16
        child = FancyBboxPatch(
            (child_x, child_y), 2.70, 0.92,
            boxstyle="round,pad=0.02,rounding_size=0.055",
            linewidth=1.0, edgecolor=PURPLE, facecolor=WHITE,
        )
        axis.add_patch(child)
        axis.text(child_x + 0.15, child_y + 0.62, question, ha="left", va="center", color=MUTED, fontsize=8.9)
        axis.text(child_x + 0.15, child_y + 0.27, metric, ha="left", va="center", color=INK, fontsize=9.5, fontweight="bold")

    stage_box(7.78, 3.18, 2.92, 1.55, "7 · Incerteza", "500 réplicas pareadas\npor ciclone inteiro", TEAL)
    stage_box(4.08, 3.18, 2.92, 1.55, "8 · Decisão", "consistência entre métricas,\nfases, bootstrap e suporte", RED)

    arrow_pairs = [
        ((2.75, 8.38), (3.12, 8.38)),
        ((5.52, 8.38), (5.89, 8.38)),
        ((8.29, 8.38), (8.66, 8.38)),
        ((13.01, 8.38), (13.48, 8.38)),
        ((14.84, 7.65), (14.84, 6.55)),
        ((11.44, 4.05), (10.70, 4.05)),
        ((7.78, 4.05), (7.00, 4.05)),
    ]
    for start, end in arrow_pairs:
        axis.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=16, linewidth=1.5, color=INK))

    axis.text(9.0, 10.10, "Fluxo lógico de E-001", ha="center", va="center", color=INK, fontsize=16, fontweight="bold")
    axis.text(9.0, 0.55, "Os braços diferem somente pela orientação; todas as avaliações e a incerteza usam comparação pareada.", ha="center", va="center", color=MUTED, fontsize=10.5)
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


def rms_vector_geometry_figure() -> None:
    """Explain the RMS geometry with a shared legend and sparse panels."""
    centroid_target = np.array([75.0, 75.0])
    weights = np.array([0.40, 0.15, 0.15, 0.15, 0.15])
    cases = (
        ("A · Padrão compacto", 50.0),
        ("B · Padrão disperso", 150.0),
    )

    figure, axes = plt.subplots(1, 2, figsize=(16.8, 8.5), sharex=True, sharey=True)
    figure.subplots_adjust(left=0.065, right=0.985, bottom=0.235, top=0.835, wspace=0.16)
    figure.suptitle(
        "RMS: mesma posição média, dispersões diferentes",
        y=0.975,
        fontsize=16,
        fontweight="bold",
        color=INK,
    )
    figure.text(
        0.5,
        0.925,
        "Os dois padrões têm o mesmo centro do ciclone, o mesmo centroide e os mesmos pesos; "
        "em B, os bins periféricos estão mais distantes.",
        ha="center",
        va="center",
        color=MUTED,
        fontsize=10.5,
    )

    for axis, (title, spread) in zip(axes, cases, strict=True):
        offsets = np.array(
            [
                [0.0, 0.0],
                [-spread, -spread],
                [-spread, spread],
                [spread, -spread],
                [spread, spread],
            ]
        )
        centers = centroid_target + offsets
        centroid = np.sum(centers * weights[:, None], axis=0)
        distances = np.linalg.norm(centers - centroid, axis=1)
        rms = float(np.sqrt(np.sum(weights * distances**2)))
        highlighted = centers[3]
        highlighted_distance = float(distances[3])

        for edge in np.arange(-150.0, 301.0, 50.0):
            axis.axvline(edge, color=GRID, linewidth=0.55, alpha=0.40, zorder=0)
            axis.axhline(edge, color=GRID, linewidth=0.55, alpha=0.40, zorder=0)

        for index, (center, weight) in enumerate(zip(centers, weights, strict=True)):
            is_highlighted = index == 3
            axis.add_patch(
                Rectangle(
                    (center[0] - 25.0, center[1] - 25.0),
                    50.0,
                    50.0,
                    facecolor=BLUE,
                    edgecolor=ORANGE if is_highlighted else BLUE,
                    linewidth=2.5 if is_highlighted else 1.0,
                    alpha=0.16 + 0.95 * weight,
                    zorder=1,
                )
            )

        # Component guides are identified once in the shared legend.
        axis.plot([highlighted[0], highlighted[0]], [0.0, highlighted[1]], color=BLUE, linewidth=1.2, linestyle=":", alpha=0.85, zorder=3)
        axis.plot([0.0, highlighted[0]], [highlighted[1], highlighted[1]], color=BLUE, linewidth=1.2, linestyle=":", alpha=0.85, zorder=3)
        axis.plot([centroid[0], centroid[0]], [0.0, centroid[1]], color=RED, linewidth=1.2, linestyle="--", alpha=0.85, zorder=3)
        axis.plot([0.0, centroid[0]], [centroid[1], centroid[1]], color=RED, linewidth=1.2, linestyle="--", alpha=0.85, zorder=3)

        axis.add_patch(
            FancyArrowPatch(
                (0.0, 0.0), tuple(highlighted),
                arrowstyle="-|>", mutation_scale=13,
                linewidth=2.0, color=BLUE, zorder=4,
            )
        )
        axis.add_patch(
            FancyArrowPatch(
                (0.0, 0.0), tuple(centroid),
                arrowstyle="-|>", mutation_scale=13,
                linewidth=2.2, color=RED, zorder=5,
            )
        )
        axis.add_patch(
            FancyArrowPatch(
                tuple(centroid), tuple(highlighted),
                arrowstyle="<->", mutation_scale=12,
                linewidth=2.0, color=PURPLE, zorder=5,
            )
        )
        axis.add_patch(
            Circle(
                centroid, rms,
                facecolor="none", edgecolor=TEAL,
                linewidth=2.1, linestyle=(0, (5, 3)), zorder=2,
            )
        )

        # Sparse marker labels keep the geometry readable; details live below.
        axis.scatter([0.0], [0.0], s=125, facecolor=WHITE, edgecolor=INK, linewidth=2.0, zorder=6)
        axis.scatter([0.0], [0.0], s=18, color=INK, zorder=7)
        axis.scatter([centroid[0]], [centroid[1]], marker="X", s=115, color=RED, edgecolor=WHITE, linewidth=0.9, zorder=7)
        axis.scatter([highlighted[0]], [highlighted[1]], marker="s", s=42, color=ORANGE, edgecolor=WHITE, linewidth=0.7, zorder=7)
        axis.text(-8.0, -18.0, "O", ha="right", va="top", color=INK, fontsize=10.0, fontweight="bold", zorder=8)
        axis.text(centroid[0] + 8.0, centroid[1] + 8.0, "μ", ha="left", va="bottom", color=RED, fontsize=10.5, fontweight="bold", zorder=8)
        axis.text(highlighted[0] + 8.0, highlighted[1] - 2.0, "i", ha="left", va="center", color=ORANGE, fontsize=10.5, fontweight="bold", zorder=8)

        distance_midpoint = (centroid + highlighted) / 2.0
        axis.text(
            distance_midpoint[0] + 9.0, distance_midpoint[1] + 9.0,
            f"dᵢ = {highlighted_distance:.0f} km",
            ha="left", va="bottom", color=PURPLE, fontsize=9.2, fontweight="bold",
            bbox={"facecolor": WHITE, "edgecolor": "none", "alpha": 0.82, "pad": 1.2},
            zorder=8,
        )

        axis.axhline(0.0, color=INK, linewidth=1.0, zorder=1)
        axis.axvline(0.0, color=INK, linewidth=1.0, zorder=1)
        axis.set(
            xlim=(-155.0, 310.0),
            ylim=(-155.0, 310.0),
            aspect="equal",
            xlabel="x relativo ao centro (km)",
            title=f"{title}  ·  RMS ≈ {rms:.0f} km",
        )
        axis.set_xticks(np.arange(-100.0, 301.0, 100.0))
        axis.set_yticks(np.arange(-100.0, 301.0, 100.0))
        axis.tick_params(labelsize=9.2)
        for spine in ("top", "right"):
            axis.spines[spine].set_visible(False)

    axes[0].set_ylabel("y relativo ao centro (km)")

    legend_handles = [
        Line2D([], [], linestyle="none", marker="o", markerfacecolor=WHITE, markeredgecolor=INK, markeredgewidth=1.8, markersize=8, label="O  centro do ciclone"),
        Line2D([], [], linestyle="none", marker="X", markerfacecolor=RED, markeredgecolor=WHITE, markersize=9, label="μ  centroide ponderado"),
        Line2D([], [], linestyle="none", marker="s", markerfacecolor=ORANGE, markeredgecolor=ORANGE, markersize=7, label="i  bin destacado"),
        Patch(facecolor=BLUE, edgecolor=BLUE, alpha=0.35, label="tom azul  peso pᵢ"),
        Line2D([], [], color=BLUE, linewidth=2.1, marker=">", markevery=[1], markersize=6, label="rᵢ  centro → bin"),
        Line2D([], [], color=RED, linewidth=2.1, marker=">", markevery=[1], markersize=6, label="μ  centro → centroide"),
        Line2D([], [], color=PURPLE, linewidth=2.1, label="dᵢ  centroide ↔ bin"),
        Line2D([], [], color=TEAL, linewidth=2.1, linestyle=(0, (5, 3)), label="RMS  raio tracejado"),
        Line2D([], [], color=BLUE, linewidth=1.3, linestyle=":", label="xᵢ, yᵢ  guias azuis"),
        Line2D([], [], color=RED, linewidth=1.3, linestyle="--", label="μₓ, μᵧ  guias vermelhas"),
    ]
    legend = figure.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.025),
        ncol=5,
        title="Como ler os símbolos",
        frameon=True,
        facecolor=WHITE,
        edgecolor=GRID,
        fontsize=9.0,
        title_fontsize=10.0,
        columnspacing=1.5,
        handlelength=2.4,
        handletextpad=0.6,
        borderpad=0.8,
        labelspacing=0.8,
    )
    legend.get_frame().set_linewidth(0.9)

    save(figure, "rms_vector_geometry.png")


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


def bootstrap_scheme_figure() -> None:
    """Didactic scheme of the cyclone-level bootstrap used for the intervals."""
    population = [
        ("C1", 3),
        ("C2", 5),
        ("C3", 2),
        ("C4", 4),
    ]
    colors = {"C1": BLUE, "C2": TEAL, "C3": PURPLE, "C4": ORANGE}
    replicas = [
        (["C2", "C2", "C4", "C1"], "C2 × 2\n1 ausente"),
        (["C2", "C2", "C2", "C4"], "C2 × 3\n2 ausentes"),
        (["C1", "C2", "C3", "C4"], "0 ausentes"),
    ]
    sizes = dict(population)

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(15.0, 5.9),
        constrained_layout=True,
        gridspec_kw={"width_ratios": [1.35, 1.0]},
    )
    figure.suptitle(
        "Exemplo esquemático · por que a reamostragem é por ciclone, não por célula",
        fontsize=15,
        fontweight="bold",
        color=INK,
    )

    axis = axes[0]
    axis.set_xlim(0, 16.4)
    axis.set_ylim(0, 6.2)
    axis.axis("off")

    def draw_row(y: float, label: str, entries: list[str], note: str) -> None:
        axis.text(
            0.0, y + 0.30, label,
            ha="left", va="center", color=INK,
            fontsize=9.5 if "\n" in label else 11,
            fontweight="bold", linespacing=1.25,
        )
        x = 2.55
        for name in entries:
            width = sizes[name] * 0.52
            box = FancyBboxPatch(
                (x, y - 0.02), width, 0.64,
                boxstyle="round,pad=0.015,rounding_size=0.05",
                linewidth=1.3, edgecolor=colors[name], facecolor=WHITE,
            )
            axis.add_patch(box)
            for index in range(sizes[name]):
                axis.add_patch(
                    Rectangle(
                        (x + 0.09 + index * 0.49, y + 0.13), 0.36, 0.38,
                        facecolor=colors[name], edgecolor="none", alpha=0.55,
                    )
                )
            axis.text(x + width / 2, y + 0.80, name, ha="center", va="bottom",
                      color=colors[name], fontsize=10.2, fontweight="bold")
            x += width + 0.42
        axis.text(16.3, y + 0.30, note, ha="right", va="center", color=MUTED, fontsize=9.6)

    draw_row(5.05, "População", [name for name, _ in population], "cada bloco = um estado do ciclone")
    for index, (replica, note) in enumerate(replicas):
        draw_row(3.75 - index * 1.25, f"Réplica {index + 1}\n{note}", replica, "")

    axis.text(
        0.0, 0.33,
        "Cada réplica faz N = 4 sorteios com reposição — não retira exatamente um ciclone.\n"
        "Quando um ciclone é sorteado, todos os seus estados e células entram juntos.",
        ha="left", va="center", color=INK, fontsize=10.4, linespacing=1.45,
    )

    axis = axes[1]
    generator = np.random.default_rng(20260921)
    differences = generator.normal(loc=-0.0023, scale=0.0041, size=500)
    low, high = np.percentile(differences, [2.5, 97.5])
    axis.hist(differences, bins=26, color="#cfe0e8", edgecolor=BLUE, linewidth=0.8)
    axis.axvline(0.0, color=MUTED, linewidth=1.3, linestyle=":")
    axis.axvline(low, color=RED, linewidth=1.6)
    axis.axvline(high, color=RED, linewidth=1.6)
    axis.axvline(float(np.mean(differences)), color=ORANGE, linewidth=1.8)
    axis.set_title("Distribuição das 500 diferenças recalculadas", fontsize=12, color=INK)
    axis.set_xlabel("diferença da métrica numa réplica (unidade da métrica)")
    axis.set_ylabel("número de réplicas")
    axis.tick_params(labelsize=9.5)
    axis.text(
        0.02, 0.96,
        "valores ilustrativos,\nnão são o bootstrap de E-001",
        transform=axis.transAxes, ha="left", va="top", color=MUTED, fontsize=9.4, linespacing=1.4,
    )
    axis.annotate(
        "percentis 2,5 e 97,5\ndelimitam o IC de 95%",
        xy=(high, axis.get_ylim()[1] * 0.52), xytext=(high + 0.0018, axis.get_ylim()[1] * 0.80),
        color=RED, fontsize=9.6, linespacing=1.4,
        arrowprops={"arrowstyle": "-|>", "color": RED, "linewidth": 1.2},
    )
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)

    save(figure, "bootstrap_scheme.png")


def main() -> None:
    workflow_figure()
    bin_grid_figure()
    coordinate_frames_figure()
    binning_entropy_figure()
    concentration_area_figure()
    rms_vector_geometry_figure()
    geometry_metrics_figure()
    bootstrap_scheme_figure()
    for filename in (
        "methodology_flow.png",
        "bin_grid_real_state.png",
        "coordinate_frames_example.png",
        "binning_entropy_example.png",
        "concentration_area_example.png",
        "rms_vector_geometry.png",
        "geometric_metrics_example.png",
        "bootstrap_scheme.png",
    ):
        print(f"Wrote {(OUTPUT / filename).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
