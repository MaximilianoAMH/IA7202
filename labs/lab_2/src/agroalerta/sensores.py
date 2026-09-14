from abc import ABC, abstractmethod


class Sensor(ABC):
    def __init__(self, nombre, unidad):
        self._nombre = nombre
        self._unidad = unidad

    @property
    def nombre(self):
        return self._nombre

    @property
    def unidad(self):
        return self._unidad

    @abstractmethod
    def es_riesgo(self, valor: float) -> bool:
        pass


class SensorTemperatura(Sensor):
    def __init__(self, minimo, maximo):
        super().__init__("temperatura", "°C")
        self._minimo = minimo
        self._maximo = maximo

    def es_riesgo(self, valor: float) -> bool:
        return valor < self._minimo or valor > self._maximo

    @property
    def rango_seguro(self):
        return f"entre {self._minimo} y {self._maximo} {self.unidad}"


class SensorViento(Sensor):
    def __init__(self, maximo):
        super().__init__("viento", "km/h")
        self._maximo = maximo

    def es_riesgo(self, valor: float) -> bool:
        return valor > self._maximo

    @property
    def rango_seguro(self):
        return f"bajo {self._maximo} {self.unidad}"


class SensorHumedad(Sensor):
    def __init__(self, maximo):
        super().__init__("humedad", "%")
        self._maximo = maximo

    def es_riesgo(self, valor: float) -> bool:
        return valor > self._maximo

    @property
    def rango_seguro(self):
        return f"bajo {self._maximo} {self.unidad}"
