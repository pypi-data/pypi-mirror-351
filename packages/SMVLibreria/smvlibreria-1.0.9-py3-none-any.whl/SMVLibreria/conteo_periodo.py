# conteo_periodo.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def contar_por_anio_trimestre_o_mes(df, periodo="trimestre"):
       
    # Verificar si las columnas necesarias están en el DataFrame
    if 'anio' not in df.columns or ('trimestre' not in df.columns and 'mes' not in df.columns):
        raise ValueError("El DataFrame debe contener las columnas 'anio', 'trimestre' y/o 'mes'")
    
    # Agrupar por 'anio', 'anio y trimestre' o 'anio y mes'
    if periodo == "anio":
        conteo = df.groupby(['anio']).size().reset_index(name="conteo")
    elif periodo == "trimestre":
        conteo = df.groupby(['anio', 'trimestre']).size().reset_index(name="conteo")
    elif periodo == "mes":
        conteo = df.groupby(['anio', 'mes']).size().reset_index(name="conteo")
    else:
        raise ValueError("El parámetro 'periodo' debe ser 'anio', 'trimestre' o 'mes'")

    return conteo

def graficar_conteo_barras (conteo_df, periodo="trimestre"):
    plt.figure(figsize=(12, 6))
    
    if periodo == "anio":
        sns.barplot(data=conteo_df, x="anio", y="conteo", palette="Blues_d")
        plt.title("Conteo de incidentes por año")
    
    elif periodo == "trimestre":
        conteo_df["periodo"] = conteo_df["anio"].astype(str) + " T" + conteo_df["trimestre"].astype(str)
        sns.barplot(data=conteo_df, x="periodo", y="conteo", palette="Greens_d")
        plt.title("Conteo de incidentes por trimestre")
        plt.xticks(rotation=45)
    
    elif periodo == "mes":
        conteo_df["periodo"] = conteo_df["anio"].astype(str) + "-" + conteo_df["mes"].astype(str).str.zfill(2)
        sns.barplot(data=conteo_df, x="periodo", y="conteo", palette="Oranges_d")
        plt.title("Conteo de incidentes por mes")
        plt.xticks(rotation=45)

    plt.xlabel("Periodo")
    plt.ylabel("Número de incidentes")
    plt.tight_layout() #ajusta los elemtos de la grafica para que no se empalmen
    plt.show()


def graficar_conteo_lineas (conteo_df, periodo="trimestre"):
    plt.figure(figsize=(12, 6))
    
    if periodo == "anio":
        sns.lineplot(data=conteo_df, x="anio", y="conteo", marker="o", color="blue")
        plt.title("Conteo de incidentes por año")
    
    elif periodo == "trimestre":
        conteo_df["periodo"] = conteo_df["anio"].astype(str) + " T" + conteo_df["trimestre"].astype(str)
        sns.lineplot(data=conteo_df, x="periodo", y="conteo", marker="o", color="green")
        plt.title("Conteo de incidentes por trimestre")
        plt.xticks(rotation=45)
    
    elif periodo == "mes":
        conteo_df["periodo"] = conteo_df["anio"].astype(str) + "-" + conteo_df["mes"].astype(str).str.zfill(2)
        sns.lineplot(data=conteo_df, x="periodo", y="conteo", marker="o", color="orange")
        plt.title("Conteo de incidentes por mes")
        plt.xticks(rotation=45)

    plt.xlabel("Periodo")
    plt.ylabel("Número de incidentes")
    plt.tight_layout() #ajusta los elemtos de la grafica para que no se empalmen
    plt.grid(True)
    plt.show()
