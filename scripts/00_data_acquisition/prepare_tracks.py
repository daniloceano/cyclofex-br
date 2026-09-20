#!/usr/bin/env python3
"""Prepare and validate the canonical hourly and ERA5 6-hour track catalogs.

This is a data-provenance transformation, not a wind or footprint analysis.
It requires the validated Zenodo CSV and the current exceedance Parquet, then
writes two compact Parquets plus reproducible provenance/validation reports.

Run from any directory::

    .venv/bin/python scripts/00_data_acquisition/prepare_tracks.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
PIPELINE_VERSION = "1.0.0"

RECORD_ID = 18133432
RECORD_VERSION = 1
DOI = "10.5281/zenodo.18133432"
RECORD_URL = f"https://zenodo.org/records/{RECORD_ID}"
FILENAME = "tracks_SAt_filtered_with_energetics.csv"
EXPECTED_SIZE = 180_778_076
EXPECTED_MD5 = "a413e7f89d20b5b18a9da8b671b53d72"
EXPECTED_SHA256 = "bf1059ab2f1896c6df942a290d7676bce701f6d3cbf7ac9193f5c6b51d63cc26"
EXPECTED_HEADER = [
    "track_id", "date", "lon vor", "lat vor", "vor42", "region", "period",
    "Az", "Ae", "Kz", "Ke", "Cz", "Ca", "Ck", "Ce", "BAz", "BAe",
    "BKz", "BKe", "BΦZ", "BΦE", "Gz", "Ge",
    "∂Az/∂t (finite diff.)", "∂Ae/∂t (finite diff.)",
    "∂Kz/∂t (finite diff.)", "∂Ke/∂t (finite diff.)",
    "RGz", "RKz", "RGe", "RKe",
]
SOURCE_COLUMNS = ["track_id", "date", "lon vor", "lat vor", "vor42", "region", "period"]
EXPECTED_PHASES = {
    "incipient", "incipient 2", "intensification", "intensification 2",
    "mature", "mature 2", "decay", "decay 2", "residual",
}
EXPECTED_REGIONS = {"ARG", "LA-PLATA", "SE-BR"}

GRID_LAT_MIN = -65.0
GRID_LAT_MAX = -10.0
GRID_LON_MIN = -85.0
GRID_LON_MAX = -15.0
GRID_STEP_DEG = 0.25
EARTH_RADIUS_KM = 6_371.0
SUPPORT_RADIUS_KM = 1_100.0
CURRENT_PERIOD_START = np.datetime64("2010-01-01T00", "h").astype(np.int64)
CURRENT_PERIOD_END = np.datetime64("2020-12-31T18", "h").astype(np.int64)

EXPECTED = {
    "source_rows": 631_009,
    "source_tracks": 6_789,
    "source_null_phase_rows": 50_069,
    "derived_states": 109_857,
    "current_parquet_tracks": 1_781,
    "current_parquet_states": 20_101,
    "current_period_expected_states": 29_311,
    "current_period_tracks": 1_785,
    "missing_states": 9_210,
    "missing_with_support": 3_233,
    "missing_no_support": 5_977,
    "unexpected_parquet_states": 0,
    "matching_centers": 20_101,
    "matching_phases": 20_101,
    "current_period_support_cells": 137_621_821,
}

SPECIAL_CASES = {
    20091196: {"states": 31, "expected": "absent_no_support"},
    20110523: {"states": 6, "expected": "absent_with_support"},
    20191177: {"states": 21, "expected": "absent_with_support"},
    20203207: {"states": 6, "expected": "absent_with_support"},
}

DEFAULT_SOURCE = ROOT / "data" / "raw" / "zenodo" / str(RECORD_ID) / FILENAME
DEFAULT_TRACKS = ROOT / "data" / "tracks_SAt_1979_2020.parquet"
DEFAULT_STATES = ROOT / "data" / "cyclone_states_era5_6h_1979_2020.parquet"
DEFAULT_CURRENT = ROOT / "data" / "cyclone_exceedances_by_track_2010_2020_p90.parquet"
DEFAULT_OUTPUT = ROOT / "outputs" / "00_data_acquisition"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def hash_file(path: Path, algorithms: tuple[str, ...] = ("sha256",)) -> dict[str, str]:
    hashes = {
        name: hashlib.md5() if name == "md5" else hashlib.new(name)  # nosec B324
        for name in algorithms
    }
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            for value in hashes.values():
                value.update(chunk)
    return {name: value.hexdigest() for name, value in hashes.items()}


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def validate_source_file(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"Fonte Zenodo ausente: {path}")
    size = path.stat().st_size
    hashes = hash_file(path, ("md5", "sha256"))
    with path.open("r", encoding="utf-8", newline="") as source:
        header = next(csv.reader(source))
    require(size == EXPECTED_SIZE, f"Tamanho da fonte: {size}; esperado: {EXPECTED_SIZE}")
    require(hashes["md5"] == EXPECTED_MD5, "MD5 da fonte não corresponde ao Zenodo")
    require(hashes["sha256"] == EXPECTED_SHA256, "SHA-256 da fonte não corresponde à auditoria")
    require(header == EXPECTED_HEADER, "Schema/header da fonte Zenodo mudou")
    return {"size_bytes": size, "hashes": hashes, "header": header}


def read_source(path: Path) -> pa.Table:
    convert = pacsv.ConvertOptions(
        column_types={
            "track_id": pa.int64(),
            "date": pa.timestamp("ms"),
            "lon vor": pa.float64(),
            "lat vor": pa.float64(),
            "vor42": pa.float64(),
            "region": pa.string(),
            "period": pa.string(),
        },
        include_columns=SOURCE_COLUMNS,
        strings_can_be_null=True,
        null_values=["", "nan"],
    )
    table = pacsv.read_csv(path, convert_options=convert)
    order = pc.sort_indices(table, sort_keys=[("track_id", "ascending"), ("date", "ascending")])
    return table.take(order)


def validate_hourly_source(table: pa.Table) -> dict[str, Any]:
    require(table.num_rows == EXPECTED["source_rows"], "Contagem de linhas Zenodo divergiu")
    require(table.column_names == SOURCE_COLUMNS, "Colunas mínimas Zenodo divergiram")
    for column in ("track_id", "date", "lon vor", "lat vor", "vor42", "region"):
        require(table[column].null_count == 0, f"Nulos inesperados em {column}")

    track_id = table["track_id"].to_numpy()
    date_ms = table["date"].to_numpy().astype("datetime64[ms]").astype(np.int64)
    unique_tracks = int(np.unique(track_id).size)
    require(unique_tracks == EXPECTED["source_tracks"], "Contagem de tracks Zenodo divergiu")
    duplicate = (track_id[1:] == track_id[:-1]) & (date_ms[1:] == date_ms[:-1])
    require(not np.any(duplicate), "Duplicata encontrada em track_id + date")

    same_track = track_id[1:] == track_id[:-1]
    gaps_hours = (date_ms[1:] - date_ms[:-1]) // 3_600_000
    require(np.all(gaps_hours[same_track] == 1), "Track horária com lacuna ou ordem inválida")

    phases = set(table["period"].drop_null().unique().to_pylist())
    regions = set(table["region"].unique().to_pylist())
    require(phases == EXPECTED_PHASES, f"Categorias phase inesperadas: {sorted(phases)}")
    require(regions == EXPECTED_REGIONS, f"Regiões inesperadas: {sorted(regions)}")
    require(
        table["period"].null_count == EXPECTED["source_null_phase_rows"],
        "Contagem de phase nula divergiu",
    )
    return {
        "rows": table.num_rows,
        "tracks": unique_tracks,
        "duplicate_track_date": 0,
        "within_track_non_hourly_gaps": 0,
        "date_min": pc.min(table["date"]).as_py().isoformat(),
        "date_max": pc.max(table["date"]).as_py().isoformat(),
        "regions": sorted(regions),
        "phase_categories": sorted(phases),
        "null_phase_rows": table["period"].null_count,
    }


def canonical_tracks(table: pa.Table) -> pa.Table:
    result = table.rename_columns(
        ["track_id", "date", "lon_center", "lat_center", "vor42", "region", "phase"]
    )
    metadata = {
        b"product": b"canonical hourly cyclone track and lifecycle catalog",
        b"source_doi": DOI.encode(),
        b"source_record": str(RECORD_ID).encode(),
        b"source_sha256": EXPECTED_SHA256.encode(),
        b"pipeline_version": PIPELINE_VERSION.encode(),
        b"time_standard": b"UTC; timezone-naive timestamp[ms]",
        b"column_mapping": b"lon_center<-lon vor; lat_center<-lat vor; phase<-period",
    }
    return result.replace_schema_metadata(metadata)


def nearest_six_hour_states(tracks: pa.Table) -> tuple[pa.Table, np.ndarray, np.ndarray]:
    track_id = tracks["track_id"].to_numpy()
    original_ms = tracks["date"].to_numpy().astype("datetime64[ms]").astype(np.int64)
    original_hour = original_ms // 3_600_000
    remainder = original_hour % 6
    era_hour = original_hour - remainder + np.where(remainder <= 3, 0, 6)
    offset = original_hour - era_hour
    require(np.max(np.abs(offset)) <= 3, "Associação temporal excedeu três horas")

    # Primary keys are the last lexsort keys.  At equal |offset|, the earlier
    # original track hour wins, reproducing the validated backward tie rule.
    order = np.lexsort((original_hour, np.abs(offset), era_hour, track_id))
    ordered_track = track_id[order]
    ordered_era = era_hour[order]
    keep = np.ones(order.size, dtype=bool)
    keep[1:] = (ordered_track[1:] != ordered_track[:-1]) | (ordered_era[1:] != ordered_era[:-1])
    selected = order[keep]

    selected_tracks = tracks.take(pa.array(selected, type=pa.int64()))
    era_ms = (era_hour[selected] * 3_600_000).astype("datetime64[ms]")
    selected_track = ordered_track[keep]
    selected_era = ordered_era[keep]
    duplicate_state = (
        (selected_track[1:] == selected_track[:-1])
        & (selected_era[1:] == selected_era[:-1])
    )
    require(not np.any(duplicate_state), "Duplicata encontrada em track_id + time")
    state_table = pa.table(
        {
            "track_id": selected_tracks["track_id"],
            "track_time_original": selected_tracks["date"],
            "time": pa.array(era_ms, type=pa.timestamp("ms")),
            "lat_center": selected_tracks["lat_center"],
            "lon_center": selected_tracks["lon_center"],
            "phase": selected_tracks["phase"],
            "vor42": selected_tracks["vor42"],
            "region": selected_tracks["region"],
            "track_minus_era5_hours": pa.array(offset[selected].astype(np.int8)),
        }
    )
    require(state_table.num_rows == EXPECTED["derived_states"], "Total de estados de 6 h divergiu")
    return state_table, era_hour[selected], selected


def support_cell_counts(lat_center: np.ndarray, lon_center: np.ndarray) -> np.ndarray:
    """Count regular-grid cells within the spherical 1,100 km disk.

    The haversine inequality is solved for the allowed longitude interval at
    each of the 221 latitude rows.  This is exactly equivalent to evaluating
    all 62,101 grid cells, without materializing the state-cell cross product.
    """

    grid_lat = np.arange(GRID_LAT_MIN, GRID_LAT_MAX + 1e-9, GRID_STEP_DEG)
    grid_lat_rad = np.radians(grid_lat)[None, :]
    angular_radius = SUPPORT_RADIUS_KM / EARTH_RADIUS_KM
    sin_half_radius_sq = math.sin(angular_radius / 2.0) ** 2
    lon_cells = int(round((GRID_LON_MAX - GRID_LON_MIN) / GRID_STEP_DEG)) + 1
    counts = np.zeros(lat_center.size, dtype=np.int32)

    for start in range(0, lat_center.size, 4_096):
        stop = min(start + 4_096, lat_center.size)
        center_lat_rad = np.radians(lat_center[start:stop])[:, None]
        remaining = sin_half_radius_sq - np.sin((grid_lat_rad - center_lat_rad) / 2.0) ** 2
        denominator = np.cos(center_lat_rad) * np.cos(grid_lat_rad)
        ratio = np.clip(remaining / denominator, 0.0, 1.0)
        longitude_half_width = np.degrees(2.0 * np.arcsin(np.sqrt(ratio)))
        valid_latitude = remaining >= -1e-15

        lower = np.maximum(
            GRID_LON_MIN,
            lon_center[start:stop, None] - longitude_half_width,
        )
        upper = np.minimum(
            GRID_LON_MAX,
            lon_center[start:stop, None] + longitude_half_width,
        )
        first = np.ceil((lower - GRID_LON_MIN) / GRID_STEP_DEG - 1e-10).astype(np.int32)
        last = np.floor((upper - GRID_LON_MIN) / GRID_STEP_DEG + 1e-10).astype(np.int32)
        per_latitude = np.maximum(
            0,
            np.minimum(last, lon_cells - 1) - np.maximum(first, 0) + 1,
        )
        per_latitude[~valid_latitude] = 0
        counts[start:stop] = per_latitude.sum(axis=1)
    return counts


def support_status(
    lat_center: np.ndarray,
    lon_center: np.ndarray,
    counts: np.ndarray,
) -> np.ndarray:
    """Classify complete, domain-truncated, and empty spatial support."""

    angular_radius = SUPPORT_RADIUS_KM / EARTH_RADIUS_KM
    lat_half_width = math.degrees(angular_radius)
    latitude_contained = (
        (lat_center - lat_half_width >= GRID_LAT_MIN)
        & (lat_center + lat_half_width <= GRID_LAT_MAX)
    )
    ratio = np.sin(angular_radius) / np.cos(np.radians(lat_center))
    longitude_half_width = np.full(lat_center.size, 180.0)
    regular = np.abs(ratio) <= 1.0
    longitude_half_width[regular] = np.degrees(np.arcsin(np.clip(ratio[regular], -1.0, 1.0)))
    longitude_contained = (
        (lon_center - longitude_half_width >= GRID_LON_MIN)
        & (lon_center + longitude_half_width <= GRID_LON_MAX)
    )
    return np.where(
        counts == 0,
        "no_support",
        np.where(latitude_contained & longitude_contained, "full_support", "partial_support"),
    )


def read_current_parquet_states(path: Path) -> tuple[pa.Table, int]:
    require(path.is_file(), f"Parquet atual ausente: {path}")
    escaped = str(path).replace("'", "''")
    connection = duckdb.connect()
    try:
        tracks = connection.execute(
            f"SELECT count(DISTINCT track_id) FROM read_parquet('{escaped}')"
        ).fetchone()[0]
        states = connection.execute(
            f"""
            SELECT DISTINCT track_id, time, lat_center, lon_center, phase
            FROM read_parquet('{escaped}')
            ORDER BY track_id, time
            """
        ).to_arrow_table()
    finally:
        connection.close()
    return states, int(tracks)


def enrich_and_validate_states(
    state_table: pa.Table,
    era_hour: np.ndarray,
    current_states: pa.Table,
    current_track_count: int,
) -> tuple[pa.Table, dict[str, Any]]:
    track_id = state_table["track_id"].to_numpy()
    lat_center = state_table["lat_center"].to_numpy()
    lon_center = state_table["lon_center"].to_numpy()
    support_count = support_cell_counts(lat_center, lon_center)
    geometry_status = support_status(lat_center, lon_center, support_count)
    in_period = (era_hour >= CURRENT_PERIOD_START) & (era_hour <= CURRENT_PERIOD_END)

    current_track = current_states["track_id"].to_numpy()
    current_ms = current_states["time"].to_numpy().astype("datetime64[ms]").astype(np.int64)
    current_keys = {
        (int(track), int(time)): index
        for index, (track, time) in enumerate(zip(current_track, current_ms, strict=True))
    }
    state_ms = state_table["time"].to_numpy().astype("datetime64[ms]").astype(np.int64)
    state_keys = [(int(track), int(time)) for track, time in zip(track_id, state_ms, strict=True)]
    has_rows = np.fromiter((key in current_keys for key in state_keys), dtype=bool, count=len(state_keys))
    state_key_to_index = {key: index for index, key in enumerate(state_keys)}
    unexpected_keys = set(current_keys) - set(state_key_to_index)

    parquet_status = np.full(state_table.num_rows, "outside_comparison_period", dtype="U28")
    parquet_status[in_period & has_rows] = "present"
    parquet_status[in_period & ~has_rows & (support_count > 0)] = "absent_with_support"
    parquet_status[in_period & ~has_rows & (support_count == 0)] = "absent_no_support"

    expected_states = int(np.count_nonzero(in_period))
    present_states = int(np.count_nonzero(in_period & has_rows))
    missing = in_period & ~has_rows
    missing_with_support = int(np.count_nonzero(missing & (support_count > 0)))
    missing_no_support = int(np.count_nonzero(missing & (support_count == 0)))
    current_period_tracks = int(np.unique(track_id[in_period]).size)

    require(current_track_count == EXPECTED["current_parquet_tracks"], "Tracks no Parquet atual divergiram")
    require(current_states.num_rows == EXPECTED["current_parquet_states"], "Estados no Parquet atual divergiram")
    require(expected_states == EXPECTED["current_period_expected_states"], "Estados esperados divergiram")
    require(current_period_tracks == EXPECTED["current_period_tracks"], "Tracks esperadas divergiram")
    require(present_states == EXPECTED["current_parquet_states"], "Estados presentes divergiram")
    require(expected_states - present_states == EXPECTED["missing_states"], "Estados ausentes divergiram")
    require(missing_with_support == EXPECTED["missing_with_support"], "Ausentes com suporte divergiram")
    require(missing_no_support == EXPECTED["missing_no_support"], "Ausentes sem suporte divergiram")
    require(len(unexpected_keys) == EXPECTED["unexpected_parquet_states"], "Há estado inesperado no Parquet")
    require(
        int(support_count[in_period].sum()) == EXPECTED["current_period_support_cells"],
        "Total de células de suporte divergiu",
    )

    phases = state_table["phase"].to_pylist()
    current_lat = current_states["lat_center"].to_numpy()
    current_lon = current_states["lon_center"].to_numpy()
    current_phase = current_states["phase"].to_pylist()
    center_matches = 0
    phase_matches = 0
    for current_index, key in enumerate(zip(current_track, current_ms, strict=True)):
        state_index = state_key_to_index[(int(key[0]), int(key[1]))]
        center_matches += int(
            np.float32(lat_center[state_index]) == np.float32(current_lat[current_index])
            and np.float32(lon_center[state_index]) == np.float32(current_lon[current_index])
        )
        phase_matches += int(phases[state_index] == current_phase[current_index])
    require(center_matches == EXPECTED["matching_centers"], "Centros não correspondem ao Parquet")
    require(phase_matches == EXPECTED["matching_phases"], "phase não corresponde a period")

    special_report: dict[str, Any] = {}
    for cyclone_id, expectation in SPECIAL_CASES.items():
        selected = in_period & (track_id == cyclone_id)
        statuses = set(parquet_status[selected].tolist())
        require(int(np.count_nonzero(selected)) == expectation["states"], f"Estados de {cyclone_id} divergiram")
        require(statuses == {expectation["expected"]}, f"Status de {cyclone_id} divergiu: {statuses}")
        require(not np.any(has_rows[selected]), f"{cyclone_id} apareceu no Parquet")
        special_report[str(cyclone_id)] = {
            "state_count": int(np.count_nonzero(selected)),
            "has_parquet_rows": False,
            "parquet_state_status": expectation["expected"],
            "support_cell_count": int(support_count[selected].sum()),
            "support_status_counts": dict(sorted(Counter(geometry_status[selected]).items())),
        }

    enriched = state_table.append_column("in_current_parquet_period", pa.array(in_period))
    enriched = enriched.append_column("has_parquet_rows", pa.array(has_rows))
    enriched = enriched.append_column("support_cell_count", pa.array(support_count, type=pa.int32()))
    enriched = enriched.append_column("support_status", pa.array(geometry_status, type=pa.string()))
    enriched = enriched.append_column("parquet_state_status", pa.array(parquet_status, type=pa.string()))
    metadata = {
        b"product": b"cyclone states associated with nearest ERA5 6-hour time",
        b"source_product": relative(DEFAULT_TRACKS).encode(),
        b"source_doi": DOI.encode(),
        b"pipeline_version": PIPELINE_VERSION.encode(),
        b"time_rule": b"nearest 6 h; maximum 3 h; 3 h tie goes backward; one row per track_id+time",
        b"support_rule": b"0.25 degree grid lat[-65,-10] lon[-85,-15]; haversine R=6371 km; distance<=1100 km",
        b"support_status": b"full_support=continuous disk contained; partial_support=disk intersects and is truncated; no_support=zero grid cells",
    }
    enriched = enriched.replace_schema_metadata(metadata)

    geometry_counts = dict(sorted(Counter(geometry_status[in_period]).items()))
    missing_geometry_counts = dict(sorted(Counter(geometry_status[missing]).items()))
    report = {
        "current_parquet": {
            "tracks": current_track_count,
            "states": current_states.num_rows,
        },
        "reconstructed_current_period": {
            "tracks": current_period_tracks,
            "expected_states": expected_states,
            "present_states": present_states,
            "missing_states": expected_states - present_states,
            "missing_with_support": missing_with_support,
            "missing_no_support": missing_no_support,
            "support_cell_count": int(support_count[in_period].sum()),
            "support_status_counts": geometry_counts,
            "missing_support_status_counts": missing_geometry_counts,
        },
        "correspondence": {
            "matching_centers_after_float32": center_matches,
            "matching_phase_period": phase_matches,
            "unexpected_parquet_states": len(unexpected_keys),
        },
        "special_cases": special_report,
    }
    return enriched, report


def write_parquet_atomic(table: pa.Table, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    pq.write_table(
        table,
        temporary,
        compression="zstd",
        compression_level=9,
        use_dictionary=[name for name in ("region", "phase", "support_status", "parquet_state_status") if name in table.column_names],
        write_statistics=True,
        row_group_size=100_000,
    )
    written = pq.read_table(temporary)
    require(written.num_rows == table.num_rows, f"Validação pós-escrita falhou: {path}")
    require(written.schema.names == table.schema.names, f"Schema pós-escrita falhou: {path}")
    os.replace(temporary, path)


def schema_description(schema: pa.Schema) -> list[dict[str, Any]]:
    return [
        {"name": field.name, "type": str(field.type), "nullable": field.nullable}
        for field in schema
    ]


def load_downloaded_at(manifest_path: Path, source_path: Path) -> str:
    if manifest_path.is_file():
        try:
            value = json.loads(manifest_path.read_text(encoding="utf-8"))
            downloaded = value.get("source", {}).get("downloaded_at_utc")
            if downloaded:
                return downloaded
        except (json.JSONDecodeError, OSError, AttributeError):
            pass
    return datetime.fromtimestamp(source_path.stat().st_mtime, timezone.utc).isoformat().replace("+00:00", "Z")


def product_manifest(path: Path, table: pa.Table, role: str) -> dict[str, Any]:
    return {
        "path": relative(path),
        "role": role,
        "size_bytes": path.stat().st_size,
        "sha256": hash_file(path)["sha256"],
        "rows": table.num_rows,
        "schema": schema_description(table.schema),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--current-parquet", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--tracks-output", type=Path, default=DEFAULT_TRACKS)
    parser.add_argument("--states-output", type=Path, default=DEFAULT_STATES)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--remove-raw-after-success",
        action="store_true",
        help="Remove only the validated raw CSV, after every output and report passes validation.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_path = args.source.resolve()
    current_path = args.current_parquet.resolve()
    tracks_path = args.tracks_output.resolve()
    states_path = args.states_output.resolve()
    output_dir = args.output_dir.resolve()
    manifest_path = output_dir / "provenance_manifest.json"
    report_path = output_dir / "validation_report.json"

    source_file = validate_source_file(source_path)
    require(current_path.is_file(), f"Parquet atual ausente: {current_path}")
    current_hash = hash_file(current_path)["sha256"]
    require(
        current_hash == "3913a1d8ab49856212e1e5a19275b3644ae947dcf940872fb2f40a884d9efa0c",
        "SHA-256 do Parquet atual mudou; não é seguro publicar a validação conhecida",
    )
    source_table = read_source(source_path)
    source_validation = validate_hourly_source(source_table)
    tracks = canonical_tracks(source_table)

    state_base, era_hour, _ = nearest_six_hour_states(tracks)
    current_states, current_track_count = read_current_parquet_states(current_path)
    states, state_validation = enrich_and_validate_states(
        state_base,
        era_hour,
        current_states,
        current_track_count,
    )

    write_parquet_atomic(tracks, tracks_path)
    write_parquet_atomic(states, states_path)

    track_product = product_manifest(tracks_path, tracks, "canonical hourly track/lifecycle catalog")
    state_product = product_manifest(states_path, states, "nearest-ERA5-6h state and spatial-support catalog")

    offsets = Counter(states["track_minus_era5_hours"].to_pylist())
    validation_report = {
        "status": "passed",
        "generated_at_utc": utc_now(),
        "pipeline_version": PIPELINE_VERSION,
        "source": source_validation,
        "derived": {
            "hourly_catalog_rows": tracks.num_rows,
            "six_hour_state_rows": states.num_rows,
            "six_hour_tracks": int(pc.count_distinct(states["track_id"]).as_py()),
            "temporal_offset_hours": {str(key): value for key, value in sorted(offsets.items())},
            "duplicate_track_time": 0,
        },
        **state_validation,
        "checks": {
            "source_checksum": "passed",
            "source_schema": "passed",
            "source_counts": "passed",
            "source_key_uniqueness": "passed",
            "source_hourly_order": "passed",
            "phase_categories": "passed",
            "six_hour_association": "passed",
            "current_parquet_correspondence": "passed",
            "special_case_regressions": "passed",
        },
        "products": {
            "tracks": track_product,
            "states": state_product,
        },
    }
    write_json_atomic(report_path, validation_report)

    downloaded_at = load_downloaded_at(manifest_path, source_path)
    script_paths = [
        ROOT / "scripts" / "00_data_acquisition" / "download_tracks_zenodo.py",
        ROOT / "scripts" / "00_data_acquisition" / "prepare_tracks.py",
    ]
    manifest = {
        "manifest_schema_version": 1,
        "pipeline_version": PIPELINE_VERSION,
        "status": "validated_products_ready",
        "generated_at_utc": utc_now(),
        "source": {
            "provider": "Zenodo",
            "record_id": RECORD_ID,
            "record_version": RECORD_VERSION,
            "doi": DOI,
            "concept_doi": "10.5281/zenodo.18133431",
            "record_url": RECORD_URL,
            "download_url": f"{RECORD_URL}/files/{FILENAME}?download=1",
            "filename": FILENAME,
            "cache_path": relative(source_path),
            "downloaded_at_utc": downloaded_at,
            "verified_at_utc": utc_now(),
            "official_checksum": {"algorithm": "md5", "value": EXPECTED_MD5},
            "local_hashes": source_file["hashes"],
            "size_bytes": source_file["size_bytes"],
            "csv_header": source_file["header"],
            "parsed_schema": schema_description(source_table.schema),
            "rows": source_validation["rows"],
            "tracks": source_validation["tracks"],
            "date_min": source_validation["date_min"],
            "date_max": source_validation["date_max"],
            "phase_categories": source_validation["phase_categories"],
            "null_phase_rows": source_validation["null_phase_rows"],
        },
        "transformation": {
            "scripts": {
                relative(path): hash_file(path)["sha256"] for path in script_paths
            },
            "runtime": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "pyarrow": pa.__version__,
                "duckdb": duckdb.__version__,
            },
            "column_mapping": {
                "date": "date",
                "lon_center": "lon vor",
                "lat_center": "lat vor",
                "phase": "period",
            },
            "type_policy": {
                "track_id": "int64",
                "date_and_time": "timestamp[ms], UTC semantics, timezone-naive storage",
                "center_and_vor42": "float64 to preserve source precision",
                "region_and_phase": "string; source 'nan' phase parsed as null",
            },
            "six_hour_rule": "nearest ERA5 6 h; |delta|<=3 h; 3 h tie backward; one row per track_id+time",
            "support_rule": {
                "grid_degrees": 0.25,
                "latitude_range": [GRID_LAT_MIN, GRID_LAT_MAX],
                "longitude_range": [GRID_LON_MIN, GRID_LON_MAX],
                "distance": "spherical haversine",
                "earth_radius_km": EARTH_RADIUS_KM,
                "maximum_distance_km": SUPPORT_RADIUS_KM,
                "comparison": "<=",
            },
        },
        "derived_products": {
            "tracks": track_product,
            "states": state_product,
        },
        "validation": {
            "report_path": relative(report_path),
            "report_sha256": hash_file(report_path)["sha256"],
            "current_parquet_path": relative(current_path),
            "current_parquet_sha256": current_hash,
            "result": "passed",
        },
        "historical_reference": {
            "provider": "Mendeley Data",
            "doi": "10.17632/kwcvfr52hp.4",
            "role": "historical genealogy only; IDs and track universe are not the operational Zenodo catalog",
        },
    }
    write_json_atomic(manifest_path, manifest)

    print(f"Wrote {tracks_path} ({tracks_path.stat().st_size:,} bytes)")
    print(f"Wrote {states_path} ({states_path.stat().st_size:,} bytes)")
    print(f"Wrote {report_path}")
    print(f"Wrote {manifest_path}")

    if args.remove_raw_after_success:
        source_path.unlink()
        print(f"Removed validated raw source after successful conversion: {source_path}")


if __name__ == "__main__":
    main()
