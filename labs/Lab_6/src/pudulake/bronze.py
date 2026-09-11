"""Ingesta reproducible de las fuentes Parquet hacia Bronze."""

from __future__ import annotations

from pathlib import Path

import polars as pl

def read_sources(raw_dir: Path) -> dict[str, pl.DataFrame]:
    """Lee las cuatro fuentes Parquet de la capa Bronze."""

    sources = {
        "orders": raw_dir / "orders.parquet",
        "customers": raw_dir / "customers.parquet",
        "order_items": raw_dir / "order_items.parquet",
        "payments": raw_dir / "payments.parquet",
    }

    missing = [
        name
        for name, path in sources.items()
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(
            f"Faltan las siguientes fuentes: {', '.join(missing)}"
        )

    return {
        name: pl.read_parquet(path)
        for name, path in sources.items()
    }