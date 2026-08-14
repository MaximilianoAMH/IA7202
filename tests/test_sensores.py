from src.agroalerta.sensores import SensorTemperatura, SensorViento

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
