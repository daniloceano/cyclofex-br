"""Create the first exploratory products for the track-linked exceedance data.

Run from anywhere with:
    .venv/bin/python scripts/02_exploratory_analysis/exploratory_analysis.py

The script queries the Parquet with DuckDB, writes compact tabular summaries,
creates static figures, and renders an MP4 for the cyclone containing the
largest observed wind speed. It does not fit or evaluate a scientific model.
"""

from collections import defaultdict
import csv
from hashlib import sha256
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

import cartopy.crs as ccrs
from cartopy.geodesic import Geodesic
import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, LogNorm, Normalize
from matplotlib.patches import Patch
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "cyclone_exceedances_by_track_2010_2020_p90.parquet"
OUTPUT = ROOT / "outputs" / "02_exploratory_analysis"
DASHBOARD_ASSETS = ROOT / "dashboard" / "assets" / "02_exploratory_analysis"
RADIUS_KM = 1_100
COASTLINE_RESOLUTION = "50m"
ANIMATION_FPS = 3

PHASE_ORDER = (
    "incipient",
    "intensification",
    "mature",
    "decay",
    "residual",
    "missing",
)
PHASE_LABELS = {
    "incipient": "incipiente",
    "intensification": "intensificação",
    "mature": "madura",
    "decay": "decaimento",
    "residual": "residual",
    "missing": "ausente",
}
PHASE_COLORS = {
    "incipient": "#8ecae6",          # azul-claro solicitado
    "intensification": "#f6c945",   # amarelo solicitado
    "mature": "#d73027",            # vermelho solicitado
    "decay": "#9bd77a",             # verde-claro solicitado
    "residual": "#a78bca",
    "missing": "#8c969d",
}
EXTREME_COLORS = (
    "#FDF5D0",
    "#FCEAA1",
    "#F8E070",
    "#F4B354",
    "#EC8439",
    "#E05020",
    "#C84232",
    "#AF3540",
    "#96274B",
    "#7C1B55",
    "#600F5F",
    "#3E0668",
)
EXTREME_CMAP = ListedColormap(EXTREME_COLORS, name="cyclofex_extremes")
QUADRANT_COLORS = {1: "#2979b9", 2: "#f0a202", 3: "#d1495b", 4: "#2a9d70"}
FIXED_QUADRANT_LABELS = {1: "1 · NO", 2: "2 · NE", 3: "3 · SE", 4: "4 · SO"}
ROTATED_QUADRANT_LABELS = {
    1: "1 · frente-esq.",
    2: "2 · frente-dir.",
    3: "3 · trás-dir.",
    4: "4 · trás-esq.",
}
THRESHOLDS = (
    ("exceeded_15_6", ">15,6 m/s"),
    ("exceeded_20_0", ">20,0 m/s"),
    ("exceeded_25_0", ">25,0 m/s"),
    ("exceeded_q95", ">q95 local"),
    ("exceeded_q99", ">q99 local"),
)

PHASE_SQL = """
CASE
    WHEN phase IS NULL THEN 'missing'
    WHEN phase LIKE 'intensification%' THEN 'intensification'
    WHEN phase LIKE 'mature%' THEN 'mature'
    WHEN phase LIKE 'decay%' THEN 'decay'
    ELSE phase
END
"""


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parquet_relation() -> str:
    escaped = INPUT.as_posix().replace("'", "''")
    return f"read_parquet('{escaped}')"


def ordered(rows, key_index=0):
    position = {phase: index for index, phase in enumerate(PHASE_ORDER)}
    return sorted(rows, key=lambda row: position.get(row[key_index], len(position)))


