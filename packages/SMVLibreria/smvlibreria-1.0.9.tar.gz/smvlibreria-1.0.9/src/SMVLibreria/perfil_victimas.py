#perfil_victimas.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def perfil_de_victimas(df, periodo="anio", victima="peaton"):
    # Validación de entrada
    if periodo not in ["anio", "trimestre", "mes"]:
        raise ValueError("El parámetro 'periodo' debe ser 'anio', 'trimestre' o 'mes'")
    if victima not in ["peaton", "ciclista", "pasajero", "motociclista", "conductor"]:
        raise ValueError("El parámetro 'victima' debe ser 'peaton', 'ciclista', 'pasajero', 'motociclista' o 'conductor'")
        
    lesionados_col = f"{victima}_lesionado"
    fallecidos_col = f"{victima}_fallecido"

    #validar columnas
    if periodo not in df.columns:
        raise ValueError(f"La columna '{periodo}' no existe en el DataFrame")
    if lesionados_col not in df.columns or fallecidos_col not in df.columns:
        raise ValueError(f"Las columnas '{lesionados_col}' y/o '{fallecidos_col}' no existen en el DataFrame")


    # Agrupamos por el periodo y sumamos lesionados y fallecidos
    grupo = df.groupby(periodo).agg(
        lesionados=(lesionados_col, 'sum'),
        fallecidos=(fallecidos_col, 'sum')
    )

    # Convertimos a diccionario con formato {periodo: {'lesionados': X, 'fallecidos': Y}}
    perfil = grupo.to_dict(orient='index')

    # Convertir valores a enteros
    for key, value in perfil.items():
        perfil[key]['lesionados'] = int(value['lesionados'])
        perfil[key]['fallecidos'] = int(value['fallecidos'])

    return perfil

def graficar_perfil_barras (perfil_dict, periodo="anio", victima="peaton"):
    # Convertir e dic a  DF
    df = pd.DataFrame.from_dict(perfil_dict, orient='index').reset_index()
    df.rename(columns={'index': periodo}, inplace=True)

    # Convertir a string si el periodo es mes o trimestre (por legibilidad)
    if periodo in ["mes", "trimestre"]:
        df[periodo] = df[periodo].astype(str)

    # Reorganizar a formato largo para seaborn
    df_largo = df.melt(id_vars=[periodo], value_vars=['lesionados', 'fallecidos'], 
                       var_name='tipo', value_name='cantidad')

    ### gráfica de barras
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_largo, x=periodo, y='cantidad', hue='tipo', palette='Set2')

    plt.title(f"Lesionados y fallecidos ({victima}) por {periodo}")
    plt.xlabel(periodo.capitalize())
    plt.ylabel("Número de víctimas")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend(title="Tipo de víctima")
    plt.show()

def graficar_perfil_lineas(perfil_dict, periodo="anio", victima="peaton"):
    # Convertir el diccionario en DataFrame
    df = pd.DataFrame.from_dict(perfil_dict, orient='index').reset_index()
    df.rename(columns={'index': periodo}, inplace=True)

    # Convertir a string si el periodo es mes o trimestre (por legibilidad)
    if periodo in ["mes", "trimestre"]:
        df[periodo] = df[periodo].astype(str)

    # Reorganizar a formato largo para seaborn
    df_largo = df.melt(
        id_vars=[periodo],
        value_vars=['lesionados', 'fallecidos'],
        var_name='tipo',
        value_name='cantidad'
    )

    # Graficar líneas
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_largo, x=periodo, y='cantidad', hue='tipo', marker="o", palette='Set1'
    )

    plt.title(f"Lesionados y fallecidos ({victima}) por {periodo}")
    plt.xlabel(periodo.capitalize())
    plt.ylabel("Número de víctimas")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend(title="Tipo de víctima")
    plt.show()
