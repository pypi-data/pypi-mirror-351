# carga_datos.py

import pandas as pd

def cargar_csv_desde_url(url: str) -> pd.DataFrame | None:
    
    try:
        df = pd.read_csv(url)
        print("✅ Archivo cargado correctamente.")
        return df
    except Exception as e:
        print(f"❌ Error al cargar el archivo desde la URL: {e}")
        return None

def guardar_csv_local(df: pd.DataFrame, nombre_archivo: str) -> None:

    try:
        df.to_csv(nombre_archivo, index=False)
        print(f"✅ Archivo guardado como '{nombre_archivo}'.")
    except Exception as e:
        print(f"❌ Error al guardar el archivo: {e}")

# Este bloque solo se ejecutará si cargas este script directamente
if __name__ == "__main__":
    url = "https://seguridadvial.semovi.cdmx.gob.mx/wp-content/themes/semovi-seguridad-vial/data/dataset.csv"
    df = cargar_csv_desde_url(url)
    if df is not None:
        guardar_csv_local(df, "dataset_guardado.csv")
