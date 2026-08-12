def contar_riesgos(sensores, lecturas):
    i = 0
    for sensor in sensores:
        if sensor.es_riesgo(lecturas[str(sensor.nombre)]):
            i += 1
    return i, 0
