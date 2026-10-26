"""Evaluación de las predicciones por franja de programación."""

from collections.abc import Sequence

from .contratos import FRANJAS

def a_franja(estado: str) -> str:
    """Devuelve la franja de programación en que suena un estado de ánimo.

    Radio fcFM programa `happy` por la mañana, `angry` en la hora del taco
    y `sad` o `relaxed` de noche; el nombre de cada franja está en `FRANJAS`.
    Si `estado` no es uno de los cuatro estados de MoodyLyrics4Q, levanta un
    `ValueError` que nombra el estado desconocido.
    """
    if estado not in FRANJAS:
        raise ValueError(f"Estado de ánimo desconocido: {estado!r}")
    return FRANJAS[estado]


def acierto_por_franja(y_real: Sequence[str], y_pred: Sequence[str]) -> float:
    """Calcula la fracción de canciones cuya franja predicha es la correcta.

    Compara la franja del estado real con la del estado predicho, no los
    estados: confundir `sad` con `relaxed` cuenta como acierto, porque las dos
    suenan de noche. Si `y_real` e `y_pred` tienen largo distinto, levanta un
    `ValueError`. El resultado va entre 0 y 1 y, como fusionar estados solo
    elimina errores, nunca es menor que el accuracy de los cuatro estados.
    """
    if len(y_real) != len(y_pred):
        raise ValueError("y_real e y_pred deben tener el mismo largo.")
    if len(y_real) == 0:
        raise ValueError("Se necesita al menos una canción para evaluar.")

    aciertos = sum(
        a_franja(real) == a_franja(predicho)
        for real, predicho in zip(y_real, y_pred)
    )
    return aciertos / len(y_real)
