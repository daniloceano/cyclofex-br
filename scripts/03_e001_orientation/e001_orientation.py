#!/usr/bin/env python3
"""Run E-001: centered versus motion-relative exceedance organization.

The protocol is frozen in ``protocol.json``.  This script uses the complete
canonical 6-hour state catalog for motion, the q95 flags from the conditioned
wind Parquet for exceedances, reconstructs spatial support from the documented
ERA5 grid, and bootstraps paired differences by cyclone.

Run from any directory::

    .venv/bin/python scripts/03_e001_orientation/e001_orientation.py
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
from typing import Any

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
PROTOCOL_PATH = SCRIPT_DIR / "protocol.json"
STATES_PATH = ROOT / "data" / "cyclone_states_era5_6h_1979_2020.parquet"
TRACKS_PATH = ROOT / "data" / "tracks_SAt_1979_2020.parquet"
WIND_PATH = ROOT / "data" / "cyclone_exceedances_by_track_2010_2020_p90.parquet"
OUTPUT = ROOT / "outputs" / "03_e001_orientation"

EXPECTED_HASHES = {
    STATES_PATH.name: "4865bbc39f273d2360b5735cb26b132d9d01e7af085df94e08fdcd16ce864782",
    TRACKS_PATH.name: "7d8d628a8d54f9273e1c6280f22bb0082a470d4767393bd3b224a64e8a71c553",
    WIND_PATH.name: "3913a1d8ab49856212e1e5a19275b3644ae947dcf940872fb2f40a884d9efa0c",
}

EARTH_RADIUS_KM = 6_371.0
GRID_LAT_MIN = -65.0
GRID_LAT_MAX = -10.0
GRID_LON_MIN = -85.0
GRID_LON_MAX = -15.0
GRID_STEP_DEG = 0.25
PHASES = ("incipient", "intensification", "mature", "decay")
PHASE_LABELS = {
    "all": "Todos os estados",
    "full_support": "Somente suporte completo",
    "incipient": "Incipiente",
    "intensification": "Intensificação",
    "mature": "Madura",
    "decay": "Decaimento",
}
METRIC_DIRECTIONS = {
    "entropy_nats": "lower",
    "area50_km2": "lower",
    "area75_km2": "lower",
    "area90_km2": "lower",
    "rms_about_centroid_km": "lower",
    "centroid_x_km": "descriptive",
    "centroid_y_km": "descriptive",
    "centroid_distance_km": "descriptive",
    "anisotropy_axis_ratio": "descriptive",
}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def wrapped_longitude_delta(lon: np.ndarray, lon0: np.ndarray) -> np.ndarray:
    """Return lon-lon0 in degrees on [-180, 180)."""
    return (lon - lon0 + 180.0) % 360.0 - 180.0


def local_xy_km(
    lat0: np.ndarray | float,
    lon0: np.ndarray | float,
    lat: np.ndarray | float,
    lon: np.ndarray | float,
) -> tuple[np.ndarray, np.ndarray]:
    """Spherical azimuthal-equidistant coordinates about (lat0, lon0).

    x is positive east and y positive north.  The radial distance is the
    haversine great-circle distance on a sphere of radius 6,371 km.
    """
    lat0_rad = np.radians(lat0)
    lat_rad = np.radians(lat)
    dlat = lat_rad - lat0_rad
    dlon = np.radians(wrapped_longitude_delta(np.asarray(lon), np.asarray(lon0)))
    hav = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lat0_rad) * np.cos(lat_rad) * np.sin(dlon / 2.0) ** 2
    )
    hav = np.clip(hav, 0.0, 1.0)
    distance = EARTH_RADIUS_KM * 2.0 * np.arctan2(np.sqrt(hav), np.sqrt(1.0 - hav))
    east_term = np.sin(dlon) * np.cos(lat_rad)
    north_term = (
        np.cos(lat0_rad) * np.sin(lat_rad)
        - np.sin(lat0_rad) * np.cos(lat_rad) * np.cos(dlon)
    )
    bearing = np.arctan2(east_term, north_term)
    return distance * np.sin(bearing), distance * np.cos(bearing)


def rotate_motion(x: np.ndarray, y: np.ndarray, heading_rad: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rotate east/north coordinates to right/forward coordinates."""
    cosine = np.cos(heading_rad)
    sine = np.sin(heading_rad)
    return x * cosine - y * sine, x * sine + y * cosine


