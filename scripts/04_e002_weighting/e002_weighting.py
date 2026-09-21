#!/usr/bin/env python3
"""Run E-002: equal-state versus equal-cyclone weighting sensitivity.

E-002 imports E-001's frozen geometry and aggregation functions so that only
the weighting changes. Paths are resolved from this file, so the pipeline is
reproducible from outside the repository root.
"""

from __future__ import annotations

import csv
import json
import math
import os
from pathlib import Path
import shutil
import sys
from typing import Any

import duckdb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts" / "03_e001_orientation"))

from e001_orientation import (  # noqa: E402
    EXPECTED_HASHES,
    METRIC_DIRECTIONS,
    PHASES,
    STATES_PATH,
    TRACKS_PATH,
    WIND_PATH,
    accumulate_exceedances,
    file_sha256,
    load_states,
    make_eligible_table,
    metric_values,
    query_q95_counts,
)


PROTOCOL_PATH = SCRIPT_DIR / "protocol.json"
E001_SUMMARY_PATH = ROOT / "outputs" / "03_e001_orientation" / "summary.json"
OUTPUT = ROOT / "outputs" / "04_e002_weighting"
PRIMARY_METRICS = (
    "entropy_nats",
    "area50_km2",
    "area75_km2",
    "area90_km2",
    "rms_about_centroid_km",
)
ALL_METRICS = tuple(METRIC_DIRECTIONS)
REPRESENTATIONS = ("centered", "motion_relative")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    require(bool(rows), f"Sem linhas para {path.name}")
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalized_rows(matrix: np.ndarray, positive_states_by_track: np.ndarray) -> np.ndarray:
    """Give each represented cyclone total mass one."""
    result = np.zeros_like(matrix, dtype=np.float32)
    included = positive_states_by_track > 0
    result[included] = matrix[included] / positive_states_by_track[included, None]
    row_totals = result.sum(axis=1)
    np.testing.assert_allclose(row_totals[included], 1.0, rtol=2e-5, atol=2e-5)
    require(np.all(row_totals[~included] == 0), "Ciclone sem estado positivo recebeu massa")
    return result


def probability(matrix: np.ndarray) -> np.ndarray:
    mass = np.asarray(matrix, dtype=np.float64).sum(axis=0)
    require(float(mass.sum()) > 0, "Distribuicao espacial vazia")
    return mass / mass.sum()


def matrix_metrics(probability_matrix: np.ndarray, x: np.ndarray, y: np.ndarray, bin_area: float) -> dict[str, np.ndarray]:
    """Vectorized E-001 metrics for bootstrap probability maps."""
    safe = np.where(probability_matrix > 0, probability_matrix, 1.0)
    result: dict[str, np.ndarray] = {
        "entropy_nats": -np.sum(
            np.where(probability_matrix > 0, probability_matrix * np.log(safe), 0.0), axis=1
        )
    }
    ordered = np.sort(probability_matrix, axis=1)[:, ::-1]
    cumulative = np.cumsum(ordered, axis=1)
    for fraction in (0.50, 0.75, 0.90):
        result[f"area{int(fraction * 100)}_km2"] = (
            np.argmax(cumulative >= fraction, axis=1) + 1
        ) * bin_area
    mean_x = probability_matrix @ x
    mean_y = probability_matrix @ y
    second_x = probability_matrix @ (x * x)
    second_y = probability_matrix @ (y * y)
    result["rms_about_centroid_km"] = np.sqrt(
        np.maximum(0.0, second_x - mean_x * mean_x)
        + np.maximum(0.0, second_y - mean_y * mean_y)
    )
    return result


