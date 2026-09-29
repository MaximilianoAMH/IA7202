"""Generación de features desde el scrape de superherodb."""

import polars as pl
from sklearn.preprocessing import MultiLabelBinarizer

from src.heroverse.columns import CATEGORICAS, PUNTAJES


def altura_en_cm(columna: str = "height") -> pl.Expr:
    """Expresión con la altura en centímetros, llamada `altura_cm`.

    Lee la parte métrica de valores como "6'2 • 188 cm" (188,0) o
    "49'2 • 15.0 meters" (1 500,0). Es nula si el valor es "-" o
    "0'0 • 0 cm": nadie mide 0 cm, así que ese cero es la forma en que el
    scrape marca un dato ausente.
    """
    valor = (
        pl.col(columna)
        .str.extract(r"•\s*([\d.,]+)\s*(cm|meters)", 1)
        .str.replace_all(",", "")
        .cast(pl.Float64)
    )

    unidad = pl.col(columna).str.extract(
        r"•\s*([\d.,]+)\s*(cm|meters)",
        2,
    )

    altura = pl.when(unidad == "meters").then(valor * 100).otherwise(valor)

    return (
        pl.when(altura == 0)
        .then(None)
        .otherwise(altura)
        .cast(pl.Float64)
        .alias("altura_cm")
    )


def peso_en_kg(columna: str = "weight") -> pl.Expr:
    """Expresión con el peso en kilogramos, llamada `peso_kg`.

    Lee la parte métrica de valores como "198 lb • 89 kg" (89,0) o
    "6,600 lb • 3.0 tons" (3 000,0; una tonelada son 1 000 kg). La coma de
    "6,600" separa miles. Es nula si el valor es "-".
    """
    valor = (
        pl.col(columna)
        .str.extract(r"•\s*([\d.,]+)\s*(kg|tons)", 1)
        .str.replace_all(",", "")
        .cast(pl.Float64)
    )

    unidad = pl.col(columna).str.extract(
        r"•\s*([\d.,]+)\s*(kg|tons)",
        2,
    )

    return (
        pl.when(unidad == "tons")
        .then(valor * 1000)
        .otherwise(valor)
        .cast(pl.Float64)
        .alias("peso_kg")
    )


def anio_aparicion(columna: str = "first_appearance") -> pl.Expr:
    """Expresión `anio_aparicion` (Int64) con el año de primera aparición.

    Lee "(April, 2008)", "(1979)" o "(november 1986)". Solo acepta años entre
    1900 y 2029, para no leer "(2099)", que es parte de un título.
    """
    patron = "\\((?:[A-Za-z]+,?\\s+)?(19\\d{2}|20[0-2]\\d)\\)"
    return (
        pl.col(columna)
        .str.extract(patron, 1)
        .cast(pl.Int64)
        .alias("anio_aparicion")
    )


def lista_poderes(columna: str = "superpowers") -> pl.Expr:
    """Expresión `poderes`: "['Flight', 'Super Speed']" como lista de strings.

    "[]" produce una lista vacía. Se eliminan etiquetas repetidas
    conservando el orden de primera aparición.
    """
    return (
        pl.col(columna)
        .str.extract_all(r"'[^']+'")
        .list.eval(pl.element().str.strip_chars("'"))
        .list.unique(maintain_order=True)
        .alias("poderes")
    )


def puntajes_con_ficha() -> list[pl.Expr]:
    """Los seis `PUNTAJES` como enteros, nulos si todos valen 0.

    Seis ceros no describen a un personaje sin habilidades: en el catálogo
    coinciden siempre con `overall_score == "-"`, es decir, sin ficha.
    """
    todos_cero = pl.all_horizontal(
        [pl.col(puntaje) == 0 for puntaje in PUNTAJES]
    )

    return [
        (
            pl.when(todos_cero)
            .then(None)
            .otherwise(pl.col(puntaje))
            .cast(pl.Int64)
            .alias(puntaje)
        )
        for puntaje in PUNTAJES
    ]


def construir_features(personajes: pl.DataFrame) -> pl.DataFrame:
    """Devuelve una fila por personaje con sus features tipadas.

    Columnas, en este orden: `name`; las de `CATEGORICAS` sin cambios; los
    seis `PUNTAJES` según `puntajes_con_ficha` (ambas listas están en
    `src/heroverse/columns.py`); `altura_cm`, `peso_kg`,
    `anio_aparicion` y `poderes`; `n_poderes`, el largo de `poderes`; y
    `powers_text` sin cambios. La codificación binaria se ajusta después
    con `ajustar_poderes`, a partir de la lista `poderes`.

    Precondición: `name` no tiene nulos ni duplicados. Si los tiene, levanta
    `ValueError` con un mensaje que menciona `name`, porque cada fila debe
    representar a un solo personaje.
    """
    if personajes["name"].null_count() > 0:
        raise ValueError("La columna name contiene valores nulos.")

    if personajes["name"].n_unique() != personajes.height:
        raise ValueError("La columna name contiene valores duplicados.")

    features = personajes.with_columns(
        *puntajes_con_ficha(),
        altura_en_cm(),
        peso_en_kg(),
        anio_aparicion(),
        lista_poderes(),
    )

    features = features.with_columns(
        pl.col("poderes").list.len().alias("n_poderes")
    )

    return features.select(
        "name",
        *CATEGORICAS,
        *PUNTAJES,
        "altura_cm",
        "peso_kg",
        "anio_aparicion",
        "poderes",
        "n_poderes",
        "powers_text",
    )


def ajustar_poderes(
    features: pl.DataFrame,
) -> tuple[MultiLabelBinarizer, pl.DataFrame]:
    """Aprende los poderes del catálogo y devuelve encoder y tabla codificada.

    `features` tiene una columna `poderes` con listas de strings sin nulos.
    Se conservan todas las columnas, el número y el orden de las filas.
    Se agrega una columna Int8 `poder_<etiqueta>` por cada etiqueta aprendida,
    en el orden de `classes_`, sin modificar espacios ni mayúsculas.
    Una lista vacía produce una fila de ceros en el bloque de poderes.
    """
    binarizador = MultiLabelBinarizer()

    matriz = binarizador.fit_transform(features["poderes"].to_list())

    binarias = [f"poder_{etiqueta}" for etiqueta in binarizador.classes_]

    bloque_poderes = pl.DataFrame(
        matriz,
        schema=binarias,
        orient="row",
    ).cast(pl.Int8)

    tabla = features.hstack(bloque_poderes)

    return binarizador, tabla


def transformar_poderes(
    features: pl.DataFrame, binarizador: MultiLabelBinarizer
) -> pl.DataFrame:
    """Codifica poderes con un encoder ajustado, sin aprender nuevas etiquetas.

    Conserva filas y columnas de `features`; agrega el mismo bloque Int8 y
    en el mismo orden que `ajustar_poderes`. Una lista vacía da ceros.
    Un poder fuera de `classes_` no tiene columna: se ignora, y
    `MultiLabelBinarizer` emite un `UserWarning` que lo nombra. No se
    reajusta, porque eso cambiaría las columnas del catálogo.
    """
    matriz = binarizador.transform(features["poderes"].to_list())

    binarias = [f"poder_{etiqueta}" for etiqueta in binarizador.classes_]

    bloque_poderes = pl.DataFrame(
        matriz,
        schema=binarias,
        orient="row",
    ).cast(pl.Int8)

    return features.hstack(bloque_poderes)