def write_csv(path: Path, columns: list[str], rows: list[tuple]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(columns)
        writer.writerows(rows)


def format_count(value: float) -> str:
    value = float(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f} mi"
    if value >= 1_000:
        return f"{value / 1_000:.0f} mil"
    return f"{value:.0f}"


def setup_geo_axis(ax, extent, left_labels=True, bottom_labels=True) -> None:
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.coastlines(resolution=COASTLINE_RESOLUTION, linewidth=0.65, color="#40535d")
    gridlines = ax.gridlines(
        crs=ccrs.PlateCarree(),
        draw_labels=True,
        linewidth=0.35,
        color="#83949d",
        alpha=0.55,
        linestyle="--",
    )
    gridlines.top_labels = False
    gridlines.right_labels = False
    gridlines.left_labels = left_labels
    gridlines.bottom_labels = bottom_labels
    gridlines.xlabel_style = {"size": 7}
    gridlines.ylabel_style = {"size": 7}


def phase_statistics(connection, source: str) -> tuple[list[str], list[tuple]]:
    columns = [
        "phase_group",
        "cyclone_count",
        "cyclone_timestep_count",
        "point_row_count",
        "wind_mean_ms",
        "wind_p05_ms",
        "wind_p25_ms",
        "wind_median_ms",
        "wind_p75_ms",
        "wind_p95_ms",
        "exceeded_15_6_count",
        "exceeded_20_0_count",
        "exceeded_25_0_count",
        "exceeded_q90_count",
        "exceeded_q95_count",
        "exceeded_q99_count",
    ]
    rows = connection.execute(
        f"""
        SELECT
            {PHASE_SQL} AS phase_group,
            count(DISTINCT track_id) AS cyclone_count,
            count(DISTINCT (track_id, time)) AS cyclone_timestep_count,
            count(*) AS point_row_count,
            avg(wind_speed) AS wind_mean_ms,
            quantile_cont(wind_speed, 0.05) AS wind_p05_ms,
            quantile_cont(wind_speed, 0.25) AS wind_p25_ms,
            quantile_cont(wind_speed, 0.50) AS wind_median_ms,
            quantile_cont(wind_speed, 0.75) AS wind_p75_ms,
            quantile_cont(wind_speed, 0.95) AS wind_p95_ms,
            sum(exceeded_15_6::BIGINT),
            sum(exceeded_20_0::BIGINT),
            sum(exceeded_25_0::BIGINT),
            sum(exceeded_q90::BIGINT),
            sum(exceeded_q95::BIGINT),
            sum(exceeded_q99::BIGINT)
        FROM {source}
        GROUP BY phase_group
        """
    ).fetchall()
    return columns, ordered(rows)


def quadrant_statistics(connection, source: str) -> tuple[list[str], list[tuple]]:
    columns = [
        "coordinate_system",
        "quadrant",
        "point_row_count",
        "wind_mean_ms",
        "wind_p05_ms",
        "wind_p25_ms",
        "wind_median_ms",
        "wind_p75_ms",
        "wind_p95_ms",
        "exceeded_15_6_count",
        "exceeded_20_0_count",
        "exceeded_25_0_count",
        "exceeded_q90_count",
        "exceeded_q95_count",
        "exceeded_q99_count",
    ]
    query = """
        SELECT
            {system!r} AS coordinate_system,
            {quadrant} AS quadrant,
            count(*) AS point_row_count,
            avg(wind_speed) AS wind_mean_ms,
            quantile_cont(wind_speed, 0.05) AS wind_p05_ms,
            quantile_cont(wind_speed, 0.25) AS wind_p25_ms,
            quantile_cont(wind_speed, 0.50) AS wind_median_ms,
            quantile_cont(wind_speed, 0.75) AS wind_p75_ms,
            quantile_cont(wind_speed, 0.95) AS wind_p95_ms,
            sum(exceeded_15_6::BIGINT),
            sum(exceeded_20_0::BIGINT),
            sum(exceeded_25_0::BIGINT),
            sum(exceeded_q90::BIGINT),
            sum(exceeded_q95::BIGINT),
            sum(exceeded_q99::BIGINT)
        FROM {source}
        GROUP BY {quadrant}
    """
    fixed = connection.execute(
        query.format(system="fixed", quadrant="fixed_quadrant", source=source)
    ).fetchall()
    rotated = connection.execute(
        query.format(system="rotated", quadrant="rotated_quadrant", source=source)
    ).fetchall()
    return columns, sorted(fixed + rotated, key=lambda row: (row[0], row[1]))


def cyclone_state_exceedances(connection, source: str) -> tuple[list[str], list[tuple]]:
    columns = ["phase_group", "cyclone_timestep_count"] + [name for name, _ in THRESHOLDS]
    bool_columns = ",\n".join(
        f"bool_or({name}) AS {name}" for name, _ in THRESHOLDS
    )
    sum_columns = ",\n".join(
        f"sum({name}::BIGINT) AS {name}" for name, _ in THRESHOLDS
    )
    rows = connection.execute(
        f"""
        WITH states AS (
            SELECT
                {PHASE_SQL} AS phase_group,
                track_id,
                time,
                {bool_columns}
            FROM {source}
            GROUP BY phase_group, track_id, time
        )
        SELECT phase_group, count(*) AS cyclone_timestep_count, {sum_columns}
        FROM states
        GROUP BY phase_group
        """
    ).fetchall()
    return columns, ordered(rows)


def phase_quadrant_exceedances(connection, source: str) -> list[tuple]:
    rows = []
    for system, column in (("fixed", "fixed_quadrant"), ("rotated", "rotated_quadrant")):
        rows.extend(
            connection.execute(
                f"""
                SELECT
                    {system!r} AS coordinate_system,
                    {PHASE_SQL} AS phase_group,
                    {column} AS quadrant,
                    sum(exceeded_q90::BIGINT) AS q90_count,
                    avg(exceeded_q95::INTEGER) * 100 AS q95_rate_percent
                FROM {source}
                GROUP BY phase_group, quadrant
                """
            ).fetchall()
        )
    return rows


def all_track_states(connection, source: str) -> list[tuple]:
    return connection.execute(
        f"""
        SELECT
            track_id,
            time,
            {PHASE_SQL} AS phase_group,
            lat_center,
            lon_center
        FROM {source}
        GROUP BY track_id, time, phase_group, lat_center, lon_center
        ORDER BY track_id, time
        """
    ).fetchall()


def plot_all_tracks(track_states: list[tuple]) -> Path:
    tracks = defaultdict(list)
    for track_id, time, phase, lat, lon in track_states:
        tracks[track_id].append((time, phase, float(lat), float(lon)))

    segments = []
    colors = []
    for states in tracks.values():
        for previous, current in zip(states, states[1:]):
            segments.append([(previous[3], previous[2]), (current[3], current[2])])
            colors.append(PHASE_COLORS.get(current[1], PHASE_COLORS["missing"]))

    lats = [float(row[3]) for row in track_states]
    lons = [float(row[4]) for row in track_states]
    extent = [min(lons) - 3, max(lons) + 3, max(-90, min(lats) - 3), min(90, max(lats) + 3)]

    fig = plt.figure(figsize=(11.6, 7.8), constrained_layout=True)
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    setup_geo_axis(ax, extent)
    collection = LineCollection(segments, colors=colors, linewidths=0.55, alpha=0.58)
    collection.set_transform(ccrs.PlateCarree())
    ax.add_collection(collection)
    ax.set_title("Tracks disponíveis, coloridas pela fase do ciclo de vida", fontsize=14, pad=14)
    ax.text(
        0.01,
        0.015,
        f"{len(tracks):,} ciclones · {len(track_states):,} estados ciclone-tempo".replace(",", "."),
        transform=ax.transAxes,
        fontsize=8,
        bbox={"facecolor": "white", "edgecolor": "#ccd8dc", "alpha": 0.9, "pad": 5},
    )
    handles = [Patch(facecolor=PHASE_COLORS[p], label=PHASE_LABELS[p]) for p in PHASE_ORDER]
    ax.legend(handles=handles, loc="upper right", frameon=True, fontsize=8, title="Fase agrupada")
    target = OUTPUT / "all_tracks_by_phase.png"
    fig.savefig(target, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return target


def bxp_stats(rows, label_index, count_index, mean_index, p05_index, p25_index, median_index, p75_index, p95_index):
    return [
        {
            "label": str(row[label_index]),
            "mean": float(row[mean_index]),
            "whislo": float(row[p05_index]),
            "q1": float(row[p25_index]),
            "med": float(row[median_index]),
            "q3": float(row[p75_index]),
            "whishi": float(row[p95_index]),
            "fliers": [],
            "count": int(row[count_index]),
        }
        for row in rows
    ]


def draw_bxp(ax, stats, colors, title, labels) -> None:
    for stat, label in zip(stats, labels):
        stat["label"] = label
    artists = ax.bxp(stats, patch_artist=True, showmeans=True, showfliers=False)
    for box, color in zip(artists["boxes"], colors):
        box.set_facecolor(color)
        box.set_alpha(0.75)
        box.set_edgecolor("#334a55")
    for median in artists["medians"]:
        median.set_color("#112f3c")
        median.set_linewidth(1.8)
    for mean in artists["means"]:
        mean.set_marker("o")
        mean.set_markerfacecolor("white")
        mean.set_markeredgecolor("#112f3c")
        mean.set_markersize(4)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("Velocidade do vento a 10 m (m/s)")
    ax.grid(axis="y", color="#d7e0e3", linewidth=0.6)
    ax.tick_params(axis="x", labelrotation=28, labelsize=8)
    ax.text(0.01, 0.99, "caixas: P25–P75 · hastes: P5–P95 · ponto: média", transform=ax.transAxes,
            ha="left", va="top", fontsize=7, color="#536b79")


def plot_wind_boxplots(phase_rows: list[tuple], quadrant_rows: list[tuple]) -> Path:
    phase_stats = bxp_stats(phase_rows, 0, 3, 4, 5, 6, 7, 8, 9)
    phase_labels = [PHASE_LABELS.get(row[0], row[0]) for row in phase_rows]
    phase_colors = [PHASE_COLORS.get(row[0], PHASE_COLORS["missing"]) for row in phase_rows]

    fixed_rows = [row for row in quadrant_rows if row[0] == "fixed"]
    rotated_rows = [row for row in quadrant_rows if row[0] == "rotated"]
    fixed_stats = bxp_stats(fixed_rows, 1, 2, 3, 4, 5, 6, 7, 8)
    rotated_stats = bxp_stats(rotated_rows, 1, 2, 3, 4, 5, 6, 7, 8)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.1), constrained_layout=True)
    draw_bxp(axes[0], phase_stats, phase_colors, "Por fase agrupada", phase_labels)
    draw_bxp(
        axes[1],
        fixed_stats,
        [QUADRANT_COLORS[row[1]] for row in fixed_rows],
        "Por quadrante geográfico",
        [FIXED_QUADRANT_LABELS[row[1]] for row in fixed_rows],
    )
    draw_bxp(
        axes[2],
        rotated_stats,
        [QUADRANT_COLORS[row[1]] for row in rotated_rows],
        "Por quadrante relativo ao movimento",
        [ROTATED_QUADRANT_LABELS[row[1]] for row in rotated_rows],
    )
    fig.suptitle("Distribuições descritivas de wind_speed", fontsize=15)
    target = OUTPUT / "wind_speed_boxplots.png"
    fig.savefig(target, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return target


def plot_state_exceedances(state_rows: list[tuple]) -> Path:
    phases = [row[0] for row in state_rows]
    totals = np.asarray([row[1] for row in state_rows], dtype=float)
    values = np.asarray([row[2:] for row in state_rows], dtype=float)
    positions = np.arange(len(phases))
    width = 0.15
    colors = ("#8ecae6", "#4f86c6", "#ef8a62", "#8c6bb1", "#4a235a")

    fig, axes = plt.subplots(2, 1, figsize=(11.8, 8.1), sharex=True, constrained_layout=True)
    for index, ((_, label), color) in enumerate(zip(THRESHOLDS, colors)):
        offset = (index - (len(THRESHOLDS) - 1) / 2) * width
        axes[0].bar(positions + offset, values[:, index], width, label=label, color=color)
        axes[1].bar(positions + offset, values[:, index] / totals * 100, width, color=color)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("Número de estados ciclone-tempo (escala log)")
    axes[0].set_title("Estados com ao menos um ponto excedente")
    axes[0].legend(ncol=5, fontsize=8, loc="upper right")
    axes[1].set_ylabel("Percentual dos estados da fase (%)")
    axes[1].set_title("Fração dos estados da fase com excedência")
    axes[1].set_xticks(positions, [PHASE_LABELS.get(p, p) for p in phases], rotation=24, ha="right")
    for ax in axes:
        ax.grid(axis="y", color="#d7e0e3", linewidth=0.6)
    fig.suptitle("Ocorrência de excedências por fase", fontsize=15)
    target = OUTPUT / "exceedance_occurrence_by_phase.png"
    fig.savefig(target, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return target


def matrix_from_rows(rows, system, value_index):
    result = np.zeros((len(PHASE_ORDER), 4), dtype=float)
    lookup = {(row[1], int(row[2])): float(row[value_index]) for row in rows if row[0] == system}
    for phase_index, phase in enumerate(PHASE_ORDER):
        for quadrant in range(1, 5):
            result[phase_index, quadrant - 1] = lookup.get((phase, quadrant), 0.0)
    return result


def heatmap(ax, values, title, labels, norm, cmap, formatter):
    image = ax.imshow(values, aspect="auto", norm=norm, cmap=cmap)
    ax.set_xticks(np.arange(4), labels, rotation=20, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(PHASE_ORDER)), [PHASE_LABELS[p] for p in PHASE_ORDER], fontsize=8)
    ax.set_title(title, fontsize=10)
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            rgba = image.cmap(image.norm(values[row, column]))
            luminance = 0.2126 * rgba[0] + 0.7152 * rgba[1] + 0.0722 * rgba[2]
            ax.text(column, row, formatter(values[row, column]), ha="center", va="center",
                    color="black" if luminance > 0.55 else "white", fontsize=7)
    return image


def plot_phase_quadrant(rows: list[tuple]) -> Path:
    fixed_count = matrix_from_rows(rows, "fixed", 3)
    rotated_count = matrix_from_rows(rows, "rotated", 3)
    fixed_rate = matrix_from_rows(rows, "fixed", 4)
    rotated_rate = matrix_from_rows(rows, "rotated", 4)
    maximum_count = max(float(fixed_count.max()), float(rotated_count.max()))

    fig, axes = plt.subplots(2, 2, figsize=(12.4, 8.7), constrained_layout=True)
    count_norm = LogNorm(vmin=1, vmax=maximum_count)
    rate_norm = Normalize(vmin=0, vmax=max(float(fixed_rate.max()), float(rotated_rate.max())))
    count_1 = heatmap(axes[0, 0], fixed_count, "Pontos q90 · quadrante geográfico",
                      [FIXED_QUADRANT_LABELS[i] for i in range(1, 5)], count_norm, EXTREME_CMAP, format_count)
    heatmap(axes[0, 1], rotated_count, "Pontos q90 · quadrante relativo ao movimento",
            [ROTATED_QUADRANT_LABELS[i] for i in range(1, 5)], count_norm, EXTREME_CMAP, format_count)
    rate_1 = heatmap(axes[1, 0], fixed_rate, "Percentual q95 · quadrante geográfico",
                     [FIXED_QUADRANT_LABELS[i] for i in range(1, 5)], rate_norm, EXTREME_CMAP, lambda x: f"{x:.1f}%")
    heatmap(axes[1, 1], rotated_rate, "Percentual q95 · quadrante relativo ao movimento",
            [ROTATED_QUADRANT_LABELS[i] for i in range(1, 5)], rate_norm, EXTREME_CMAP, lambda x: f"{x:.1f}%")
    fig.colorbar(count_1, ax=axes[0, :], shrink=0.78, label="Contagem de pontos q90 (escala log)")
    fig.colorbar(rate_1, ax=axes[1, :], shrink=0.78, label="Pontos do recorte que também excedem q95 (%)")
    fig.suptitle("Excedências por fase e quadrante", fontsize=15)
    target = OUTPUT / "exceedances_by_phase_and_quadrant.png"
    fig.savefig(target, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return target


def animation_extent(centers: list[dict]) -> list[float]:
    lat_padding = RADIUS_KM / 111.0
    lower_lats = [state["lat_center"] - lat_padding for state in centers]
    upper_lats = [state["lat_center"] + lat_padding for state in centers]
    lower_lons = []
    upper_lons = []
    for state in centers:
        cosine = max(math.cos(math.radians(abs(state["lat_center"]))), 0.15)
        lon_padding = RADIUS_KM / (111.0 * cosine)
        lower_lons.append(state["lon_center"] - lon_padding)
        upper_lons.append(state["lon_center"] + lon_padding)
    return [
        max(-180, min(lower_lons) - 1),
        min(180, max(upper_lons) + 1),
        max(-90, min(lower_lats) - 1),
        min(90, max(upper_lats) + 1),
    ]


def selected_cyclone(connection, source: str) -> tuple[dict, list[dict]]:
    maximum = connection.execute(
        f"""
        SELECT track_id, time, {PHASE_SQL} AS phase_group, lat_center, lon_center,
               lat, lon, wind_speed
        FROM {source}
        ORDER BY wind_speed DESC, track_id, time, lat, lon
        LIMIT 1
        """
    ).fetchone()
    track_id = int(maximum[0])
    rows = connection.execute(
        f"""
        SELECT time, {PHASE_SQL} AS phase_group, lat_center, lon_center,
               lat, lon, wind_speed, fixed_quadrant, rotated_quadrant, exceeded_q90
        FROM {source}
        WHERE track_id = ?
        ORDER BY time, lat, lon
        """,
        [track_id],
    ).fetchall()
    groups = defaultdict(list)
    for row in rows:
        groups[row[0]].append(row)
    states = []
    for time in sorted(groups):
        group = groups[time]
        states.append(
            {
                "time": time,
                "phase": group[0][1],
                "lat_center": float(group[0][2]),
                "lon_center": float(group[0][3]),
                "max_wind_ms": max(float(row[6]) for row in group),
                "q90_points": [
                    {
                        "lat": float(row[4]),
                        "lon": float(row[5]),
                        "wind_speed": float(row[6]),
                        "fixed_quadrant": int(row[7]),
                        "rotated_quadrant": int(row[8]),
                    }
                    for row in group
                    if row[9]
                ],
            }
        )
    maximum_info = {
        "track_id": track_id,
        "time": maximum[1],
        "phase": maximum[2],
        "lat_center": float(maximum[3]),
        "lon_center": float(maximum[4]),
        "lat": float(maximum[5]),
        "lon": float(maximum[6]),
        "wind_speed_ms": float(maximum[7]),
    }
    return maximum_info, states


def motion_unit_vector(states: list[dict], index: int) -> tuple[float, float]:
    """Reproduce the unit motion vector used to create rotated_quadrant."""
    start_index = max(index - 1, 0)
    end_index = min(index + 1, len(states) - 1)
    if start_index == end_index:
        return 1.0, 0.0
    start = states[start_index]
    end = states[end_index]
    delta_lon = (end["lon_center"] - start["lon_center"] + 180.0) % 360.0 - 180.0
    delta_x = delta_lon * math.cos(math.radians(states[index]["lat_center"]))
    delta_y = end["lat_center"] - start["lat_center"]
    magnitude = math.hypot(delta_x, delta_y)
    if magnitude == 0.0:
        return 1.0, 0.0
    return delta_x / magnitude, delta_y / magnitude


def motion_bearing(states: list[dict], index: int) -> float:
    """Convert the generator's east/north motion vector to a map bearing."""
    unit_east, unit_north = motion_unit_vector(states, index)
    return math.degrees(math.atan2(unit_east, unit_north))


def draw_quadrant_sectors(ax, geodesic: Geodesic, state: dict, heading: float, labels: dict) -> None:
    """Draw four 90-degree sectors without obscuring the wind field."""
    center = [[state["lon_center"], state["lat_center"]]]
    boundaries = geodesic.direct(
        center,
        np.asarray([heading, heading + 90, heading + 180, heading + 270]),
        np.repeat(RADIUS_KM * 1_000, 4),
    )
    for lon, lat, _ in boundaries:
        ax.plot(
            [state["lon_center"], lon],
            [state["lat_center"], lat],
            color="#263f4b",
            linewidth=0.9,
            alpha=0.9,
            transform=ccrs.Geodetic(),
            zorder=5,
        )

    label_points = geodesic.direct(
        center,
        np.asarray([heading - 45, heading + 45, heading + 135, heading + 225]),
        np.repeat(RADIUS_KM * 650, 4),
    )
    for quadrant, (lon, lat, _) in enumerate(label_points, start=1):
        label = labels[quadrant].split("·", 1)[-1].strip()
        ax.text(
            lon,
            lat,
            label,
            ha="center",
            va="center",
            fontsize=6.8,
            fontweight="bold",
            color="#263f4b",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.72, "pad": 1.4},
            transform=ccrs.PlateCarree(),
            zorder=6,
        )


def render_animation(maximum: dict, states: list[dict]) -> tuple[Path, Path, list[float]]:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to create the MP4 animation")
    extent = animation_extent(states)
    geodesic = Geodesic()
    path_lons = [state["lon_center"] for state in states]
    path_lats = [state["lat_center"] for state in states]
    max_time = maximum["time"]
    wind_values = [
        point["wind_speed"]
        for state in states
        for point in state["q90_points"]
    ]
    wind_norm = Normalize(vmin=min(wind_values), vmax=max(wind_values))
    video = OUTPUT / "max_wind_cyclone_animation.mp4"
    poster = OUTPUT / "max_wind_cyclone_peak_frame.png"

    with tempfile.TemporaryDirectory(prefix="cyclofex_frames_", dir=OUTPUT) as temporary:
        frame_dir = Path(temporary)
        for index, state in enumerate(states):
            fig = plt.figure(figsize=(13.8, 6.7), constrained_layout=True)
            axes = [
                fig.add_subplot(1, 2, 1, projection=ccrs.PlateCarree()),
                fig.add_subplot(1, 2, 2, projection=ccrs.PlateCarree()),
            ]
            points = state["q90_points"]
            circle = geodesic.circle(
                lon=state["lon_center"],
                lat=state["lat_center"],
                radius=RADIUS_KM * 1_000,
                n_samples=180,
                endpoint=True,
            )
            track_heading = motion_bearing(states, index)
            for axis_index, (ax, heading, title, labels) in enumerate(
                (
                    (axes[0], 0.0, "Quadrantes geográficos fixos", FIXED_QUADRANT_LABELS),
                    (axes[1], track_heading, "Quadrantes relativos ao movimento", ROTATED_QUADRANT_LABELS),
                )
            ):
                setup_geo_axis(ax, extent, left_labels=axis_index == 0, bottom_labels=True)
                ax.plot(path_lons, path_lats, color="#7f8d93", linewidth=1.0, linestyle="--",
                        transform=ccrs.PlateCarree(), zorder=3)
                ax.plot(path_lons[: index + 1], path_lats[: index + 1], color="#172f3c", linewidth=2.1,
                        transform=ccrs.PlateCarree(), zorder=4)
                ax.plot(circle[:, 0], circle[:, 1], color="#263f4b", linewidth=1.15,
                        transform=ccrs.PlateCarree(), zorder=5)
                ax.scatter(
                    [point["lon"] for point in points],
                    [point["lat"] for point in points],
                    c=[point["wind_speed"] for point in points],
                    norm=wind_norm,
                    cmap=EXTREME_CMAP,
                    s=6.0,
                    marker="s",
                    alpha=0.82,
                    linewidths=0,
                    transform=ccrs.PlateCarree(),
                    zorder=2,
                )
                draw_quadrant_sectors(ax, geodesic, state, heading, labels)
                ax.scatter(
                    [state["lon_center"]],
                    [state["lat_center"]],
                    s=95,
                    color=PHASE_COLORS.get(state["phase"], PHASE_COLORS["missing"]),
                    edgecolor="#142b3d",
                    linewidth=1.2,
                    transform=ccrs.PlateCarree(),
                    zorder=7,
                )
                ax.set_title(title, fontsize=11)
                ax.text(
                    0.015,
                    0.018,
                    f"fase: {PHASE_LABELS.get(state['phase'], state['phase'])}\n"
                    f"máx. no instante: {state['max_wind_ms']:.2f} m/s\n"
                    f"pontos q90: {len(points):,}".replace(",", "."),
                    transform=ax.transAxes,
                    fontsize=7.5,
                    bbox={"facecolor": "white", "edgecolor": "#ccd8dc", "alpha": 0.91, "pad": 4},
                    zorder=8,
                )
            colorbar = fig.colorbar(
                plt.cm.ScalarMappable(norm=wind_norm, cmap=EXTREME_CMAP),
                ax=axes,
                orientation="horizontal",
                location="bottom",
                shrink=0.65,
                pad=0.035,
            )
            colorbar.set_label("Velocidade do vento nos pontos q90 (m/s)", fontsize=9)
            colorbar.ax.tick_params(labelsize=8)
            phase_label = PHASE_LABELS.get(state["phase"], state["phase"])
            fig.suptitle(
                f"Ciclone {maximum['track_id']} · {state['time']:%Y-%m-%d %H:%M} UTC · fase {phase_label}\n"
                f"Pontos com exceeded_q90 = true e raio de {RADIUS_KM:,} km".replace(",", "."),
                fontsize=14,
            )
            frame = frame_dir / f"frame_{index:03d}.png"
            fig.savefig(frame, dpi=145, bbox_inches="tight", facecolor="white")
            plt.close(fig)
            if state["time"] == max_time:
                shutil.copy2(frame, poster)

        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-framerate",
                str(ANIMATION_FPS),
                "-i",
                str(frame_dir / "frame_%03d.png"),
                "-c:v",
                "libx264",
                "-vf",
                "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(video),
            ],
            check=True,
        )
    return video, poster, extent


