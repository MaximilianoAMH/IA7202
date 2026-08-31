"""Funciones para declarar y validar el esquema CRU."""

from __future__ import annotations

import pandera.polars as pa
import polars as pl

from src.meteolab.constantes import ESQUEMA_CRU, PERIODOS_VALIDOS

ESQUEMA_TEMPERATURAS = pa.DataFrameSchema(
    {
        "country": pa.Column(str),
        "iso_alpha2": pa.Column(str),
        "iso_alpha3": pa.Column(str),
        "year": pa.Column(
            int,
            checks=pa.Check.in_range(1901, 2025),
        ),
        "period": pa.Column(
            str,
            checks=pa.Check.isin(PERIODOS_VALIDOS),
        ),
        "temperature_c": pa.Column(
            float,
            nullable=True,
        ),
        "parameter": pa.Column(
            str,
            checks=pa.Check.eq("Mean Temperature"),
        ),
        "units": pa.Column(
            str,
            checks=pa.Check.eq("degrees Celsius"),
        ),
        "source_file": pa.Column(str),
    }
)


def comparar_esquema(temperaturas: pl.DataFrame) -> list[str]:
    diferencias = []

    for columna, tipo_esperado in ESQUEMA_CRU.items():
        if columna not in temperaturas.columns:
            diferencias.append(f"Falta la columna '{columna}'")

        elif temperaturas.schema[columna] != tipo_esperado:
            diferencias.append(
                f"Tipo incorrecto en '{columna}': "
                f"{temperaturas.schema[columna]} != {tipo_esperado}"
            )

    return diferencias


def validar_esquema(temperaturas: pl.DataFrame) -> None:
    """Comprueba los nombres y tipos de las columnas."""

    diferencias = comparar_esquema(temperaturas)

    if diferencias:
        raise ValueError("Esquema incorrecto:\n" + "\n".join(diferencias))


def validar_datos(temperaturas: pl.DataFrame) -> pl.DataFrame:
    """Valida tipos, periodos, unidades y valores faltantes."""
    return ESQUEMA_TEMPERATURAS.validate(temperaturas)


def casos_que_fallan(temperaturas: pl.DataFrame) -> pl.DataFrame:
    """Devuelve los incumplimientos sin ocultar sus columnas."""
    try:
        ESQUEMA_TEMPERATURAS.validate(
            temperaturas,
            lazy=True,
        )
    except pa.errors.SchemaErrors as error:
        return error.failure_cases

    return pl.DataFrame()
