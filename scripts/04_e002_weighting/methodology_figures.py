#!/usr/bin/env python3
"""Create didactic methodology figures for the E-002 scientific report.

The figures explain the frozen protocol; they do not recompute or alter the
experiment results. Numbers shown in the hierarchy schematic are a small
illustrative example, not E-002 output. Run from any directory with::

    .venv/bin/python scripts/04_e002_weighting/methodology_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs" / "04_e002_weighting"

INK = "#21323d"
MUTED = "#647783"
BLUE = "#3178a8"
TEAL = "#2a8c82"
ORANGE = "#d8862f"
RED = "#b84b45"
PURPLE = "#7653a6"
GRID = "#cbd5da"
WHITE = "#ffffff"


def save(figure: plt.Figure, filename: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT / filename, dpi=190, bbox_inches="tight", facecolor=WHITE)
    plt.close(figure)


def node(axis, x, y, width, height, title, detail, color) -> None:
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.025,rounding_size=0.08",
        linewidth=1.4, edgecolor=color, facecolor=WHITE,
    )
    axis.add_patch(box)
    axis.add_patch(Rectangle((x, y + height - 0.18), width, 0.18, facecolor=color, edgecolor="none"))
    axis.text(x + 0.18, y + height - 0.39, title, ha="left", va="top", color=INK, fontsize=11.5, fontweight="bold")
    axis.text(x + width / 2, y + 0.47, detail, ha="center", va="center", color=MUTED, fontsize=10.3, linespacing=1.35)


def workflow_figure() -> None:
    """Scientific flow of E-002, from the question to the robustness verdict."""
    figure, axis = plt.subplots(figsize=(15.5, 7.2))
    axis.set_xlim(0, 15.5)
    axis.set_ylim(0, 7.2)
    axis.axis("off")

    nodes = [
        (0.35, 4.65, 3.0, 1.45, "1 · Pergunta", "a estrutura q95 depende\nde quem recebe peso igual?", BLUE),
        (4.15, 4.65, 3.0, 1.45, "2 · Protocolo herdado", "população, q95, suporte, heading,\ncoordenadas e bins de E-001", PURPLE),
        (7.95, 4.65, 3.0, 1.45, "3 · Auditoria", "recontar ciclones, estados,\ncélulas e exclusões", TEAL),
        (11.75, 4.65, 3.0, 1.45, "4 · Dois weightings", "equal-state ↔ equal-cyclone\na única mudança é o peso", ORANGE),
        (11.75, 1.15, 3.0, 1.45, "5 · Quatro distribuições", "2 orientações × 2 weightings\nna mesma grade de 50 km", BLUE),
        (7.95, 1.15, 3.0, 1.45, "6 · Avaliação", "H · A50/75/90 · RMS\nconcentração entre ciclones\ne distância de variação total", PURPLE),
        (4.15, 1.15, 3.0, 1.45, "7 · Incerteza", "500 réplicas reamostradas\npor track_id", TEAL),
        (0.35, 1.15, 3.0, 1.45, "8 · Decisão", "robusto, parcialmente\nsensível ou sensível", RED),
    ]
    for item in nodes:
        node(axis, *item)

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

    axis.text(7.75, 6.85, "Fluxo lógico de E-002", ha="center", va="center", color=INK, fontsize=16, fontweight="bold")
    axis.text(
        7.75, 0.35,
        "A geometria e a população vêm congeladas de E-001; só o peso atribuído a estados e ciclones muda entre os dois braços.",
        ha="center", va="center", color=MUTED, fontsize=10.5,
    )
    save(figure, "methodology_flow.png")


def hierarchy_figure() -> None:
    """Worked example of the cyclone -> state -> cell -> bin weighting hierarchy."""
    # Illustrative population: cyclone A has two positive states, cyclone B one.
    states = [
        ("Ciclone A", "Estado A1", 4, BLUE),
        ("Ciclone A", "Estado A2", 2, BLUE),
        ("Ciclone B", "Estado B1", 3, TEAL),
    ]
    n_states = {"Ciclone A": 2, "Ciclone B": 1}

    figure, axes = plt.subplots(1, 2, figsize=(14.6, 6.4), constrained_layout=True)
    figure.suptitle(
        "Exemplo esquemático · como o peso desce de ciclone para célula",
        fontsize=15, fontweight="bold", color=INK,
    )

    for axis, scheme in zip(axes, ("equal-state", "equal-cyclone")):
        axis.set_xlim(0, 10)
        axis.set_ylim(0, 8.4)
        axis.axis("off")
        axis.set_title(
            "A · Equal-state" if scheme == "equal-state" else "B · Equal-cyclone",
            fontsize=12.5, color=INK, fontweight="bold",
        )

        total = 3.0 if scheme == "equal-state" else 2.0
        y = 7.1
        for cyclone, state, cells, color in states:
            state_weight = 1.0 if scheme == "equal-state" else 1.0 / n_states[cyclone]
            cell_weight = state_weight / cells

            axis.text(0.15, y + 0.22, f"{cyclone} · {state}", ha="left", va="center",
                      color=color, fontsize=11, fontweight="bold")
            axis.text(9.85, y + 0.22, f"peso do estado = {state_weight:.3f}".replace(".", ","),
                      ha="right", va="center", color=INK, fontsize=10.5)

            for index in range(cells):
                x = 0.35 + index * 1.62
                box = FancyBboxPatch(
                    (x, y - 0.95), 1.42, 0.78,
                    boxstyle="round,pad=0.02,rounding_size=0.06",
                    linewidth=1.3, edgecolor=color, facecolor=WHITE,
                )
                axis.add_patch(box)
                axis.text(x + 0.71, y - 0.56, f"{cell_weight:.4f}".replace(".", ","),
                          ha="center", va="center", color=INK, fontsize=10.5, fontweight="bold")
            axis.text(0.35 + cells * 1.62 + 0.12, y - 0.56,
                      f"{cells} células", ha="left", va="center", color=MUTED, fontsize=9.8)
            y -= 1.72

        # Totals per cyclone and overall, before global normalisation.
        axis.plot([0.2, 9.8], [y + 0.72, y + 0.72], color=GRID, linewidth=1.2)
        weight_a = sum(
            (1.0 if scheme == "equal-state" else 1.0 / n_states[c])
            for c, _, _, _ in states if c == "Ciclone A"
        )
        weight_b = sum(
            (1.0 if scheme == "equal-state" else 1.0 / n_states[c])
            for c, _, _, _ in states if c == "Ciclone B"
        )
        axis.text(0.2, y + 0.28, "Peso total do ciclone A", ha="left", va="center", color=INK, fontsize=10.6)
        axis.text(9.8, y + 0.28, f"{weight_a:.3f}".replace(".", ","), ha="right", va="center",
                  color=INK, fontsize=10.6, fontweight="bold")
        axis.text(0.2, y - 0.22, "Peso total do ciclone B", ha="left", va="center", color=INK, fontsize=10.6)
        axis.text(9.8, y - 0.22, f"{weight_b:.3f}".replace(".", ","), ha="right", va="center",
                  color=INK, fontsize=10.6, fontweight="bold")

        share_a = weight_a / total
        share_b = weight_b / total
        axis.text(0.2, y - 0.86, "Contribuição final ao mapa", ha="left", va="center",
                  color=INK, fontsize=10.6, fontweight="bold")
        axis.text(
            9.8, y - 0.86,
            f"A = {share_a * 100:.1f}%  ·  B = {share_b * 100:.1f}%".replace(".", ","),
            ha="right", va="center", color=ORANGE if scheme == "equal-state" else TEAL,
            fontsize=11, fontweight="bold",
        )
        axis.text(
            5.0, y - 1.52,
            "Cada estado positivo vale 1; o ciclone A entra duas vezes."
            if scheme == "equal-state"
            else "Cada ciclone vale 1; os estados de A dividem esse peso.",
            ha="center", va="center", color=MUTED, fontsize=10.2,
        )

    save(figure, "weighting_hierarchy_example.png")


def main() -> None:
    workflow_figure()
    hierarchy_figure()
    for filename in ("methodology_flow.png", "weighting_hierarchy_example.png"):
        print(f"Wrote {(OUTPUT / filename).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
