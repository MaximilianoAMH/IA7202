"""Operaciones de procesamiento de imágenes para completar."""

from __future__ import annotations

import numpy as np
from scipy.signal import convolve2d

from .imagen import Imagen


class LibImagen:
    """Filtros y transformaciones que reciben y retornan ``Imagen``."""

    # Agrupa filtros y transformaciones para imágenes RGB.
    # #Todos los métodos reciben una Imagen y retornan una nueva Imagen.
    # La imagen recibida como entrada no debe modificarse.

    def conv_channel(self, img_in: Imagen, kernel: np.ndarray) -> Imagen:
        "La función de convolución define un kernel, el cual se desplaza a lo largo y ancho de la"
        "imagen, tomando los píxeles que se encuentran bajo este y realizando una combinación"
        "ponderada sobre ellos. La convolución se aplica de manera independiente a cada canal de color."
        "El Kernel que se ocupa determina cual es la transformación que se busca aplicar a la imagen"
        "En particular se aplican los kernels, identidad laplaciano, enfoque, desenfoque y relieve"
        img = img_in.imagen
        img_out = []
        for i in range(img.shape[-1]):
            img_channel = convolve2d(
                img[:, :, i], kernel, mode="same", boundary="symm"
            )
            img_out.append(img_channel)
        new_image = np.stack(img_out, axis=2)
        new_image[new_image > 255], new_image[new_image < 0] = 255, 0
        return Imagen(new_image.astype(int))

    def to_negative(self, img_in: Imagen) -> Imagen:
        # Calcula el negativo de una imagen RGB.
        # Cada intensidad se reemplaza por su valor complementario respecto de 255
        # Por ejemplo, 0 se transforma en 255 y 200 en 55
        resultado = (255 - img_in.imagen).astype(int)
        return Imagen(np.copy(resultado))

    def to_gray(self, img_in: Imagen) -> Imagen:
        # Convierte una imagen RGB a escala de grises
        R = img_in.imagen[:, :, 0]
        G = img_in.imagen[:, :, 1]
        B = img_in.imagen[:, :, 2]

        gris = 0.299 * R + 0.587 * G + 0.114 * B

        resultado = np.stack(
            [gris, gris, gris],
            axis=2,
        ).astype(int)

        return Imagen(np.copy(resultado))

    def get_channel(self, img_in: Imagen, channel: str) -> Imagen:
        # Conserva un canal de color y deja los otros dos en cero
        resultado = np.zeros_like(img_in.imagen)

        if channel == "r":
            resultado[:, :, 0] = img_in.imagen[:, :, 0]

        elif channel == "g":
            resultado[:, :, 1] = img_in.imagen[:, :, 1]

        elif channel == "b":
            resultado[:, :, 2] = img_in.imagen[:, :, 2]

        else:
            raise ValueError(
                f"Canal '{channel}' no válido. Valores posibles: 'r', 'g' o 'b'."
            )

        resultado = resultado.astype(int)

        return Imagen(np.copy(resultado))

    def flip(self, img_in: Imagen, axis: str) -> Imagen:
        # Invierte horizontal o verticalmente una imagen

        if axis == "h":
            # Se mantienen todas las filas y canales, pero se recorren las
            # columnas con paso -1.
            resultado = img_in.imagen[:, ::-1, :]

        elif axis == "v":
            # Se recorren las filas con paso -1, manteniendo columnas y
            # canales en su orden original.
            resultado = img_in.imagen[::-1, :, :]

        else:
            raise ValueError(
                f"Eje '{axis}' no válido. "
                "Valores posibles: 'h' (horizontal) o 'v' (vertical)."
            )

        resultado = resultado.astype(int)

        return Imagen(np.copy(resultado))

    def set_saturation(self, img_in: Imagen, C: float) -> Imagen:
        # Modifica la saturación de una imagen.
        # C = 0 produce una imagen gris.
        # C = 1 conserva aproximadamente la saturación original.
        # C > 1 aumenta la separación entre cada color y el gris.
        # C < 1 reduce esa separación.

        # Se convierte primero a float
        img = img_in.imagen.astype(float)

        # Se obtiene la versión gris como arreglo float
        gris = self.to_gray(img_in).imagen

        resultado = gris + C * (img - gris)

        #  La especificación exige que las intensidades finales sean int
        resultado = resultado.astype(int)
        # Se ajustan niveles de Saturación
        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0

        return Imagen(np.copy(resultado))

    def set_contrast(self, img_in: Imagen, C: float) -> Imagen:
        # Modifica el contraste alrededor de la intensidad

        # Se transforma a float
        img = img_in.imagen.astype(float)

        F = 259 * (C + 255) / (255 * (259 - C))

        resultado = F * (img - 128) + 128

        resultado = resultado.astype(int)

        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0

        return Imagen(np.copy(resultado))