def bootstrap_differences(
    centered_state: np.ndarray,
    motion_state: np.ndarray,
    positive_states_by_track: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    bin_area: float,
    replicates: int,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, dict[str, float]]]]:
    """Recalculate both estimands after resampling eligible cyclones."""
    tracks = centered_state.shape[0]
    rng = np.random.default_rng(seed)
    multiplicity = rng.multinomial(
        tracks, np.full(tracks, 1.0 / tracks), size=replicates
    ).astype(np.float32)
    centered_cyclone = normalized_rows(centered_state, positive_states_by_track)
    motion_cyclone = normalized_rows(motion_state, positive_states_by_track)
    masses = {
        "centered_equal_state": multiplicity @ centered_state,
        "motion_relative_equal_state": multiplicity @ motion_state,
        "centered_equal_cyclone": multiplicity @ centered_cyclone,
        "motion_relative_equal_cyclone": multiplicity @ motion_cyclone,
    }
    metrics: dict[str, dict[str, np.ndarray]] = {}
    for name, mass in masses.items():
        total = mass.sum(axis=1)
        require(np.all(total > 0), f"Replica sem excedencias em {name}")
        metrics[name] = matrix_metrics(mass / total[:, None], x, y, bin_area)

    contrasts = {
        "centered_equal_cyclone_minus_equal_state": (
            "centered_equal_cyclone",
            "centered_equal_state",
        ),
        "motion_equal_cyclone_minus_equal_state": (
            "motion_relative_equal_cyclone",
            "motion_relative_equal_state",
        ),
        "motion_minus_centered_equal_state": (
            "motion_relative_equal_state",
            "centered_equal_state",
        ),
        "motion_minus_centered_equal_cyclone": (
            "motion_relative_equal_cyclone",
            "centered_equal_cyclone",
        ),
    }
    rows: list[dict[str, Any]] = []
    summaries: dict[str, dict[str, dict[str, float]]] = {}
    for contrast, (left, right) in contrasts.items():
        summaries[contrast] = {}
        for metric in PRIMARY_METRICS:
            values = metrics[left][metric] - metrics[right][metric]
            low, median, high = np.quantile(values, [0.025, 0.5, 0.975])
            summaries[contrast][metric] = {
                "ci95_low": float(low),
                "bootstrap_median": float(median),
                "ci95_high": float(high),
                "probability_difference_below_zero": float(np.mean(values < 0)),
            }
            for index, value in enumerate(values):
                rows.append(
                    {
                        "replicate": index + 1,
                        "contrast": contrast,
                        "metric": metric,
                        "difference": float(value),
                    }
                )
    return rows, summaries


def cyclone_contributions(
    eligible: Any,
    q95_counts: np.ndarray,
    track_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any], np.ndarray]:
    track_index = eligible["track_idx"].to_numpy()
    positive = q95_counts > 0
    eligible_count = np.bincount(track_index, minlength=track_count)
    positive_count = np.bincount(track_index[positive], minlength=track_count)
    positive_cyclones = int(np.count_nonzero(positive_count))
    total_positive_states = int(positive_count.sum())
    track_ids = eligible["track_id"].to_numpy()
    times = eligible["time"].to_numpy().astype("datetime64[ms]")
    unique_track_ids = np.zeros(track_count, dtype=np.int64)
    minimum_time = np.empty(track_count, dtype="datetime64[ms]")
    maximum_time = np.empty(track_count, dtype="datetime64[ms]")
    for index in range(track_count):
        mask = track_index == index
        unique_track_ids[index] = int(track_ids[mask][0])
        minimum_time[index] = times[mask].min()
        maximum_time[index] = times[mask].max()
    equal_state = positive_count / total_positive_states
    equal_cyclone = np.where(positive_count > 0, 1.0 / positive_cyclones, 0.0)
    order = np.argsort(-equal_state, kind="stable")
    rank = np.empty(track_count, dtype=np.int32)
    rank[order] = np.arange(1, track_count + 1)
    rows = []
    for index in range(track_count):
        span_hours = float((maximum_time[index] - minimum_time[index]) / np.timedelta64(1, "h"))
        rows.append(
            {
                "track_id": int(unique_track_ids[index]),
                "eligible_states": int(eligible_count[index]),
                "q95_positive_states": int(positive_count[index]),
                "eligible_duration_hours": int(eligible_count[index] * 6),
                "q95_positive_duration_hours": int(positive_count[index] * 6),
                "eligible_time_span_hours": span_hours,
                "equal_state_mass_fraction": float(equal_state[index]),
                "equal_cyclone_mass_fraction": float(equal_cyclone[index]),
                "equal_state_contribution_rank": int(rank[index]),
            }
        )

    positive_values = positive_count[positive_count > 0]
    quantiles = {
        f"p{int(q * 100):02d}": float(np.quantile(positive_values, q))
        for q in (0.0, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0)
    }
    ordered_positive_weights = np.sort(equal_state[equal_state > 0])[::-1]
    top_shares = {}
    for percentage in (0.01, 0.05, 0.10):
        count = int(math.ceil(positive_cyclones * percentage))
        top_shares[f"top_{int(percentage * 100)}_percent"] = {
            "cyclones": count,
            "equal_state_mass_fraction": float(ordered_positive_weights[:count].sum()),
            "equal_cyclone_mass_fraction": float(count / positive_cyclones),
        }
    hhi_state = float(np.sum(equal_state * equal_state))
    hhi_cyclone = float(np.sum(equal_cyclone * equal_cyclone))
    summary = {
        "positive_cyclones": positive_cyclones,
        "maximum_equal_state_contribution": float(ordered_positive_weights[0]),
        "maximum_equal_cyclone_contribution": float(1.0 / positive_cyclones),
        "top_shares": top_shares,
        "positive_state_count_quantiles": quantiles,
        "equal_state": {"hhi": hhi_state, "effective_cyclones": float(1.0 / hhi_state)},
        "equal_cyclone": {"hhi": hhi_cyclone, "effective_cyclones": float(1.0 / hhi_cyclone)},
    }
    return rows, summary, positive_count


