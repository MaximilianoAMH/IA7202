"""Predicción del ánimo de canciones nuevas."""

from collections.abc import Sequence


import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from .data import limpiar_letra
from .evaluation import a_franja

def predecir_animo(modelo: Pipeline, letras: Sequence[str]) -> pd.DataFrame:
    """Predice el ánimo, la franja y la confianza de cada letra.

    `modelo` es un `Pipeline` ya ajustado que entrega `predict_proba`. Cada
    letra se limpia con `limpiar_letra`, igual que las del entrenamiento. El
    resultado tiene una fila por letra, en el mismo orden, con tres columnas:
    `animo` (la clase de mayor probabilidad), `franja` (la franja de
    programación de ese ánimo, según `a_franja`) y `confianza` (la
    probabilidad de la clase elegida, entre 0 y 1). La confianza no está
    calibrada: no es la probabilidad real de acertar.
    """
    if len(letras) == 0:
        return pd.DataFrame(
            {
                "animo": pd.Series(dtype="object"),
                "franja": pd.Series(dtype="object"),
                "confianza": pd.Series(dtype="float64"),
            }
        )

    letras_limpias = [limpiar_letra(letra) for letra in letras]
    probabilidades = modelo.predict_proba(letras_limpias)
    indices = probabilidades.argmax(axis=1)
    animos = modelo.classes_[indices]

    return pd.DataFrame(
        {
            "animo": animos,
            "franja": [a_franja(animo) for animo in animos],
            "confianza": probabilidades[np.arange(len(letras)), indices],
        }
    )