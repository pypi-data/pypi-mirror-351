# tasa_crecimiento.py

import pandas as pd
import matplotlib.pyplot as plt


def tasa_crecimiento(df, periodo="anio", desde=None, hasta=None):
    
     # Validación de entrada
    if periodo not in ["anio", "trimestre", "mes"]:
        raise ValueError("El parámetro 'periodo' debe ser 'anio', 'trimestre' o 'mes'")
    if desde is None or hasta is None:
        raise ValueError("Debes especificar los parámetros 'desde' y 'hasta'")

     # Agrupación según el periodo
    if periodo == "anio":
        grupo = df.groupby("anio").size()
        valor_desde = grupo.get(desde[0], 0)
        valor_hasta = grupo.get(hasta[0], 0)

    elif periodo == "trimestre":
        grupo = df.groupby(["anio", "trimestre"]).size()
        valor_desde = grupo.get((desde[0], desde[1]), 0)
        valor_hasta = grupo.get((hasta[0], hasta[1]), 0)

    elif periodo == "mes":
        grupo = df.groupby(["anio", "mes"]).size()
        valor_desde = grupo.get((desde[0], desde[1]), 0)
        valor_hasta = grupo.get((hasta[0], hasta[1]), 0)
    # Calcular tasa de crecimiento:
    if valor_desde == 0:
        raise ZeroDivisionError(f"No hay datos en el periodo desde {desde} (división por cero)")

    tasa = ((valor_hasta - valor_desde) / valor_desde) * 100
    return tasa

def graficar_tasa (valor_desde, valor_hasta, desde, hasta, tasa, periodo="anio"):
    etiquetas = [f"{desde}", f"{hasta}"]
    valores = [valor_desde, valor_hasta]

    plt.figure(figsize=(8, 5))
    plt.plot(etiquetas, valores, marker='o', color='blue', linewidth=2)
    plt.title(f"Tasa de crecimiento entre {desde} y {hasta}\nCrecimiento: {tasa:.2f}%")
    plt.xlabel(f"Periodo ({periodo})")
    plt.ylabel("Número de incidentes")
    plt.grid(True)
    plt.tight_layout()
    plt.show()