def concentration_from_counts(positive_states_by_track: np.ndarray) -> dict[str, float | int]:
    included = positive_states_by_track > 0
    count = int(np.count_nonzero(included))
    total = int(positive_states_by_track.sum())
    require(count > 0 and total > 0, "Estrato sem ciclones q95-positivos")
    state_weights = positive_states_by_track[included] / total
    hhi_state = float(np.sum(state_weights * state_weights))
    hhi_cyclone = float(1.0 / count)
    return {
        "q95_positive_cyclones": count,
        "q95_positive_states": total,
        "maximum_equal_state_contribution": float(state_weights.max()),
        "hhi_equal_state": hhi_state,
        "effective_cyclones_equal_state": float(1.0 / hhi_state),
        "hhi_equal_cyclone": hhi_cyclone,
        "effective_cyclones_equal_cyclone": float(count),
    }


def map_figure(
    left: np.ndarray,
    right: np.ndarray,
    left_title: str,
    right_title: str,
    difference_title: str,
    title: str,
    path: Path,
    bins_per_axis: int,
    domain_km: float,
) -> None:
    left_p = probability(left)
    right_p = probability(right)
    difference = right_p - left_p
    maximum = max(float(left_p.max()), float(right_p.max()))
    limit = float(np.max(np.abs(difference)))
    figure, axes = plt.subplots(1, 3, figsize=(14.4, 4.35), constrained_layout=True)
    extent = (-domain_km, domain_km, -domain_km, domain_km)
    image = axes[0].imshow(left_p.reshape(bins_per_axis, bins_per_axis), origin="lower", extent=extent, cmap="magma", vmin=0, vmax=maximum)
    axes[1].imshow(right_p.reshape(bins_per_axis, bins_per_axis), origin="lower", extent=extent, cmap="magma", vmin=0, vmax=maximum)
    diff_image = axes[2].imshow(
        difference.reshape(bins_per_axis, bins_per_axis), origin="lower", extent=extent,
        cmap="RdBu_r", norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit)
    )
    for axis, panel_title in zip(axes, (left_title, right_title, difference_title), strict=True):
        axis.set_title(panel_title)
        axis.axhline(0, color="white", linewidth=0.4, alpha=0.7)
        axis.axvline(0, color="white", linewidth=0.4, alpha=0.7)
        axis.set(xlabel="x (km): leste / direita", ylabel="y (km): norte / frente", aspect="equal")
    axes[2].lines[-2].set_color("#555555")
    axes[2].lines[-1].set_color("#555555")
    figure.colorbar(image, ax=axes[:2], shrink=0.78, label="Massa q95 normalizada por bin")
    figure.colorbar(diff_image, ax=axes[2], shrink=0.78, label="Diferença de massa")
    figure.suptitle(title, fontsize=13, fontweight="bold")
    figure.savefig(path, dpi=180)
    plt.close(figure)