def json_value(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def publish_dashboard_assets() -> None:
    """Copy browser-facing artifacts under dashboard so local previews can load them."""
    DASHBOARD_ASSETS.mkdir(parents=True, exist_ok=True)
    for source in OUTPUT.iterdir():
        if source.is_file() and source.suffix.lower() in {".png", ".mp4", ".csv", ".json"}:
            shutil.copy2(source, DASHBOARD_ASSETS / source.name)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    source = parquet_relation()
    connection = duckdb.connect()

    phase_columns, phase_rows = phase_statistics(connection, source)
    quadrant_columns, quadrant_rows = quadrant_statistics(connection, source)
    state_columns, state_rows = cyclone_state_exceedances(connection, source)
    phase_quadrant_rows = phase_quadrant_exceedances(connection, source)
    track_states = all_track_states(connection, source)
    maximum, selected_states = selected_cyclone(connection, source)

    write_csv(OUTPUT / "phase_statistics.csv", phase_columns, phase_rows)
    write_csv(OUTPUT / "quadrant_statistics.csv", quadrant_columns, quadrant_rows)
    write_csv(OUTPUT / "cyclone_timestep_exceedances_by_phase.csv", state_columns, state_rows)
    write_csv(
        OUTPUT / "phase_quadrant_exceedances.csv",
        ["coordinate_system", "phase_group", "quadrant", "q90_point_count", "q95_rate_percent"],
        phase_quadrant_rows,
    )

    figures = {
        "all_tracks": plot_all_tracks(track_states).name,
        "wind_boxplots": plot_wind_boxplots(phase_rows, quadrant_rows).name,
        "state_exceedances": plot_state_exceedances(state_rows).name,
        "phase_quadrant": plot_phase_quadrant(phase_quadrant_rows).name,
    }
    video, poster, extent = render_animation(maximum, selected_states)
    total_rows = connection.execute(f"SELECT count(*) FROM {source}").fetchone()[0]
    unique_cyclones = connection.execute(f"SELECT count(DISTINCT track_id) FROM {source}").fetchone()[0]
    connection.close()

    summary = {
        "input": str(INPUT.relative_to(ROOT)),
        "input_sha256": file_sha256(INPUT),
        "unit_of_analysis": "cyclone identified by unique track_id",
        "cyclone_count": unique_cyclones,
        "cyclone_timestep_count": len(track_states),
        "point_row_count": total_rows,
        "phase_grouping": {
            "intensification": ["intensification", "intensification 2"],
            "mature": ["mature", "mature 2"],
            "decay": ["decay", "decay 2"],
            "incipient": ["incipient"],
            "residual": ["residual"],
            "missing": [None],
        },
        "animation": {
            "selection_rule": "track_id of the global maximum wind_speed row",
            "track_id": maximum["track_id"],
            "global_maximum": {key: json_value(value) for key, value in maximum.items()},
            "track_start": selected_states[0]["time"].isoformat(),
            "track_end": selected_states[-1]["time"].isoformat(),
            "cyclone_timestep_count": len(selected_states),
            "radius_km": RADIUS_KM,
            "map_extent_lon_min_lon_max_lat_min_lat_max": extent,
            "video": video.name,
            "poster": poster.name,
            "fps": ANIMATION_FPS,
            "wind_speed_color_scale": list(EXTREME_COLORS),
            "fixed_sector_heading_degrees": 0,
            "rotated_sector_direction": (
                "centered displacement over neighboring 6 h track states, simple difference at "
                "endpoints, longitude scaled by cos(current latitude), east fallback for zero motion"
            ),
        },
        "figures": figures,
        "notes": [
            "Boxplots describe point rows; they are not inferential summaries of independent observations.",
            "Exceedance occurrence counts use unique track_id/time states.",
            "Animation points are rows with exceeded_q90=true and are colored by wind_speed.",
            "Quadrants are drawn as sector boundaries; the rotated panel reproduces the direction convention used to generate rotated_quadrant.",
            "The p90 reference is experimental and will be recalculated for 1979-2020.",
        ],
    }
    (OUTPUT / "analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    publish_dashboard_assets()
    print(f"Wrote exploratory outputs to {OUTPUT.relative_to(ROOT)}")
    print(f"Published dashboard assets to {DASHBOARD_ASSETS.relative_to(ROOT)}")
    print(
        f"Selected track {maximum['track_id']} with maximum wind "
        f"{maximum['wind_speed_ms']:.3f} m/s at {maximum['time']}"
    )


if __name__ == "__main__":
    main()
