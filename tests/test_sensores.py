from src.agroalerta.reporte import contar_riesgos
from src.agroalerta.sensores import (
    SensorHumedad,
    SensorTemperatura,
    SensorViento,
)

# Primer Test: Temperatura bajo 0 es reisgosa


def test_temperatura_bajo_cero():
    sensor = SensorTemperatura(0, 40)

    assert sensor.es_riesgo(-2)


# Segundo Test: Temperatura templada no es riesgosa


def test_temperatura_templada():
    sensor = SensorTemperatura(0, 40)

    assert not sensor.es_riesgo(15)


# Tercer Test: Un viento normal no es riesgoso


def test_viento_normal():
    sensor = SensorViento(25)
    assert not sensor.es_riesgo(10)


# Cuarto Test: devuelve el conteo esperado para un conjunto pequeño de lecturas escrito a mano en la prueba.
def test_contar_riegos():
    lecturas = {"temperatura": [50], "humedad": [100], "viento": [2]}
    sensores = [SensorTemperatura(0, 40), SensorHumedad(40), SensorViento(10)]
    contea_riesgos = contar_riesgos(sensores, lecturas)

    assert contea_riesgos["temperatura"] == 1
    assert contea_riesgos["humedad"] == 1
    assert contea_riesgos["viento"] == 0