def contribution_figures(rows: list[dict[str, Any]]) -> None:
    positive_counts = np.asarray([row["q95_positive_states"] for row in rows if row["q95_positive_states"] > 0])
    figure, axis = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
    bins = np.arange(0.5, positive_counts.max() + 1.5)
    axis.hist(positive_counts, bins=bins, color="#376d8c", edgecolor="white", linewidth=0.25)
    axis.axvline(np.median(positive_counts), color="#b23a2b", label=f"mediana = {np.median(positive_counts):g}")
    axis.set(xlabel="Estados q95-positivos por ciclone", ylabel="Ciclones", title="E-002 · Participação temporal dos ciclones")
    axis.grid(alpha=0.18)
    axis.legend(frameon=False)
    figure.savefig(OUTPUT / "positive_states_per_cyclone.png", dpi=180)
    plt.close(figure)

    weights = np.sort(np.asarray([row["equal_state_mass_fraction"] for row in rows if row["q95_positive_states"] > 0]))[::-1]
    x = np.arange(1, weights.size + 1) / weights.size * 100
    figure, axis = plt.subplots(figsize=(7.2, 4.4), constrained_layout=True)
    axis.plot(x, np.cumsum(weights) * 100, color="#8c2d62", linewidth=2, label="Equal-state")
    axis.plot(x, x, color="#555555", linestyle="--", label="Equal-cyclone")
    axis.set(xlabel="Ciclones com maior peso acumulados (%)", ylabel="Massa acumulada (%)", xlim=(0, 100), ylim=(0, 100), title="E-002 · Concentração da contribuição")
    axis.grid(alpha=0.18)
    axis.legend(frameon=False)
    figure.savefig(OUTPUT / "cumulative_cyclone_contribution.png", dpi=180)
    plt.close(figure)


def metric_interval_figure(
    point_contrasts: dict[str, dict[str, float]],
    bootstrap: dict[str, dict[str, dict[str, float]]],
) -> None:
    labels = {
        "centered_equal_cyclone_minus_equal_state": "Centered: ciclone − estado",
        "motion_equal_cyclone_minus_equal_state": "Motion: ciclone − estado",
        "motion_minus_centered_equal_cyclone": "Motion − centered: equal-cyclone",
    }
    metrics = list(PRIMARY_METRICS)
    titles = ["H (nat)", "A50 (km²)", "A75 (km²)", "A90 (km²)", "RMS (km)"]
    colors = ("#376d8c", "#8c2d62", "#d17831")
    figure, axes = plt.subplots(1, 5, figsize=(15.5, 4.3), constrained_layout=True)
    for axis, metric, title in zip(axes, metrics, titles, strict=True):
        for row, (contrast, label) in enumerate(labels.items()):
            point = point_contrasts[contrast][metric]
            low = bootstrap[contrast][metric]["ci95_low"]
            high = bootstrap[contrast][metric]["ci95_high"]
            axis.errorbar(point, row, xerr=[[point - low], [high - point]], fmt="o", color=colors[row], capsize=3)
        axis.axvline(0, color="#555555", linewidth=1)
        axis.set_title(title)
        axis.grid(axis="x", alpha=0.18)
        axis.set_yticks(range(len(labels)))
        axis.set_yticklabels(list(labels.values()) if axis is axes[0] else [])
    figure.suptitle("E-002 · Diferenças pontuais e IC95% por bootstrap de ciclones", fontsize=13, fontweight="bold")
    figure.savefig(OUTPUT / "metric_differences_bootstrap.png", dpi=180)
    plt.close(figure)