def inverse_rotate_motion(
    x_motion: np.ndarray,
    y_motion: np.ndarray,
    heading_rad: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Invert :func:`rotate_motion`."""
    cosine = np.cos(heading_rad)
    sine = np.sin(heading_rad)
    return x_motion * cosine + y_motion * sine, -x_motion * sine + y_motion * cosine


def phase_group(value: str | None) -> str:
    if value is None:
        return "missing"
    for phase in PHASES:
        if value == phase or value == f"{phase} 2":
            return phase
    return value


def compute_motion(
    track_id: np.ndarray,
    time_hours: np.ndarray,
    lat: np.ndarray,
    lon: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute centered/end-point local motion using the complete catalog."""
    count = track_id.size
    east = np.full(count, np.nan, dtype=np.float64)
    north = np.full(count, np.nan, dtype=np.float64)
    interval_hours = np.full(count, np.nan, dtype=np.float64)
    starts = np.r_[0, np.flatnonzero(track_id[1:] != track_id[:-1]) + 1]
    ends = np.r_[starts[1:], count]

    for start, end in zip(starts, ends, strict=True):
        size = end - start
        if size == 1:
            continue
        if size > 2:
            previous_x, previous_y = local_xy_km(
                lat[start + 1 : end - 1],
                lon[start + 1 : end - 1],
                lat[start : end - 2],
                lon[start : end - 2],
            )
            next_x, next_y = local_xy_km(
                lat[start + 1 : end - 1],
                lon[start + 1 : end - 1],
                lat[start + 2 : end],
                lon[start + 2 : end],
            )
            east[start + 1 : end - 1] = next_x - previous_x
            north[start + 1 : end - 1] = next_y - previous_y
            interval_hours[start + 1 : end - 1] = (
                time_hours[start + 2 : end] - time_hours[start : end - 2]
            )

        x, y = local_xy_km(lat[start], lon[start], lat[start + 1], lon[start + 1])
        east[start], north[start] = float(x), float(y)
        interval_hours[start] = time_hours[start + 1] - time_hours[start]

        x, y = local_xy_km(lat[end - 2], lon[end - 2], lat[end - 1], lon[end - 1])
        east[end - 1], north[end - 1] = float(x), float(y)
        interval_hours[end - 1] = time_hours[end - 1] - time_hours[end - 2]

    require(np.all(interval_hours[np.isfinite(interval_hours)] > 0), "Intervalo de movimento inválido")
    speed = np.hypot(east, north) / interval_hours
    heading = np.arctan2(east, north)
    return heading, speed, east, north


def bin_indices(
    x: np.ndarray,
    y: np.ndarray,
    domain_km: float,
    bin_km: float,
    bins_per_axis: int,
) -> tuple[np.ndarray, np.ndarray]:
    tolerance = 1e-6
    valid = (
        (x >= -domain_km - tolerance)
        & (x <= domain_km + tolerance)
        & (y >= -domain_km - tolerance)
        & (y <= domain_km + tolerance)
    )
    ix = np.floor((x + domain_km) / bin_km).astype(np.int32)
    iy = np.floor((y + domain_km) / bin_km).astype(np.int32)
    ix = np.clip(ix, 0, bins_per_axis - 1)
    iy = np.clip(iy, 0, bins_per_axis - 1)
    return iy[valid] * bins_per_axis + ix[valid], valid


def metric_values(mass: np.ndarray, x_centers: np.ndarray, y_centers: np.ndarray, bin_area: float) -> dict[str, float]:
    total = float(np.sum(mass))
    require(total > 0.0, "Massa espacial vazia")
    probability = np.asarray(mass, dtype=np.float64) / total
    positive = probability > 0.0
    entropy = float(-np.sum(probability[positive] * np.log(probability[positive])))
    ordered = np.sort(probability)[::-1]
    cumulative = np.cumsum(ordered)

    areas = {}
    for fraction in (0.50, 0.75, 0.90):
        bins_needed = int(np.searchsorted(cumulative, fraction, side="left") + 1)
        areas[f"area{int(fraction * 100)}_km2"] = bins_needed * bin_area

    mean_x = float(probability @ x_centers)
    mean_y = float(probability @ y_centers)
    dx = x_centers - mean_x
    dy = y_centers - mean_y
    covariance_xx = float(probability @ (dx * dx))
    covariance_yy = float(probability @ (dy * dy))
    covariance_xy = float(probability @ (dx * dy))
    eigenvalues = np.linalg.eigvalsh(
        np.array([[covariance_xx, covariance_xy], [covariance_xy, covariance_yy]])
    )
    anisotropy = float(math.sqrt(eigenvalues[1] / eigenvalues[0])) if eigenvalues[0] > 0 else math.inf
    return {
        "entropy_nats": entropy,
        **areas,
        "rms_about_centroid_km": float(math.sqrt(covariance_xx + covariance_yy)),
        "centroid_x_km": mean_x,
        "centroid_y_km": mean_y,
        "centroid_distance_km": float(math.hypot(mean_x, mean_y)),
        "anisotropy_axis_ratio": anisotropy,
        "occupied_bins": int(np.count_nonzero(positive)),
        "mass_total_state_equivalents": total,
    }


def bootstrap_metrics(
    centered: np.ndarray,
    motion: np.ndarray,
    x_centers: np.ndarray,
    y_centers: np.ndarray,
    bin_area: float,
    replicates: int,
    rng: np.random.Generator,
) -> tuple[list[dict[str, float]], dict[str, dict[str, float]]]:
    """Paired track bootstrap; rows are track-by-bin masses."""
    tracks = centered.shape[0]
    require(tracks > 1, "Estrato sem ciclones suficientes para bootstrap")
    multiplicity = rng.multinomial(tracks, np.full(tracks, 1.0 / tracks), size=replicates).astype(np.float32)
    centered_mass = multiplicity @ centered
    motion_mass = multiplicity @ motion
    centered_total = centered_mass.sum(axis=1)
    motion_total = motion_mass.sum(axis=1)
    valid = (centered_total > 0) & (motion_total > 0)
    require(np.all(valid), "Réplica bootstrap sem excedências")
    centered_p = centered_mass / centered_total[:, None]
    motion_p = motion_mass / motion_total[:, None]

    def matrix_metrics(probability: np.ndarray) -> dict[str, np.ndarray]:
        safe = np.where(probability > 0, probability, 1.0)
        result: dict[str, np.ndarray] = {
            "entropy_nats": -np.sum(np.where(probability > 0, probability * np.log(safe), 0.0), axis=1)
        }
        ordered = np.sort(probability, axis=1)[:, ::-1]
        cumulative = np.cumsum(ordered, axis=1)
        for fraction in (0.50, 0.75, 0.90):
            result[f"area{int(fraction * 100)}_km2"] = (
                np.argmax(cumulative >= fraction, axis=1) + 1
            ) * bin_area
        mean_x = probability @ x_centers
        mean_y = probability @ y_centers
        second_x = probability @ (x_centers * x_centers)
        second_y = probability @ (y_centers * y_centers)
        second_xy = probability @ (x_centers * y_centers)
        cov_xx = np.maximum(0.0, second_x - mean_x * mean_x)
        cov_yy = np.maximum(0.0, second_y - mean_y * mean_y)
        cov_xy = second_xy - mean_x * mean_y
        trace = cov_xx + cov_yy
        discriminant = np.sqrt(np.maximum(0.0, (cov_xx - cov_yy) ** 2 + 4.0 * cov_xy ** 2))
        lambda_max = (trace + discriminant) / 2.0
        lambda_min = np.maximum((trace - discriminant) / 2.0, np.finfo(float).eps)
        result.update(
            {
                "rms_about_centroid_km": np.sqrt(trace),
                "centroid_x_km": mean_x,
                "centroid_y_km": mean_y,
                "centroid_distance_km": np.hypot(mean_x, mean_y),
                "anisotropy_axis_ratio": np.sqrt(lambda_max / lambda_min),
            }
        )
        return result

    c_metrics = matrix_metrics(centered_p)
    m_metrics = matrix_metrics(motion_p)
    replicate_rows: list[dict[str, float]] = []
    summaries: dict[str, dict[str, float]] = {}
    for metric in METRIC_DIRECTIONS:
        differences = m_metrics[metric] - c_metrics[metric]
        low, median, high = np.quantile(differences, [0.025, 0.5, 0.975])
        summaries[metric] = {
            "ci95_low": float(low),
            "bootstrap_median": float(median),
            "ci95_high": float(high),
            "probability_difference_below_zero": float(np.mean(differences < 0)),
        }
        for index in range(replicates):
            replicate_rows.append(
                {
                    "replicate": index + 1,
                    "metric": metric,
                    "centered": float(c_metrics[metric][index]),
                    "motion_relative": float(m_metrics[metric][index]),
                    "difference_motion_minus_centered": float(differences[index]),
                }
            )
    return replicate_rows, summaries


def load_states(protocol: dict[str, Any]) -> dict[str, Any]:
    columns = [
        "track_id",
        "time",
        "lat_center",
        "lon_center",
        "phase",
        "in_current_parquet_period",
        "support_status",
        "support_cell_count",
    ]
    table = pq.read_table(STATES_PATH, columns=columns)
    track_id = table["track_id"].to_numpy()
    time = table["time"].to_numpy().astype("datetime64[ms]")
    time_hours = time.astype(np.int64) / 3_600_000.0
    lat = table["lat_center"].to_numpy()
    lon = table["lon_center"].to_numpy()
    heading, speed, east, north = compute_motion(track_id, time_hours, lat, lon)
    support_status = np.asarray(table["support_status"].to_pylist(), dtype=object)
    current = table["in_current_parquet_period"].to_numpy()
    has_support = support_status != "no_support"
    finite_heading = np.isfinite(heading) & np.isfinite(speed)
    reliable = finite_heading & (speed >= float(protocol["translation_speed_min_kmh"]))
    base = current & has_support
    eligible = base & reliable
    phases_literal = np.asarray(
        [value if value is not None else "missing" for value in table["phase"].to_pylist()],
        dtype=object,
    )
    phases_grouped = np.asarray([phase_group(value) for value in phases_literal], dtype=object)
    return {
        "table": table,
        "track_id": track_id,
        "time": time,
        "lat": lat,
        "lon": lon,
        "heading": heading,
        "speed": speed,
        "motion_east": east,
        "motion_north": north,
        "support_status": support_status,
        "support_cell_count": table["support_cell_count"].to_numpy(),
        "phase_literal": phases_literal,
        "phase_group": phases_grouped,
        "base_mask": base,
        "eligible_mask": eligible,
        "reliable": reliable,
    }


def make_eligible_table(states: dict[str, Any]) -> tuple[pa.Table, dict[int, int], np.ndarray]:
    indices = np.flatnonzero(states["eligible_mask"])
    unique_tracks = np.unique(states["track_id"][indices])
    track_lookup = {int(value): index for index, value in enumerate(unique_tracks)}
    track_index = np.asarray([track_lookup[int(value)] for value in states["track_id"][indices]], dtype=np.int32)
    table = pa.table(
        {
            "state_idx": pa.array(np.arange(indices.size, dtype=np.int32)),
            "catalog_idx": pa.array(indices.astype(np.int32)),
            "track_idx": pa.array(track_index),
            "track_id": pa.array(states["track_id"][indices], type=pa.int64()),
            "time": pa.array(states["time"][indices], type=pa.timestamp("ms")),
            "lat_center": pa.array(states["lat"][indices]),
            "lon_center": pa.array(states["lon"][indices]),
            "heading_rad": pa.array(states["heading"][indices]),
            "translation_speed_kmh": pa.array(states["speed"][indices]),
            "phase_literal": pa.array(states["phase_literal"][indices].tolist(), type=pa.string()),
            "phase_group": pa.array(states["phase_group"][indices].tolist(), type=pa.string()),
            "support_status": pa.array(states["support_status"][indices].tolist(), type=pa.string()),
            "support_cell_count": pa.array(states["support_cell_count"][indices], type=pa.int32()),
        }
    )
    return table, track_lookup, indices


def query_q95_counts(connection: duckdb.DuckDBPyConnection) -> np.ndarray:
    counts = np.zeros(connection.execute("SELECT count(*) FROM eligible").fetchone()[0], dtype=np.int32)
    source = WIND_PATH.as_posix().replace("'", "''")
    rows = connection.execute(
        f"""
        SELECT e.state_idx, count(*) AS q95_cells
        FROM read_parquet('{source}') AS w
        JOIN eligible AS e USING (track_id, time)
        WHERE w.exceeded_q95
        GROUP BY e.state_idx
        """
    ).fetchall()
    for state_idx, value in rows:
        counts[state_idx] = value
    return counts


def accumulate_exceedances(
    connection: duckdb.DuckDBPyConnection,
    eligible: pa.Table,
    track_count: int,
    q95_counts: np.ndarray,
    domain_km: float,
    bin_km: float,
    bins_per_axis: int,
) -> tuple[
    dict[str, tuple[np.ndarray, np.ndarray]],
    dict[str, tuple[np.ndarray, np.ndarray]],
    np.ndarray,
    np.ndarray,
]:
    number_bins = bins_per_axis * bins_per_axis
    strata = ("all", "full_support", *PHASES)
    matrices = {
        name: (
            np.zeros((track_count, number_bins), dtype=np.float32),
            np.zeros((track_count, number_bins), dtype=np.float32),
        )
        for name in strata
    }
    literal_histograms: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    raw_centered = np.zeros(number_bins, dtype=np.int64)
    raw_motion = np.zeros(number_bins, dtype=np.int64)
    source = WIND_PATH.as_posix().replace("'", "''")
    reader = connection.execute(
        f"""
        SELECT e.state_idx, e.track_idx, e.lat_center, e.lon_center,
               e.heading_rad, e.phase_literal, e.phase_group, e.support_status,
               w.lat, w.lon
        FROM read_parquet('{source}') AS w
        JOIN eligible AS e USING (track_id, time)
        WHERE w.exceeded_q95
        """
    ).to_arrow_reader(batch_size=250_000)

    for batch in reader:
        state_idx = batch.column("state_idx").to_numpy()
        track_idx = batch.column("track_idx").to_numpy()
        lat0 = batch.column("lat_center").to_numpy()
        lon0 = batch.column("lon_center").to_numpy()
        heading = batch.column("heading_rad").to_numpy()
        latitude = batch.column("lat").to_numpy()
        longitude = batch.column("lon").to_numpy()
        phases_literal = np.asarray(batch.column("phase_literal").to_pylist(), dtype=object)
        phases_grouped = np.asarray(batch.column("phase_group").to_pylist(), dtype=object)
        support = np.asarray(batch.column("support_status").to_pylist(), dtype=object)
        x, y = local_xy_km(lat0, lon0, latitude, longitude)
        x_motion, y_motion = rotate_motion(x, y, heading)
        centered_bin, centered_valid = bin_indices(x, y, domain_km, bin_km, bins_per_axis)
        motion_bin, motion_valid = bin_indices(x_motion, y_motion, domain_km, bin_km, bins_per_axis)
        require(np.all(centered_valid) and np.all(motion_valid), "Excedência fora do domínio relativo")
        weights = 1.0 / q95_counts[state_idx]
        np.add.at(raw_centered, centered_bin, 1)
        np.add.at(raw_motion, motion_bin, 1)

        def add(name: str, mask: np.ndarray) -> None:
            centered_matrix, motion_matrix = matrices[name]
            np.add.at(centered_matrix, (track_idx[mask], centered_bin[mask]), weights[mask])
            np.add.at(motion_matrix, (track_idx[mask], motion_bin[mask]), weights[mask])

        all_mask = np.ones(state_idx.size, dtype=bool)
        add("all", all_mask)
        add("full_support", support == "full_support")
        for phase in PHASES:
            add(phase, phases_grouped == phase)
        for literal in np.unique(phases_literal):
            if literal not in literal_histograms:
                literal_histograms[str(literal)] = (
                    np.zeros(number_bins, dtype=np.float64),
                    np.zeros(number_bins, dtype=np.float64),
                )
            mask = phases_literal == literal
            np.add.at(literal_histograms[str(literal)][0], centered_bin[mask], weights[mask])
            np.add.at(literal_histograms[str(literal)][1], motion_bin[mask], weights[mask])
    return matrices, literal_histograms, raw_centered, raw_motion


def reconstruct_support(
    eligible: pa.Table,
    domain_km: float,
    bin_km: float,
    bins_per_axis: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    """Aggregate the exact documented 0.25-degree support without zero filling."""
    number_bins = bins_per_axis * bins_per_axis
    cells_centered = np.zeros(number_bins, dtype=np.int64)
    cells_motion = np.zeros(number_bins, dtype=np.int64)
    states_centered = np.zeros(number_bins, dtype=np.int32)
    states_motion = np.zeros(number_bins, dtype=np.int32)
    grid_lat = np.arange(GRID_LAT_MIN, GRID_LAT_MAX + GRID_STEP_DEG / 2.0, GRID_STEP_DEG)
    grid_lon = np.arange(GRID_LON_MIN, GRID_LON_MAX + GRID_STEP_DEG / 2.0, GRID_STEP_DEG)
    angular_degrees = math.degrees(float(domain_km) / EARTH_RADIUS_KM)
    generated_total = 0
    expected_total = int(np.sum(eligible["support_cell_count"].to_numpy()))
    mismatched_states = 0

    lat0_values = eligible["lat_center"].to_numpy()
    lon0_values = eligible["lon_center"].to_numpy()
    headings = eligible["heading_rad"].to_numpy()
    expected_counts = eligible["support_cell_count"].to_numpy()

    for lat0, lon0, heading, expected in zip(
        lat0_values, lon0_values, headings, expected_counts, strict=True
    ):
        latitude_values = grid_lat[
            (grid_lat >= lat0 - angular_degrees - GRID_STEP_DEG)
            & (grid_lat <= lat0 + angular_degrees + GRID_STEP_DEG)
        ]
        minimum_cosine = max(0.15, math.cos(math.radians(abs(lat0) + angular_degrees)))
        longitude_half_width = min(180.0, angular_degrees / minimum_cosine + GRID_STEP_DEG)
        longitude_values = grid_lon[
            (grid_lon >= lon0 - longitude_half_width)
            & (grid_lon <= lon0 + longitude_half_width)
        ]
        candidate_lon, candidate_lat = np.meshgrid(longitude_values, latitude_values)
        x, y = local_xy_km(lat0, lon0, candidate_lat.ravel(), candidate_lon.ravel())
        within = np.hypot(x, y) <= domain_km + 1e-8
        x = x[within]
        y = y[within]
        generated = int(x.size)
        generated_total += generated
        if generated != int(expected):
            mismatched_states += 1
        centered_bin, centered_valid = bin_indices(x, y, domain_km, bin_km, bins_per_axis)
        x_motion, y_motion = rotate_motion(x, y, np.full(x.size, heading))
        motion_bin, motion_valid = bin_indices(x_motion, y_motion, domain_km, bin_km, bins_per_axis)
        require(np.all(centered_valid) and np.all(motion_valid), "Célula de suporte fora do domínio")
        cells_centered += np.bincount(centered_bin, minlength=number_bins)
        cells_motion += np.bincount(motion_bin, minlength=number_bins)
        states_centered[np.unique(centered_bin)] += 1
        states_motion[np.unique(motion_bin)] += 1

    require(mismatched_states == 0, f"Reconstrução do suporte divergiu em {mismatched_states} estados")
    require(generated_total == expected_total, "Total reconstruído de células de suporte divergiu")
    return cells_centered, cells_motion, states_centered, states_motion, {
        "expected_support_cells": expected_total,
        "reconstructed_support_cells": generated_total,
        "states_with_count_mismatch": mismatched_states,
    }


def translation_outputs(states: dict[str, Any], catalog_q95_counts: np.ndarray) -> dict[str, Any]:
    base = states["base_mask"]
    speed = states["speed"][base]
    quantiles = [0.0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0]
    rows = [
        {"quantile": value, "translation_speed_kmh": float(np.quantile(speed, value))}
        for value in quantiles
    ]
    write_csv(OUTPUT / "translation_speed_distribution.csv", list(rows[0]), rows)

    count_rows: list[dict[str, Any]] = []
    for literal in sorted(np.unique(states["phase_literal"][base])):
        for support_status in ("full_support", "partial_support"):
            for reliable in (True, False):
                mask = (
                    base
                    & (states["phase_literal"] == literal)
                    & (states["support_status"] == support_status)
                    & (states["reliable"] == reliable)
                )
                if not np.any(mask):
                    continue
                count_rows.append(
                    {
                        "phase_literal": literal,
                        "phase_group": phase_group(str(literal)),
                        "support_status": support_status,
                        "heading_reliable": str(reliable).lower(),
                        "cyclones": int(np.unique(states["track_id"][mask]).size),
                        "states": int(np.sum(mask)),
                        "q95_positive_states": int(np.sum(catalog_q95_counts[mask] > 0)),
                        "q95_cells": int(np.sum(catalog_q95_counts[mask])),
                    }
                )
    write_csv(OUTPUT / "state_counts.csv", list(count_rows[0]), count_rows)
    return {
        "base_states": int(np.sum(base)),
        "base_cyclones": int(np.unique(states["track_id"][base]).size),
        "reliable_states": int(np.sum(base & states["reliable"])),
        "unreliable_states": int(np.sum(base & ~states["reliable"])),
        "unreliable_fraction": float(np.mean(~states["reliable"][base])),
        "minimum_speed_kmh": float(np.min(speed)),
        "median_speed_kmh": float(np.median(speed)),
        "p01_speed_kmh": float(np.quantile(speed, 0.01)),
        "p99_speed_kmh": float(np.quantile(speed, 0.99)),
    }


def query_catalog_q95_counts(
    connection: duckdb.DuckDBPyConnection,
    states: dict[str, Any],
) -> np.ndarray:
    """Count q95 cells for every current-period state with support."""
    base_indices = np.flatnonzero(states["base_mask"])
    base = pa.table(
        {
            "catalog_idx": pa.array(base_indices.astype(np.int32)),
            "track_id": pa.array(states["track_id"][base_indices], type=pa.int64()),
            "time": pa.array(states["time"][base_indices], type=pa.timestamp("ms")),
        }
    )
    connection.register("base_states", base)
    source = WIND_PATH.as_posix().replace("'", "''")
    result = np.zeros(states["track_id"].size, dtype=np.int32)
    rows = connection.execute(
        f"""
        SELECT b.catalog_idx, count(*) AS q95_cells
        FROM read_parquet('{source}') AS w
        JOIN base_states AS b USING (track_id, time)
        WHERE w.exceeded_q95
        GROUP BY b.catalog_idx
        """
    ).fetchall()
    for catalog_idx, count in rows:
        result[catalog_idx] = count
    return result


def plot_translation(states: dict[str, Any], threshold: float) -> None:
    speed = states["speed"][states["base_mask"]]
    figure, axes = plt.subplots(1, 2, figsize=(11.2, 4.1), constrained_layout=True)
    axes[0].hist(speed, bins=np.arange(0, 155, 2.5), color="#4678a8", edgecolor="white", linewidth=0.2)
    axes[0].axvline(threshold, color="#b23a2b", linewidth=1.8, label=f"corte = {threshold:g} km/h")
    axes[0].set(xlabel="Velocidade de translação (km/h)", ylabel="Estados", title="Distribuição observada")
    axes[0].legend(frameon=False)
    ordered = np.sort(speed)
    axes[1].plot(ordered, np.arange(1, ordered.size + 1) / ordered.size, color="#4678a8")
    axes[1].axvline(threshold, color="#b23a2b", linewidth=1.8)
    axes[1].set(xlim=(0, 25), ylim=(0, 0.15), xlabel="Velocidade de translação (km/h)", ylabel="Fração acumulada", title="Cauda inferior ampliada")
    for axis in axes:
        axis.grid(alpha=0.18)
    figure.suptitle("E-001 · Diagnóstico prévio da confiabilidade do heading", fontsize=13, fontweight="bold")
    figure.savefig(OUTPUT / "translation_speed_diagnostic.png", dpi=180)
    plt.close(figure)


def plot_maps(
    centered: np.ndarray,
    motion: np.ndarray,
    bins_per_axis: int,
    domain_km: float,
    output_name: str,
    title: str,
) -> None:
    centered_probability = centered / centered.sum()
    motion_probability = motion / motion.sum()
    difference = motion_probability - centered_probability
    maximum = max(float(centered_probability.max()), float(motion_probability.max()))
    difference_limit = float(np.max(np.abs(difference)))
    figure, axes = plt.subplots(1, 3, figsize=(14.4, 4.35), constrained_layout=True)
    extent = (-domain_km, domain_km, -domain_km, domain_km)
    first = axes[0].imshow(centered_probability.reshape(bins_per_axis, bins_per_axis), origin="lower", extent=extent, cmap="magma", vmin=0, vmax=maximum)
    axes[1].imshow(motion_probability.reshape(bins_per_axis, bins_per_axis), origin="lower", extent=extent, cmap="magma", vmin=0, vmax=maximum)
    third = axes[2].imshow(
        difference.reshape(bins_per_axis, bins_per_axis),
        origin="lower",
        extent=extent,
        cmap="RdBu_r",
        norm=TwoSlopeNorm(vmin=-difference_limit, vcenter=0.0, vmax=difference_limit),
    )
    axes[0].set_title("Centered · norte para cima")
    axes[1].set_title("Motion-relative · frente para cima")
    axes[2].set_title("Diferença · motion − centered")
    for index, axis in enumerate(axes):
        axis.axhline(0, color="white" if index < 2 else "#555555", linewidth=0.45, alpha=0.75)
        axis.axvline(0, color="white" if index < 2 else "#555555", linewidth=0.45, alpha=0.75)
        axis.set_aspect("equal")
        axis.set_xlabel("x (km): leste / direita")
        axis.set_ylabel("y (km): norte / frente")
    figure.colorbar(first, ax=axes[:2], shrink=0.78, label="Massa q95 normalizada por bin")
    figure.colorbar(third, ax=axes[2], shrink=0.78, label="Diferença de massa")
    figure.suptitle(title, fontsize=13, fontweight="bold")
    figure.savefig(OUTPUT / output_name, dpi=180)
    plt.close(figure)


def plot_phase_maps(
    matrices: dict[str, tuple[np.ndarray, np.ndarray]],
    bins_per_axis: int,
    domain_km: float,
) -> None:
    extent = (-domain_km, domain_km, -domain_km, domain_km)
    figure, axes = plt.subplots(4, 2, figsize=(8.4, 14.5), constrained_layout=True)
    for row, phase in enumerate(PHASES):
        centered = matrices[phase][0].sum(axis=0)
        motion = matrices[phase][1].sum(axis=0)
        centered = centered / centered.sum()
        motion = motion / motion.sum()
        maximum = max(float(centered.max()), float(motion.max()))
        image = None
        for column, (name, values) in enumerate((("Centered", centered), ("Motion-relative", motion))):
            image = axes[row, column].imshow(values.reshape(bins_per_axis, bins_per_axis), origin="lower", extent=extent, cmap="magma", vmin=0, vmax=maximum)
            axes[row, column].axhline(0, color="white", linewidth=0.4, alpha=0.7)
            axes[row, column].axvline(0, color="white", linewidth=0.4, alpha=0.7)
            axes[row, column].set_aspect("equal")
            axes[row, column].set_title(f"{PHASE_LABELS[phase]} · {name}")
            axes[row, column].set_xlabel("x (km): leste / direita")
            axes[row, column].set_ylabel("y (km): norte / frente")
        figure.colorbar(image, ax=axes[row, :], shrink=0.68, label="Massa q95 normalizada")
    figure.suptitle("E-001 · Distribuição não suavizada por fase", fontsize=14, fontweight="bold")
    figure.savefig(OUTPUT / "orientation_by_phase.png", dpi=180)
    plt.close(figure)


def sanity_checks_and_plot(
    connection: duckdb.DuckDBPyConnection,
    eligible: pa.Table,
    q95_counts: np.ndarray,
) -> dict[str, Any]:
    positive = np.flatnonzero(q95_counts > 0)
    speeds = eligible["translation_speed_kmh"].to_numpy()[positive]
    targets = np.quantile(speeds, [0.25, 0.50, 0.75])
    chosen = [int(positive[np.argmin(np.abs(speeds - target))]) for target in targets]
    sample_table = pa.table({"state_idx": pa.array(chosen, type=pa.int32())})
    connection.register("sanity_states", sample_table)
    source = WIND_PATH.as_posix().replace("'", "''")
    rows = connection.execute(
        f"""
        SELECT e.state_idx, e.track_id, e.time, e.lat_center, e.lon_center,
               e.heading_rad, e.translation_speed_kmh, w.lat, w.lon
        FROM read_parquet('{source}') AS w
        JOIN eligible AS e USING (track_id, time)
        JOIN sanity_states AS s USING (state_idx)
        WHERE w.exceeded_q95
        ORDER BY e.state_idx, w.lat, w.lon
        """
    ).fetchall()
    grouped: dict[int, list[tuple[Any, ...]]] = {value: [] for value in chosen}
    for row in rows:
        grouped[int(row[0])].append(row)

    figure, axes = plt.subplots(3, 2, figsize=(8.4, 12.0), constrained_layout=True)
    check_rows = []
    maximum_distance_error = 0.0
    maximum_inverse_error = 0.0
    for row_index, state_idx in enumerate(chosen):
        values = grouped[state_idx]
        metadata = values[0]
        lat0, lon0, heading = float(metadata[3]), float(metadata[4]), float(metadata[5])
        latitude = np.asarray([value[7] for value in values], dtype=float)
        longitude = np.asarray([value[8] for value in values], dtype=float)
        x, y = local_xy_km(lat0, lon0, latitude, longitude)
        xm, ym = rotate_motion(x, y, np.full(x.size, heading))
        recovered_x, recovered_y = inverse_rotate_motion(xm, ym, np.full(x.size, heading))
        distance_error = float(np.max(np.abs(np.hypot(x, y) - np.hypot(xm, ym))))
        inverse_error = float(np.max(np.hypot(x - recovered_x, y - recovered_y)))
        maximum_distance_error = max(maximum_distance_error, distance_error)
        maximum_inverse_error = max(maximum_inverse_error, inverse_error)
        step = max(1, x.size // 2500)
        axes[row_index, 0].scatter(x[::step], y[::step], s=2, alpha=0.35, color="#8c2d62")
        axes[row_index, 1].scatter(xm[::step], ym[::step], s=2, alpha=0.35, color="#286c8e")
        arrow_length = 360.0
        axes[row_index, 0].arrow(0, 0, arrow_length * math.sin(heading), arrow_length * math.cos(heading), width=10, color="#111111", length_includes_head=True)
        axes[row_index, 1].arrow(0, 0, 0, arrow_length, width=10, color="#111111", length_includes_head=True)
        for column in range(2):
            axes[row_index, column].scatter([0], [0], marker="+", s=80, color="#f2b134", linewidths=1.8)
            axes[row_index, column].set(xlim=(-1100, 1100), ylim=(-1100, 1100), aspect="equal", xlabel="x (km)", ylabel="y (km)")
            axes[row_index, column].grid(alpha=0.15)
        axes[row_index, 0].set_title(f"Centered · track {metadata[1]}")
        axes[row_index, 1].set_title(f"Motion-relative · {float(metadata[6]):.1f} km/h")
        check_rows.append(
            {
                "track_id": int(metadata[1]),
                "time": metadata[2].isoformat(),
                "translation_speed_kmh": float(metadata[6]),
                "q95_cells": len(values),
                "distance_preservation_max_error_km": distance_error,
                "inverse_max_error_km": inverse_error,
            }
        )
    figure.suptitle("E-001 · Sanidade da rotação em três estados", fontsize=14, fontweight="bold")
    figure.savefig(OUTPUT / "rotation_sanity_checks.png", dpi=180)
    plt.close(figure)

    # Analytic sign checks: northward motion maps north to front, and its east is right.
    test_x = np.array([0.0, 100.0])
    test_y = np.array([100.0, 0.0])
    xm, ym = rotate_motion(test_x, test_y, np.zeros(2))
    require(np.allclose([xm[0], ym[0]], [0.0, 100.0]), "Frente com heading norte falhou")
    require(np.allclose([xm[1], ym[1]], [100.0, 0.0]), "Direita com heading norte falhou")
    return {
        "states": check_rows,
        "center_maps_to_origin": True,
        "front_and_right_sign_checks": True,
        "maximum_distance_preservation_error_km": maximum_distance_error,
        "maximum_inverse_error_km": maximum_inverse_error,
    }


def decision_from_results(comparisons: dict[str, dict[str, Any]], heading_summary: dict[str, Any], support_metrics: dict[str, dict[str, float]]) -> dict[str, Any]:
    global_result = comparisons["all"]
    entropy = global_result["bootstrap"]["entropy_nats"]
    area75 = global_result["bootstrap"]["area75_km2"]
    same_direction = all(
        global_result["point_difference"][metric] < 0
        for metric in ("area50_km2", "area90_km2")
    )
    phase_favorable = sum(
        comparisons[phase]["point_difference"]["entropy_nats"] < 0
        and comparisons[phase]["point_difference"]["area75_km2"] < 0
        for phase in PHASES
    )
    heading_ok = heading_summary["unreliable_fraction"] < 0.10
    support_entropy_change = support_metrics["motion_relative"]["entropy_nats"] - support_metrics["centered"]["entropy_nats"]
    observed_entropy_change = global_result["point_difference"]["entropy_nats"]
    support_not_explanatory = not (
        support_entropy_change < 0
        and abs(support_entropy_change) >= 0.5 * abs(observed_entropy_change)
    )
    favorable = (
        entropy["ci95_high"] < 0
        and area75["ci95_high"] < 0
        and same_direction
        and phase_favorable >= 3
        and heading_ok
        and support_not_explanatory
    )
    contrary = entropy["ci95_low"] > 0 and area75["ci95_low"] > 0
    if favorable:
        status = "ADOPTED"
        conclusion = "motion-relative supported"
    elif contrary:
        status = "REJECTED"
        conclusion = "centered supported"
    else:
        status = "INCONCLUSIVE"
        conclusion = "evidence ambiguous"
    return {
        "experiment_status": status,
        "conclusion": conclusion,
        "checks": {
            "entropy_ci_below_zero": entropy["ci95_high"] < 0,
            "area75_ci_below_zero": area75["ci95_high"] < 0,
            "area50_and_area90_point_same_direction": same_direction,
            "favorable_phase_groups_of_four": int(phase_favorable),
            "heading_loss_below_10_percent": heading_ok,
            "support_change_not_comparable_explanation": support_not_explanatory,
        },
        "support_entropy_difference": support_entropy_change,
        "exceedance_entropy_difference": observed_entropy_change,
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    for path, expected in ((STATES_PATH, EXPECTED_HASHES[STATES_PATH.name]), (TRACKS_PATH, EXPECTED_HASHES[TRACKS_PATH.name]), (WIND_PATH, EXPECTED_HASHES[WIND_PATH.name])):
        require(path.is_file(), f"Entrada ausente: {path}")
        require(file_sha256(path) == expected, f"SHA-256 inesperado: {path.name}")

    domain_km = float(protocol["relative_domain_km"][1])
    bin_km = float(protocol["bin_size_km"])
    bins_per_axis = int(round(2.0 * domain_km / bin_km))
    require(math.isclose(bins_per_axis * bin_km, 2.0 * domain_km), "Grade relativa não fecha o domínio")
    edges = np.linspace(-domain_km, domain_km, bins_per_axis + 1)
    centers = (edges[:-1] + edges[1:]) / 2.0
    center_x, center_y = np.meshgrid(centers, centers)
    x_centers = center_x.ravel()
    y_centers = center_y.ravel()
    bin_area = bin_km * bin_km

    states = load_states(protocol)
    eligible, track_lookup, eligible_indices = make_eligible_table(states)
    connection = duckdb.connect()
    connection.register("eligible", eligible)
    q95_counts = query_q95_counts(connection)
    catalog_q95_counts = query_catalog_q95_counts(connection, states)
    positive_states = q95_counts > 0
    require(np.sum(positive_states) > 0, "Nenhum estado q95 positivo")

    heading_summary = translation_outputs(states, catalog_q95_counts)
    plot_translation(states, float(protocol["translation_speed_min_kmh"]))
    matrices, literal_histograms, raw_centered, raw_motion = accumulate_exceedances(
        connection,
        eligible,
        len(track_lookup),
        q95_counts,
        domain_km,
        bin_km,
        bins_per_axis,
    )
    require(int(raw_centered.sum()) == int(q95_counts.sum()), "Contagem q95 centered divergiu")
    require(int(raw_motion.sum()) == int(q95_counts.sum()), "Contagem q95 motion divergiu")

    cells_c, cells_m, states_c, states_m, support_validation = reconstruct_support(
        eligible, domain_km, bin_km, bins_per_axis
    )
    support_metric_values = {
        "centered": metric_values(cells_c, x_centers, y_centers, bin_area),
        "motion_relative": metric_values(cells_m, x_centers, y_centers, bin_area),
    }

    # Per-bin audit: every row describes evaluated support, not imputed zeros.
    mass_c = matrices["all"][0].sum(axis=0)
    mass_m = matrices["all"][1].sum(axis=0)
    spatial_rows = []
    for representation, support_cells, support_states, q95_cells, mass in (
        ("centered", cells_c, states_c, raw_centered, mass_c),
        ("motion_relative", cells_m, states_m, raw_motion, mass_m),
    ):
        for flat in range(bins_per_axis * bins_per_axis):
            spatial_rows.append(
                {
                    "representation": representation,
                    "bin_x_center_km": float(x_centers[flat]),
                    "bin_y_center_km": float(y_centers[flat]),
                    "eligible_states_total": eligible.num_rows,
                    "states_with_spatial_support": int(support_states[flat]),
                    "evaluated_state_cells": int(support_cells[flat]),
                    "q95_exceedance_cells": int(q95_cells[flat]),
                    "q95_state_normalized_mass": float(mass[flat]),
                    "q95_probability_mass": float(mass[flat] / mass.sum()),
                }
            )
    write_csv(OUTPUT / "spatial_bins.csv", list(spatial_rows[0]), spatial_rows)

    # Point metrics and paired cyclone bootstrap for global, support diagnostic and phases.
    rng = np.random.default_rng(int(protocol["bootstrap_seed"]))
    comparisons: dict[str, dict[str, Any]] = {}
    metric_rows = []
    bootstrap_rows = []
    comparison_rows = []
    eligible_phase = np.asarray(eligible["phase_group"].to_pylist(), dtype=object)
    eligible_support = np.asarray(eligible["support_status"].to_pylist(), dtype=object)
    eligible_track_index = eligible["track_idx"].to_numpy()
    for stratum in ("all", "full_support", *PHASES):
        if stratum == "all":
            state_mask = np.ones(eligible.num_rows, dtype=bool)
        elif stratum == "full_support":
            state_mask = eligible_support == "full_support"
        else:
            state_mask = eligible_phase == stratum
        track_mask = np.zeros(len(track_lookup), dtype=bool)
        track_mask[np.unique(eligible_track_index[state_mask])] = True
        centered_matrix = matrices[stratum][0][track_mask]
        motion_matrix = matrices[stratum][1][track_mask]
        centered_mass = centered_matrix.sum(axis=0)
        motion_mass = motion_matrix.sum(axis=0)
        centered_metrics = metric_values(centered_mass, x_centers, y_centers, bin_area)
        motion_metrics = metric_values(motion_mass, x_centers, y_centers, bin_area)
        point_difference = {
            metric: float(motion_metrics[metric] - centered_metrics[metric])
            for metric in METRIC_DIRECTIONS
        }
        replicate_values, bootstrap_summary = bootstrap_metrics(
            centered_matrix,
            motion_matrix,
            x_centers,
            y_centers,
            bin_area,
            int(protocol["bootstrap_replicates"]),
            rng,
        )
        for representation, values in (("centered", centered_metrics), ("motion_relative", motion_metrics)):
            metric_rows.append(
                {
                    "stratum": stratum,
                    "representation": representation,
                    "cyclones": int(np.sum(track_mask)),
                    "eligible_states": int(np.sum(state_mask)),
                    "q95_positive_states": int(np.sum(positive_states[state_mask])),
                    **values,
                }
            )
        for row in replicate_values:
            bootstrap_rows.append({"stratum": stratum, **row})
        for metric in METRIC_DIRECTIONS:
            summary = bootstrap_summary[metric]
            comparison_rows.append(
                {
                    "stratum": stratum,
                    "metric": metric,
                    "direction_for_concentration": METRIC_DIRECTIONS[metric],
                    "centered": centered_metrics[metric],
                    "motion_relative": motion_metrics[metric],
                    "difference_motion_minus_centered": point_difference[metric],
                    **summary,
                }
            )
        comparisons[stratum] = {
            "cyclones": int(np.sum(track_mask)),
            "eligible_states": int(np.sum(state_mask)),
            "q95_positive_states": int(np.sum(positive_states[state_mask])),
            "centered": centered_metrics,
            "motion_relative": motion_metrics,
            "point_difference": point_difference,
            "bootstrap": bootstrap_summary,
        }

    write_csv(OUTPUT / "metrics_by_stratum.csv", list(metric_rows[0]), metric_rows)
    write_csv(OUTPUT / "metric_comparisons.csv", list(comparison_rows[0]), comparison_rows)
    write_csv(OUTPUT / "bootstrap_replicates.csv", list(bootstrap_rows[0]), bootstrap_rows)

    literal_rows = []
    for literal, (centered_mass, motion_mass) in sorted(literal_histograms.items()):
        for representation, mass in (("centered", centered_mass), ("motion_relative", motion_mass)):
            literal_rows.append(
                {"phase_literal": literal, "representation": representation, **metric_values(mass, x_centers, y_centers, bin_area)}
            )
    write_csv(OUTPUT / "metrics_by_literal_phase.csv", list(literal_rows[0]), literal_rows)

    support_rows = []
    for representation, values in support_metric_values.items():
        support_rows.append({"representation": representation, **values})
    write_csv(OUTPUT / "support_diagnostics.csv", list(support_rows[0]), support_rows)

    plot_maps(
        mass_c,
        mass_m,
        bins_per_axis,
        domain_km,
        "orientation_comparison.png",
        "E-001 · Distribuição normalizada das excedências q95",
    )
    plot_phase_maps(matrices, bins_per_axis, domain_km)
    sanity = sanity_checks_and_plot(connection, eligible, q95_counts)
    atomic_json(OUTPUT / "sanity_checks.json", sanity)

    decision = decision_from_results(comparisons, heading_summary, support_metric_values)
    input_hashes = {path.name: file_sha256(path) for path in (TRACKS_PATH, STATES_PATH, WIND_PATH)}
    summary = {
        "experiment": {"id": "E-001", "status": decision["experiment_status"]},
        "completed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "protocol": protocol,
        "population": {
            **heading_summary,
            "eligible_cyclones": int(len(track_lookup)),
            "eligible_states": int(eligible.num_rows),
            "q95_positive_cyclones": int(np.unique(eligible["track_id"].to_numpy()[positive_states]).size),
            "q95_positive_states": int(np.sum(positive_states)),
            "q95_exceedance_cells": int(np.sum(q95_counts)),
        },
        "grid": {
            "bins_per_axis": bins_per_axis,
            "total_bins": bins_per_axis * bins_per_axis,
            "bin_area_km2": bin_area,
        },
        "comparisons": comparisons,
        "support_metrics": support_metric_values,
        "support_validation": support_validation,
        "sanity_checks": sanity,
        "decision": decision,
        "reproducibility": {
            "input_sha256": input_hashes,
            "protocol_sha256": file_sha256(PROTOCOL_PATH),
            "script_sha256": file_sha256(Path(__file__)),
            "bootstrap_seed": protocol["bootstrap_seed"],
        },
    }
    atomic_json(OUTPUT / "summary.json", summary)
    print(json.dumps({
        "status": decision["experiment_status"],
        "eligible_cyclones": len(track_lookup),
        "eligible_states": eligible.num_rows,
        "q95_positive_states": int(np.sum(positive_states)),
        "global_difference": comparisons["all"]["point_difference"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
