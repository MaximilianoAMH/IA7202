"""Clase ``Imagen``: contenedor de imágenes sobre el que se opera con NumPy."""

from __future__ import annotations

import numpy as np


class Imagen:
    """Representa una imagen RGB almacenada como un arreglo de NumPy.
    Cada imagen debe tener la forma: (alto, ancho, 3)
    El último eje contiene los canales rojo, verde y azul.
    """

    def __init__(self, img: np.ndarray) -> None:
        # Verifica si es un arrgelo de NumPy
        if not isinstance(img, np.ndarray):
            raise TypeError(
                "Debes entregar un arreglo de numpy como argumento del constructor de Imagen"
            )
        # Verifica que arreglo tenga 3 dimensiones (alto, ancho,canales)
        if img.ndim != 3:
            raise ValueError("La imagen debe tener 3 dimensiones")
        # Verifica que hay 3 canales RGB
        if img.shape[-1] != 3:
            raise ValueError("La imagen debe tener 3 canales")
        # Guardar imagen
        self.imagen = img

    def __add__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Suma un valor, arreglo u otra imagen a la imagen origianl
        if isinstance(other, Imagen):
            if self.imagen.shape != other.imagen.shape:
                raise ValueError(
                    "Las dimensiones de la imagen a operar "
                    "(alto x ancho x canales) no calzan con las de la imagen "
                    "original (alto x ancho x canales)"
                )

            operando = other.imagen
        else:
            operando = other

        resultado = (self.imagen + operando).astype(int)

        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0

        return Imagen(np.copy(resultado))

    def __radd__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        return self.__add__(other)

    # Propiedad conmutativa de la suma

    def __sub__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Resta un valor, arreglo o imagen a otra imagen
        if isinstance(other, Imagen):
            if self.imagen.shape != other.imagen.shape:
                raise ValueError(
                    "Las dimensiones de la imagen a operar "
                    "(alto x ancho x canales) no calzan con las de la imagen "
                    "original (alto x ancho x canales)"
                )

            operando = other.imagen
        else:
            operando = other

        resultado = (self.imagen - operando).astype(int)

        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0

        return Imagen(np.copy(resultado))

    def __rsub__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Resta una imagen a un valor, arreglo o imagen, la resta no es conmutativa
        if isinstance(other, Imagen):
            if self.imagen.shape != other.imagen.shape:
                raise ValueError(
                    "Las dimensiones de la imagen a operar "
                    "(alto x ancho x canales) no calzan con las de la imagen "
                    "original (alto x ancho x canales)"
                )

            operando = other.imagen
        else:
            operando = other

        resultado = (operando - self.imagen).astype(int)

        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0

        return Imagen(np.copy(resultado))

    def __mul__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Multiplica la imagen por un valor, arreglo u otra Imagen
        if isinstance(other, Imagen):
            if self.imagen.shape != other.imagen.shape:
                raise ValueError(
                    "Las dimensiones de la imagen a operar "
                    "(alto x ancho x canales) no calzan con las de la imagen "
                    "original (alto x ancho x canales)"
                )

            operando = other.imagen
        else:
            operando = other

        resultado = (self.imagen * operando).astype(int)

        resultado[resultado > 255] = 255
        resultado[resultado < 0] = 0

        return Imagen(np.copy(resultado))

    def __rmul__(self, other: int | float | np.ndarray | Imagen) -> Imagen:
        # Multiplica un valor, arreglo u otra Imagen por la imagen original, propiedad conmutativa
        return self.__mul__(other)
