"""Kernels de convolución que deben definir para la Etapa 6."""

import numpy as np

# Su código aquí: agreguen al menos cinco tuplas (nombre, kernel).
KERNELS: list[tuple[str, np.ndarray]] = [
    # Cada elemento de la lista contiene: (nombre que aparecerá en la aplicación, matriz del kernel)
    # conv_channel aplica la matriz por separado a los canales R, G y B.
    # Identidad: conserva el valor del píxel central por lo que  la imagen resultante es igual a la original
    (
        "identidad",
        np.array(
            [
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0],
            ],
            dtype=float,
        ),
    ),
    # Laplaciano: Compara el píxel central con sus cuatro vecinos directos.
    # En regiones uniformes el resultado es cercano a cero, mientras que en cambios bruscos de intensidad aparecen valores elevados.
    (
        "laplaciano",
        np.array(
            [
                [0, -1, 0],
                [-1, 4, -1],
                [0, -1, 0],
            ],
            dtype=float,
        ),
    ),
    # Enfoque: Refuerza el píxel central y resta sus vecinos. Esto aumenta las
    # diferencias locales y hace que los bordes se vean más definidos.
    (
        "enfoque",
        np.array(
            [
                [-1, -1, -1],
                [-1, 9, -1],
                [-1, -1, -1],
            ],
            dtype=float,
        ),
    ),
    # Desenfoque: reemplaza cada píxel por el promedio de sus nueve vecinos.
    (
        "desenfoque",
        np.ones((5, 5), dtype=float) / 25,
    ),
    # Relieve: Los valores negativos y positivos apuntan en direcciones opuestas.
    # Esto genera zonas claras y oscuras alrededor de los bordes, dando la impresión de un relieve.
    (
        "relieve",
        np.array(
            [
                [-2, -1, 0],
                [-1, 1, 1],
                [0, 1, 2],
            ],
            dtype=float,
        ),
    ),
]
