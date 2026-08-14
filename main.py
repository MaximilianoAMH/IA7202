import argparse
from pathlib import Path

from src.agroalerta.datos import cargar_lecturas
from src.agroalerta.errores import LecturaInvalidaError
from src.agroalerta.reporte import contar_riesgos
from src.agroalerta.sensores import (
    SensorHumedad,
    SensorTemperatura,
    SensorViento,
)


def main():
    parser = argparse.ArgumentParser(description="AgroAlerta")
    parser.add_argument("--fecha", default="2026-06-15")
    args = parser.parse_args()

    sensores = [
        SensorTemperatura(0, 40),
        SensorViento(25),
        SensorHumedad(85),
    ]

    ruta = Path("data/lecturas.csv")

    lecturas = cargar_lecturas(ruta, args.fecha)

    lecturas_validas = {}

    for sensor in sensores:
        lecturas_validas[sensor.nombre] = []

        for valor in lecturas.get(sensor.nombre, []):
            try:
                if sensor.nombre == "temperatura" and (
                    valor < -50 or valor > 50
                ):
                    raise LecturaInvalidaError(
                        f"Temperatura inválida: {valor} °C"
                    )
                if sensor.nombre == "viento" and valor > 200:
                    raise LecturaInvalidaError(f"Viento inválido: {valor} km/h")

                if sensor.nombre == "humedad" and valor > 100:
                    raise LecturaInvalidaError(f"Humedad inválida: {valor} %")

                lecturas_validas[sensor.nombre].append(valor)

            except LecturaInvalidaError:
                continue

    conteo = contar_riesgos(sensores, lecturas_validas)

    print(f"Estación Parcela Norte — {args.fecha}")

    for sensor in sensores:
        print(f"{sensor.nombre}: {conteo[sensor.nombre]} lecturas en riesgo")

    total = sum(conteo.values())

    print(f"Total: {total} situaciones de riesgo")


if __name__ == "__main__":
    main()
