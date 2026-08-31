"""Agregaciones sobre las temperaturas medias mensuales."""

from __future__ import annotations

import polars as pl


def resumen_mensual(
    mensuales: pl.DataFrame | pl.LazyFrame,
    paises: list[str] | tuple[str, ...] | None = None,
) -> pl.DataFrame | pl.LazyFrame:
    """Calcula la climatología mensual por país."""

    datos = mensuales

    if paises is not None:
        datos = datos.filter(pl.col("iso_alpha3").is_in(paises))

    return (
        datos.group_by(["iso_alpha3", "country", "month"])
        .agg(
            pl.len().alias("observaciones"),
            pl.col("temperature_c").mean().round(2).alias("temperature_mean"),
        )
        .sort(["iso_alpha3", "month"])
    )


def resumen_anual_desde_mensuales(
    mensuales: pl.DataFrame | pl.LazyFrame,
    paises: list[str] | tuple[str, ...] | None = None,
) -> pl.DataFrame | pl.LazyFrame:
    """Calcula medias anuales usando únicamente filas mensuales."""

    datos = mensuales

    if paises is not None:
        datos = datos.filter(pl.col("iso_alpha3").is_in(paises))

    return (
        datos.group_by(["iso_alpha3", "country", "year"])
        .agg(
            pl.col("period").n_unique().alias("meses_disponibles"),
            pl.col("temperature_c").mean().round(2).alias("temperature_mean"),
        )
        .sort(["iso_alpha3", "year"])
    )


def anomalias_mensuales(
    mensuales: pl.DataFrame | pl.LazyFrame,
    umbral: float = 2.0,
) -> pl.DataFrame | pl.LazyFrame:
    """Marca anomalías usando una ventana por país y mes."""

    media_mes = pl.col("temperature_c").mean().over(["iso_alpha3", "month"])

    desviacion_mes = pl.col("temperature_c").std().over(["iso_alpha3", "month"])

    return mensuales.with_columns(
        media_mes.alias("temperature_mean_month"),
        ((pl.col("temperature_c") - media_mes) / desviacion_mes).alias(
            "standardized_anomaly"
        ),
    ).with_columns(
        (
            pl.col("standardized_anomaly").abs().ge(umbral).fill_null(False)
        ).alias("is_anomaly")
    )