def robustness_classification(
    contrasts: dict[str, dict[str, float]],
    bootstrap: dict[str, dict[str, dict[str, float]]],
) -> dict[str, Any]:
    difference = contrasts["motion_minus_centered_equal_cyclone"]
    core_tail_conflict = (
        np.sign(difference["area50_km2"]) != np.sign(difference["area75_km2"])
        and np.sign(difference["area50_km2"]) != np.sign(difference["area90_km2"])
        and np.sign(difference["area50_km2"]) != np.sign(difference["rms_about_centroid_km"])
    )
    signs = np.asarray([np.sign(difference[metric]) for metric in PRIMARY_METRICS])
    all_same_direction = bool(np.all(signs < 0) or np.all(signs > 0))
    interval = bootstrap["motion_minus_centered_equal_cyclone"]
    interval_direction = (
        interval["entropy_nats"]["ci95_high"] < 0
        and interval["area75_km2"]["ci95_high"] < 0
    ) or (
        interval["entropy_nats"]["ci95_low"] > 0
        and interval["area75_km2"]["ci95_low"] > 0
    )
    if core_tail_conflict and not all_same_direction:
        classification = "ROBUST_TO_WEIGHTING"
        status = "ADOPTED"
    elif all_same_direction and interval_direction:
        classification = "SENSITIVE_TO_WEIGHTING"
        status = "REJECTED"
    else:
        classification = "PARTIALLY_SENSITIVE"
        status = "INCONCLUSIVE"
    return {
        "experiment_status": status,
        "classification": classification,
        "checks": {
            "equal_cyclone_core_tail_conflict": bool(core_tail_conflict),
            "all_five_metrics_same_direction": all_same_direction,
            "entropy_and_area75_intervals_same_nonzero_direction": bool(interval_direction),
        },
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROTOCOL_PATH, OUTPUT / "protocol.json")
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    e001_summary = json.loads(E001_SUMMARY_PATH.read_text(encoding="utf-8"))
    for path, expected in (
        (STATES_PATH, EXPECTED_HASHES[STATES_PATH.name]),
        (TRACKS_PATH, EXPECTED_HASHES[TRACKS_PATH.name]),
        (WIND_PATH, EXPECTED_HASHES[WIND_PATH.name]),
    ):
        require(path.is_file(), f"Entrada ausente: {path}")
        require(file_sha256(path) == expected, f"SHA-256 inesperado: {path.name}")

    domain_km = float(protocol["relative_domain_km"][1])
    bin_km = float(protocol["bin_size_km"])
    bins_per_axis = int(round(2 * domain_km / bin_km))
    edges = np.linspace(-domain_km, domain_km, bins_per_axis + 1)
    centers = (edges[:-1] + edges[1:]) / 2
    center_x, center_y = np.meshgrid(centers, centers)
    x_centers, y_centers = center_x.ravel(), center_y.ravel()
    bin_area = bin_km * bin_km

    states = load_states(protocol)
    eligible, track_lookup, _ = make_eligible_table(states)
    connection = duckdb.connect()
    connection.execute("SET threads TO 1")
    connection.register("eligible", eligible)
    q95_counts = query_q95_counts(connection)
    matrices, _, raw_centered, raw_motion = accumulate_exceedances(
        connection, eligible, len(track_lookup), q95_counts, domain_km, bin_km, bins_per_axis
    )
    connection.close()

    expected = protocol["expected_e001_population"]
    observed = {
        "eligible_cyclones": len(track_lookup),
        "eligible_states": eligible.num_rows,
        "q95_positive_states": int(np.count_nonzero(q95_counts)),
        "q95_exceedance_cells": int(q95_counts.sum()),
        "heading_excluded_states": int(np.sum(states["base_mask"] & ~states["reliable"])),
    }
    require(observed == expected, f"Populacao divergiu de E-001: {observed} != {expected}")
    require(int(raw_centered.sum()) == expected["q95_exceedance_cells"], "Celulas centered divergiram")
    require(int(raw_motion.sum()) == expected["q95_exceedance_cells"], "Celulas motion divergiram")

    contribution_rows, contribution_summary, positive_all = cyclone_contributions(
        eligible, q95_counts, len(track_lookup)
    )
    write_csv(OUTPUT / "cyclone_contributions.csv", contribution_rows)
    contribution_figures(contribution_rows)

    positive = q95_counts > 0
    track_indices = eligible["track_idx"].to_numpy()
    phases = np.asarray(eligible["phase_group"].to_pylist(), dtype=object)
    strata = ("all", *PHASES)
    distributions: dict[str, dict[str, np.ndarray]] = {}
    metrics: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    metric_rows: list[dict[str, Any]] = []
    concentration_by_stratum: dict[str, dict[str, float | int]] = {}
    for stratum in strata:
        state_mask = np.ones(eligible.num_rows, dtype=bool) if stratum == "all" else phases == stratum
        positive_by_track = np.bincount(track_indices[state_mask & positive], minlength=len(track_lookup))
        concentration_by_stratum[stratum] = concentration_from_counts(positive_by_track)
        centered_state = matrices[stratum][0]
        motion_state = matrices[stratum][1]
        centered_cyclone = normalized_rows(centered_state, positive_by_track)
        motion_cyclone = normalized_rows(motion_state, positive_by_track)
        distributions[stratum] = {
            "centered_equal_state": centered_state,
            "motion_relative_equal_state": motion_state,
            "centered_equal_cyclone": centered_cyclone,
            "motion_relative_equal_cyclone": motion_cyclone,
        }
        metrics[stratum] = {}
        for representation, state_matrix, cyclone_matrix in (
            ("centered", centered_state, centered_cyclone),
            ("motion_relative", motion_state, motion_cyclone),
        ):
            metrics[stratum][representation] = {}
            for weighting, matrix in (("equal_state", state_matrix), ("equal_cyclone", cyclone_matrix)):
                values = metric_values(matrix.sum(axis=0), x_centers, y_centers, bin_area)
                metrics[stratum][representation][weighting] = values
                metric_rows.append(
                    {
                        "stratum": stratum,
                        "representation": representation,
                        "weighting": weighting,
                        "cyclones_with_q95": int(np.count_nonzero(positive_by_track)),
                        "q95_positive_states": int(positive_by_track.sum()),
                        **values,
                    }
                )
    write_csv(OUTPUT / "metrics.csv", metric_rows)
    write_csv(
        OUTPUT / "contribution_concentration_by_phase.csv",
        [{"stratum": stratum, **values} for stratum, values in concentration_by_stratum.items()],
    )

    # Regression against the immutable E-001 products, including bootstrap.
    regression: dict[str, Any] = {"population_exact": observed == expected, "metrics": {}}
    for representation in REPRESENTATIONS:
        old_name = representation
        current = metrics["all"][representation]["equal_state"]
        prior = e001_summary["comparisons"]["all"][old_name]
        regression["metrics"][representation] = {}
        for metric in ALL_METRICS:
            difference = float(current[metric] - prior[metric])
            regression["metrics"][representation][metric] = difference
            require(abs(difference) < 1e-6, f"Regressao E-001 falhou: {representation} {metric}: {difference}")

    global_maps = distributions["all"]
    bootstrap_rows, bootstrap_summary = bootstrap_differences(
        global_maps["centered_equal_state"],
        global_maps["motion_relative_equal_state"],
        positive_all,
        x_centers,
        y_centers,
        bin_area,
        int(protocol["bootstrap_replicates"]),
        int(protocol["bootstrap_seed"]),
    )
    write_csv(OUTPUT / "bootstrap_differences.csv", bootstrap_rows)
    for metric in PRIMARY_METRICS:
        current = bootstrap_summary["motion_minus_centered_equal_state"][metric]
        prior = e001_summary["comparisons"]["all"]["bootstrap"][metric]
        for field in ("ci95_low", "bootstrap_median", "ci95_high", "probability_difference_below_zero"):
            difference = float(current[field] - prior[field])
            require(abs(difference) < 1e-6, f"Bootstrap E-001 divergiu: {metric} {field}: {difference}")
    regression["bootstrap_equal_state_exact_within_1e-6"] = True

    contrast_definitions = {
        "centered_equal_cyclone_minus_equal_state": (
            ("centered", "equal_cyclone"), ("centered", "equal_state")
        ),
        "motion_equal_cyclone_minus_equal_state": (
            ("motion_relative", "equal_cyclone"), ("motion_relative", "equal_state")
        ),
        "motion_minus_centered_equal_state": (
            ("motion_relative", "equal_state"), ("centered", "equal_state")
        ),
        "motion_minus_centered_equal_cyclone": (
            ("motion_relative", "equal_cyclone"), ("centered", "equal_cyclone")
        ),
    }
    contrasts: dict[str, dict[str, float]] = {}
    comparison_rows: list[dict[str, Any]] = []
    phase_effects: dict[str, dict[str, dict[str, float]]] = {}
    for stratum in strata:
        phase_effects[stratum] = {}
        for contrast, (left, right) in contrast_definitions.items():
            left_metrics = metrics[stratum][left[0]][left[1]]
            right_metrics = metrics[stratum][right[0]][right[1]]
            values = {metric: float(left_metrics[metric] - right_metrics[metric]) for metric in ALL_METRICS}
            phase_effects[stratum][contrast] = values
            if stratum == "all":
                contrasts[contrast] = values
            for metric, value in values.items():
                uncertainty = bootstrap_summary.get(contrast, {}).get(metric, {}) if stratum == "all" else {}
                comparison_rows.append(
                    {
                        "stratum": stratum,
                        "contrast": contrast,
                        "metric": metric,
                        "difference": value,
                        "ci95_low": uncertainty.get("ci95_low", ""),
                        "bootstrap_median": uncertainty.get("bootstrap_median", ""),
                        "ci95_high": uncertainty.get("ci95_high", ""),
                        "probability_difference_below_zero": uncertainty.get("probability_difference_below_zero", ""),
                    }
                )
    write_csv(OUTPUT / "metric_comparisons.csv", comparison_rows)

    total_variation = {}
    for representation in REPRESENTATIONS:
        state_p = probability(global_maps[f"{representation}_equal_state"])
        cyclone_p = probability(global_maps[f"{representation}_equal_cyclone"])
        total_variation[representation] = float(0.5 * np.abs(cyclone_p - state_p).sum())

    spatial_rows = []
    for name, matrix in global_maps.items():
        p = probability(matrix)
        representation, weighting = (
            ("motion_relative", name.removeprefix("motion_relative_"))
            if name.startswith("motion_relative")
            else ("centered", name.removeprefix("centered_"))
        )
        for index, value in enumerate(p):
            spatial_rows.append(
                {
                    "representation": representation,
                    "weighting": weighting,
                    "bin_x_center_km": float(x_centers[index]),
                    "bin_y_center_km": float(y_centers[index]),
                    "probability_mass": float(value),
                }
            )
    write_csv(OUTPUT / "spatial_distributions.csv", spatial_rows)

    map_figure(global_maps["centered_equal_state"], global_maps["centered_equal_cyclone"], "Centered · equal-state", "Centered · equal-cyclone", "Cyclone − state", "E-002 · Efeito do weighting em centered", OUTPUT / "centered_weighting_comparison.png", bins_per_axis, domain_km)
    map_figure(global_maps["motion_relative_equal_state"], global_maps["motion_relative_equal_cyclone"], "Motion-relative · equal-state", "Motion-relative · equal-cyclone", "Cyclone − state", "E-002 · Efeito do weighting em motion-relative", OUTPUT / "motion_weighting_comparison.png", bins_per_axis, domain_km)
    map_figure(global_maps["centered_equal_cyclone"], global_maps["motion_relative_equal_cyclone"], "Centered · equal-cyclone", "Motion-relative · equal-cyclone", "Motion − centered", "E-002 · Representações sob peso igual por ciclone", OUTPUT / "representation_equal_cyclone.png", bins_per_axis, domain_km)
    metric_interval_figure(contrasts, bootstrap_summary)

    decision = robustness_classification(contrasts, bootstrap_summary)
    summary = {
        "experiment": {"id": "E-002", "status": decision["experiment_status"]},
        "completed_date": protocol["completed_date"],
        "protocol": protocol,
        "population": {
            **observed,
            "q95_positive_cyclones": contribution_summary["positive_cyclones"],
            "base_states": int(np.sum(states["base_mask"])),
        },
        "contribution_concentration": contribution_summary,
        "contribution_concentration_by_stratum": concentration_by_stratum,
        "metrics": metrics,
        "contrasts": contrasts,
        "total_variation": total_variation,
        "bootstrap": bootstrap_summary,
        "phase_effects": phase_effects,
        "e001_regression": regression,
        "decision": decision,
        "estimand_interpretation": {
            "equal_state": "Distribuicao esperada ao selecionar aleatoriamente um estado q95-positivo",
            "equal_cyclone": "Media das distribuicoes por ciclone ao selecionar aleatoriamente um ciclone q95-positivo",
            "adoption": "Nenhum estimando substitui o outro; usar equal-state para a populacao de estados e equal-cyclone para a populacao de ciclones, mantendo o outro como sensibilidade",
        },
        "reproducibility": {
            "input_sha256": {path.name: file_sha256(path) for path in (TRACKS_PATH, STATES_PATH, WIND_PATH)},
            "e001_summary_sha256": file_sha256(E001_SUMMARY_PATH),
            "protocol_sha256": file_sha256(PROTOCOL_PATH),
            "script_sha256": file_sha256(Path(__file__)),
            "bootstrap_seed": protocol["bootstrap_seed"],
        },
    }
    atomic_json(OUTPUT / "summary.json", summary)
    print(json.dumps({
        "status": decision,
        "population": summary["population"],
        "contribution_concentration": contribution_summary,
        "contrasts": contrasts,
        "total_variation": total_variation,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
