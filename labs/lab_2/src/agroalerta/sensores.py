class Sensor:
    def __init__(self, nombre, unidad):
        self.nombre = nombre
        self.unidad = unidad

    def es_riesgo(self, valor: int):
        return False


class SensorTemperatura(Sensor):
    def __init__(self, maximo, minimo):
        super().__init__("temperatura", "°C")
        self.maximo = maximo
        self.minimo = minimo


class SensorViento(Sensor):
    def __init__(self, maximo):
        super().__init__("viento", "km/h")
        self.maximo = maximo


class SensorHumedad(Sensor):
    def __init__(self, maximo):
        super().__init__("humedad", "%")
        self.maximo = maximo

    def es_riesgo(self, valor: int):
        if valor > self.maximo:
            return True
        return False
