from abc import ABC, abstractmethod


class Sensor(ABC):
    def __init__(self, nombre, unidad):
        self._nombre = nombre
        self._unidad = unidad

    @abstractmethod
    def es_riesgo(self, valor: int) -> bool:
        return valor


class SensorTemperatura(Sensor):
    def __init__(self, maximo, minimo):
        super().__init__("temperatura", "°C")
        self._maximo = maximo
        self._minimo = minimo

    def es_riesgo(self, valor: int) -> bool:
        return valor < self.minimo or valor > self.maximo

    @property
    def rango_seguro(self):
        return f"entre {self._minimo} y {self._maximo} {self.unidad}"


class SensorViento(Sensor):
    def __init__(self, maximo):
        super().__init__("viento", "km/h")
        self._maximo = maximo

    def es_riesgo(self, valor: int) -> bool:
        return valor > self.maximo

    @property
    def rango_seguro(self):
        return f"bajo {self._maximo} {self.unidad}"


class SensorHumedad(Sensor):
    def __init__(self, maximo):
        super().__init__("humedad", "%")
        self._maximo = maximo

    def es_riesgo(self, valor: int) -> bool:
        return valor > self.maximo

    @property
    def rango_seguro(self):
        return f"bajo {self._maximo} {self.unidad}"
