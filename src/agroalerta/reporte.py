def contar_riesgos(sensores, lecturas):
    conteo = {}

    for sensor in sensores:
        riesgos = 0

        for valor in lecturas[sensor.nombre]:
            if sensor.es_riesgo(valor):
                riesgos += 1

        conteo[sensor.nombre] = riesgos

    return conteo
