"""Record the structure of the current development parquet without scientific analysis.

Run from anywhere with: python scripts/01_data_overview/inspect_parquet.py
Requires pyarrow. Input and output are fixed relative to this repository.
"""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "cyclone_exceedances_by_track_2010_2020_p90.parquet"
DOCUMENTATION = ROOT / "data" / "COLUNAS_cyclone_exceedances_by_track_2010_2020_p90.md"
OUTPUT = ROOT / "outputs" / "01_data_overview" / "structural_summary.json"
CATEGORICAL_COLUMNS = (
    "phase",
    "fixed_quadrant",
    "rotated_quadrant",
    "exceeded_15_6",
    "exceeded_20_0",
    "exceeded_25_0",
    "exceeded_q90",
    "exceeded_q95",
    "exceeded_q99",
)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def plain(value):
    """Convert metadata scalars to JSON-compatible values."""
    return value.isoformat() if hasattr(value, "isoformat") else value


def main() -> None:
    parquet = pq.ParquetFile(INPUT)
    metadata = parquet.metadata
    columns = []

    for field in parquet.schema_arrow:
        column_index = metadata.schema.names.index(field.name)
        stats = [
            metadata.row_group(i).column(column_index).statistics
            for i in range(metadata.num_row_groups)
        ]
        if any(item is None or not item.has_min_max or item.null_count is None for item in stats):
            raise ValueError(f"Complete Parquet statistics are required: {field.name}")

        columns.append(
            {
                "name": field.name,
                "type": str(field.type),
                "null_count": sum(item.null_count for item in stats),
                "min": plain(min(item.min for item in stats)),
                "max": plain(max(item.max for item in stats)),
            }
        )

    frequencies = {name: Counter() for name in CATEGORICAL_COLUMNS}
    track_ids = set()
    scan_columns = ["track_id", *CATEGORICAL_COLUMNS]
    for batch in parquet.iter_batches(columns=scan_columns, batch_size=262_144):
        track_ids.update(batch.column("track_id").to_pylist())
        for name in CATEGORICAL_COLUMNS:
            counts = pc.value_counts(batch.column(name)).to_pylist()
            frequencies[name].update({str(item["values"]): item["counts"] for item in counts})

    first_batch = next(parquet.iter_batches(batch_size=3))
    sample = [
        {name: plain(value) for name, value in row.items()}
        for row in first_batch.to_pylist()
    ]

    summary = {
        "input": str(INPUT.relative_to(ROOT)),
        "input_sha256": file_sha256(INPUT),
        "input_size_bytes": INPUT.stat().st_size,
        "column_documentation": str(DOCUMENTATION.relative_to(ROOT)),
        "column_documentation_sha256": file_sha256(DOCUMENTATION),
        "cyclone_identifier": "track_id",
        "unique_cyclone_count": len(track_ids),
        "row_count": metadata.num_rows,
        "column_count": metadata.num_columns,
        "row_group_count": metadata.num_row_groups,
        "statistics_source": "Parquet row-group metadata; frequencies scanned in batches",
        "columns": columns,
        "observed_category_counts": {
            name: dict(sorted(counts.items())) for name, counts in frequencies.items()
        },
        "first_three_rows": sample,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
