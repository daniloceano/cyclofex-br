#!/usr/bin/env python3
"""Download and validate the canonical Zenodo cyclone-track source.

The raw CSV is intentionally cached under ``data/raw/`` (gitignored).  A
valid existing file is reused; an invalid existing file is never overwritten.

Run from any directory::

    .venv/bin/python scripts/00_data_acquisition/download_tracks_zenodo.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
PIPELINE_VERSION = "1.0.0"

RECORD_ID = 18133432
RECORD_VERSION = 1
DOI = "10.5281/zenodo.18133432"
CONCEPT_DOI = "10.5281/zenodo.18133431"
RECORD_URL = f"https://zenodo.org/records/{RECORD_ID}"
FILENAME = "tracks_SAt_filtered_with_energetics.csv"
DOWNLOAD_URL = f"{RECORD_URL}/files/{FILENAME}?download=1"
EXPECTED_SIZE = 180_778_076
EXPECTED_MD5 = "a413e7f89d20b5b18a9da8b671b53d72"
EXPECTED_SHA256 = "bf1059ab2f1896c6df942a290d7676bce701f6d3cbf7ac9193f5c6b51d63cc26"
EXPECTED_HEADER = [
    "track_id",
    "date",
    "lon vor",
    "lat vor",
    "vor42",
    "region",
    "period",
    "Az",
    "Ae",
    "Kz",
    "Ke",
    "Cz",
    "Ca",
    "Ck",
    "Ce",
    "BAz",
    "BAe",
    "BKz",
    "BKe",
    "BΦZ",
    "BΦE",
    "Gz",
    "Ge",
    "∂Az/∂t (finite diff.)",
    "∂Ae/∂t (finite diff.)",
    "∂Kz/∂t (finite diff.)",
    "∂Ke/∂t (finite diff.)",
    "RGz",
    "RKz",
    "RGe",
    "RKe",
]

DEFAULT_DESTINATION = ROOT / "data" / "raw" / "zenodo" / str(RECORD_ID) / FILENAME
DEFAULT_MANIFEST = ROOT / "outputs" / "00_data_acquisition" / "provenance_manifest.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def hash_file(path: Path) -> dict[str, str]:
    md5 = hashlib.md5()  # nosec B324: required to verify the publisher checksum
    sha256 = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            md5.update(chunk)
            sha256.update(chunk)
    return {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}


def read_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as source:
        return next(csv.reader(source))


def validate_source(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise SystemExit(f"Fonte não encontrada: {path}")

    size = path.stat().st_size
    hashes = hash_file(path)
    header = read_header(path)
    errors: list[str] = []
    if size != EXPECTED_SIZE:
        errors.append(f"tamanho {size}, esperado {EXPECTED_SIZE}")
    if hashes["md5"] != EXPECTED_MD5:
        errors.append(f"MD5 {hashes['md5']}, esperado {EXPECTED_MD5}")
    if hashes["sha256"] != EXPECTED_SHA256:
        errors.append(f"SHA-256 {hashes['sha256']}, esperado {EXPECTED_SHA256}")
    if header != EXPECTED_HEADER:
        errors.append("header/schema CSV diferente do registro esperado")
    if errors:
        raise SystemExit(
            "Arquivo Zenodo inválido; ele foi preservado e não será sobrescrito:\n- "
            + "\n- ".join(errors)
        )
    return {"size_bytes": size, "hashes": hashes, "header": header}


def load_existing_manifest(manifest_path: Path) -> dict[str, object] | None:
    if not manifest_path.is_file():
        return None
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_json_atomic(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def download(destination: Path, timeout: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    if partial.exists():
        raise SystemExit(
            f"Download parcial já existe e foi preservado: {partial}. "
            "Inspecione ou remova-o explicitamente antes de tentar novamente."
        )

    request = urllib.request.Request(
        DOWNLOAD_URL,
        headers={"User-Agent": "cyclofex-br-data-pipeline/1.0"},
    )
    print(f"Downloading {DOWNLOAD_URL}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, partial.open("xb") as target:
            while chunk := response.read(1024 * 1024):
                target.write(chunk)
    except Exception as error:
        raise SystemExit(
            f"Download falhou; conteúdo parcial preservado em {partial}: {error}"
        ) from error

    validate_source(partial)
    os.replace(partial, destination)


def source_manifest(
    destination: Path,
    validation: dict[str, object],
    downloaded_at: str,
) -> dict[str, object]:
    return {
        "manifest_schema_version": 1,
        "pipeline_version": PIPELINE_VERSION,
        "status": "source_validated",
        "generated_at_utc": utc_now(),
        "source": {
            "provider": "Zenodo",
            "record_id": RECORD_ID,
            "record_version": RECORD_VERSION,
            "doi": DOI,
            "concept_doi": CONCEPT_DOI,
            "record_url": RECORD_URL,
            "download_url": DOWNLOAD_URL,
            "filename": FILENAME,
            "cache_path": display_path(destination),
            "downloaded_at_utc": downloaded_at,
            "verified_at_utc": utc_now(),
            "official_checksum": {"algorithm": "md5", "value": EXPECTED_MD5},
            "expected_sha256": EXPECTED_SHA256,
            "local_hashes": validation["hashes"],
            "size_bytes": validation["size_bytes"],
            "csv_header": validation["header"],
        },
        "historical_reference": {
            "provider": "Mendeley Data",
            "doi": "10.17632/kwcvfr52hp.4",
            "role": "historical genealogy only; not the operational catalog input",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--timeout", type=int, default=120)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destination = args.destination.resolve()
    manifest_path = args.manifest.resolve()
    prior_manifest = load_existing_manifest(manifest_path)
    prior_source_value = prior_manifest.get("source", {}) if prior_manifest else {}
    prior_source = prior_source_value if isinstance(prior_source_value, dict) else {}
    prior_download_time = prior_source.get("downloaded_at_utc")

    if destination.exists():
        validation = validate_source(destination)
        downloaded_at = prior_download_time or datetime.fromtimestamp(
            destination.stat().st_mtime, timezone.utc
        ).isoformat().replace("+00:00", "Z")
        print(f"Reusing valid cached source: {destination}")
    else:
        download(destination, args.timeout)
        validation = validate_source(destination)
        downloaded_at = utc_now()
        print(f"Validated new download: {destination}")

    next_manifest = source_manifest(destination, validation, downloaded_at)
    # A cache verification must not discard a completed transformation manifest.
    # Derived metadata remain valid because the source hashes above are immutable
    # pipeline constants and have just been revalidated.
    if prior_manifest and prior_manifest.get("status") == "validated_products_ready":
        next_source = next_manifest["source"]
        assert isinstance(next_source, dict)
        next_manifest = {
            **prior_manifest,
            "generated_at_utc": utc_now(),
            "source": {**prior_source, **next_source},
        }
    write_json_atomic(manifest_path, next_manifest)
    print(f"Wrote {manifest_path}")


if __name__ == "__main__":
    main()
