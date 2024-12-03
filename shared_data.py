# Diccionario con las estaciones y distritos de Madrid
ESTACIONES = {
    28001: "Salamanca",
    28002: "Retiro",
    28003: "Chamberí",
    28004: "Centro",
    28005: "Latina",
    28006: "Chamartín",
    28007: "Arganzuela",
    28008: "Moncloa-Aravaca",
    28009: "Salamanca",
    28010: "Chamberí",
    28011: "Carabanchel",
    28012: "Centro",
    28013: "Centro",
    28014: "Retiro",
    28015: "Chamberí",
    28016: "Chamartín",
    28017: "Ciudad Lineal",
    28019: "Carabanchel",
    28020: "Tetuán",
    28026: "Usera",
    28027: "Ciudad Lineal",
    28028: "Salamanca",
    28030: "Moratalaz",
    28039: "Tetuán",
    28045: "Arganzuela",
    28046: "Chamartín",
    28000: "Madrid Centro",
    28038: "Puente de Vallecas",
    28040: "Moncloa-Aravaca",
    28041: "Usera",
    28053: "Puente de Vallecas",
    28029: "Fuencarral-El Pardo",
    28036: "Chamartín",
    28035: "Fuencarral-El Pardo",
    28033: "Hortaleza",
    28024: "Latina",
    28047: "Latina",
    28022: "San Blas-Canillejas",
    28043: "Hortaleza",
    28050: "Hortaleza",
    28042: "Barajas",
    28018: "Puente de Vallecas",
    28037: "San Blas-Canillejas",
    28025: "Carabanchel",
    28034: "Fuencarral-El Pardo",
    28031: "Villa de Vallecas",
    28032: "Vicálvaro",
    28044: "Latina",
    28055: "San Blas-Canillejas",
    28049: "Fuencarral-El Pardo",
    28054: "Vicálvaro",
    28052: "Vicálvaro",
}


import pandas as pd
import os

# Ruta al archivo de datos
EXCEL_FILE = "./data/DATA_MODELO.xlsx"
PARQUET_FILE = "./data/DATA_MODELO.parquet"

def cargar_datos():
    """Carga los datos desde un archivo Parquet o convierte desde Excel si es necesario."""
    if not os.path.exists(PARQUET_FILE):
        # Convertir Excel a Parquet si no existe el archivo Parquet
        if not os.path.exists(EXCEL_FILE):
            raise FileNotFoundError(f"El archivo {EXCEL_FILE} no existe.")
        df = pd.read_excel(EXCEL_FILE)
        df.to_parquet(PARQUET_FILE, engine="pyarrow")
        #print(f"Archivo Parquet generado: {PARQUET_FILE}")

    # Cargar datos desde Parquet
    return pd.read_parquet(PARQUET_FILE)

# Cargar los datos globalmente al inicio
DATA = cargar_datos()

# Diccionario con datos prefiltrados por estación para acceso rápido
DATA_BY_STATION = {
    cp: df for cp, df in DATA.groupby("zipCode_unlock")
}
