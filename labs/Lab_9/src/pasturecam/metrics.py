"""Métricas específicas del dominio para biomasa de pastura."""

import numpy as np

from src.pasturecam.contratos import PESOS_OBJETIVOS


def r2_log(y_real: np.ndarray, y_pred: np.ndarray) -> float:
    """Calcula R² sobre log(1 + y), para que errores relativos pesen igual.

    Valores negativos en `y_pred` se truncan a cero antes de aplicar el
    logaritmo, porque la biomasa no puede ser negativa.
    """
    y_pred_truncado = np.maximum(y_pred, 0.0)
    y_log = np.log1p(y_real)
    pred_log = np.log1p(y_pred_truncado)

    ss_res = np.sum((y_log - pred_log) ** 2)
    ss_tot = np.sum((y_log - np.mean(y_log)) ** 2)

    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0

    return float(1.0 - ss_res / ss_tot)


def gramos_a_kg_ha(gramos: float | np.ndarray) -> float | np.ndarray:
    """Convierte biomasa en gramos por cuadrante a kg/ha.

    El cuadrante mide 0.70 m por 0.30 m (0.21 m²). Una hectárea tiene 10 000 m²,
    y un kilogramo tiene 1 000 gramos:

        kg/ha = gramos * (10 000 / 0.21) / 1 000
    """
    factor = (10_000 / (0.70 * 0.30)) / 1_000
    return gramos * factor


def r2_log_ponderado(
    y_real: dict[str, np.ndarray] | np.ndarray,
    y_pred: dict[str, np.ndarray] | np.ndarray,
    pesos: dict[str, float] | None = None,
) -> float:
    """Calcula el R²_log ponderado sobre los objetivos canónicos.

    Soporta `y_real` e `y_pred` como diccionarios {nombre_objetivo: valores}
    y como matrices NumPy 2D de forma (n_muestras, 5).
    """
    if pesos is None:
        pesos = PESOS_OBJETIVOS

    # Caso 1: Diccionarios {nombre_objetivo: array}
    if isinstance(y_real, dict):
        puntaje_total = 0.0
        for objetivo, peso in pesos.items():
            puntaje_col = r2_log(y_real[objetivo], y_pred[objetivo])
            puntaje_total += peso * puntaje_col
        return float(puntaje_total)

    # Caso 2: Arrays 2D
    columnas_orden = [
        "Dry_Green_g",
        "Dry_Dead_g",
        "Dry_Clover_g",
        "Dry_Weed_g",
        "Dry_Total_g",
    ]
    puntaje_total = 0.0
    for i, col in enumerate(columnas_orden):
        puntaje_col = r2_log(y_real[:, i], y_pred[:, i])
        puntaje_total += pesos[col] * puntaje_col

    return float(puntaje_total)
