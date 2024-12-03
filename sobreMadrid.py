import pandas as pd
from dash import html, dcc
import dash
from components import header  # Importa el header desde components.py
import datetime  # Importa el módulo datetime para obtener la fecha actual

# Función para cargar y procesar el archivo CSV
def cargar_actividades():
    try:
        df = pd.read_csv("DATA/actividades.csv", encoding="ISO-8859-1", delimiter=";")
        df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors='coerce')
        df["HORA"] = df["HORA"].apply(lambda x: x.split(":")[0] + ":" + x.split(":")[1])
        return df
    except pd.errors.ParserError as e:
        print(f"Error al leer el CSV: {e}")
        return pd.DataFrame()

# Función para generar la página
def sobre_madrid_page():
    df_actividades = cargar_actividades()

    if df_actividades.empty:
        return html.Div([html.H1("No se encontraron actividades")])

    # Obtener la fecha actual
    today = datetime.date.today()

    # Crear el componente de filtro por fecha con la fecha de hoy como valor predeterminado
    date_picker = dcc.DatePickerSingle(
        id='date-picker',
        min_date_allowed=df_actividades["FECHA"].min().date(),
        max_date_allowed=df_actividades["FECHA"].max().date(),
        initial_visible_month=df_actividades["FECHA"].max().date(),
        date=today,  # Establecer la fecha de hoy como valor predeterminado
        display_format='DD/MM/YYYY'
    )

    # Filtro para actividades gratis (usamos un checklist con una opción de "Gratis")
    gratis_checklist = dcc.Checklist(
        id='gratis-checklist',
        options=[
            {'label': 'Mostrar solo actividades gratis', 'value': 'gratis'}
        ],
        value=[],  # Si está vacío, no filtramos por gratis
        inline=True
    )

    # Fila de filtros (fecha y gratis)
    filtros = html.Div([
        html.Div([
            html.Label("Fecha:", style={"fontSize": "1.1rem", "marginRight": "10px"}),  # Etiqueta para la fecha
            date_picker
        ], style={"display": "inline-block", "marginRight": "20px"}),  # Estilo para los filtros

        html.Div([gratis_checklist], style={"display": "inline-block"})
    ], style={"marginTop": "20px", "textAlign": "center"})

    actividades = create_activities(df_actividades, today, [])

    return html.Div([
        header(),
        filtros,  # Filtros organizados en una fila
        html.Div(id='activities-container', children=actividades)
    ])

def create_activities(df_actividades, fecha_seleccionada, filtros_gratis):
    # Filtrar por fecha seleccionada
    df_filtrado = df_actividades[df_actividades["FECHA"].dt.date == fecha_seleccionada]

    # Si se seleccionó el filtro "gratis", solo mostrar actividades gratuitas
    if 'gratis' in filtros_gratis:
        df_filtrado = df_filtrado[df_filtrado['GRATUITO'] == 1]  # Filtramos por la columna 'GRATUITO'

    # Convertir la columna 'HORA' a tipo datetime para ordenar
    df_filtrado['HORA'] = pd.to_datetime(df_filtrado['HORA'], format='%H:%M').dt.time

    # Ordenar las actividades por hora (de más pronto a más tarde)
    df_filtrado = df_filtrado.sort_values(by='HORA', ascending=True)

    actividades = []
    for i in range(0, len(df_filtrado), 5):
        fila = df_filtrado.iloc[i:i+5]
        actividad_fila = []

        for _, row in fila.iterrows():
            # Formatear la fecha en el formato "DD-MM-YYYY"
            fecha_formateada = row["FECHA"].strftime('%d-%m-%Y')

            # Formatear la hora para mostrar solo HH:mm
            hora_formateada = row["HORA"].strftime('%H:%M')  # Solo muestra las horas y minutos

            actividad_fila.append(html.Div(
                children=[
                    html.H3(row["TITULO"], style={"color": "#0044cc", "fontSize": "1.3rem", "textAlign": "center"}),
                    html.P(f"Fecha: {fecha_formateada} | Hora: {hora_formateada}", style={"fontSize": "1.1rem", "textAlign": "center"}),
                    html.P(f"Instalación: {row['NOMBRE-INSTALACION']} | Código Postal: {row['CP']}", style={"fontSize": "1.1rem", "textAlign": "center"}),
                    html.P(f"Gratis: {'Sí' if row['GRATUITO'] == 1 else 'No'}", style={"fontSize": "1.1rem", "textAlign": "center"}),
                    html.A("Ver más", href=row["CONTENT-URL"], target="_blank", style={"color": "#0044cc", "textDecoration": "none", "fontSize": "1.2rem", "textAlign": "center", "display": "block"}),
                    html.Br(),
                ],
                style={
                    "border": "1px solid #ccc",
                    "padding": "10px",
                    "margin": "10px",
                    "borderRadius": "5px",
                    "backgroundColor": "#f9f9f9",
                    "textAlign": "center",
                    "flex": "1",  # Esto asegura que todos los elementos tengan el mismo tamaño
                    "maxWidth": "300px",  # Puedes ajustar esto para que se vea bien en tu página
                    "boxSizing": "border-box"  # Asegura que el padding no afecte el tamaño del elemento
                }
            ))

        # Se asegura de que las actividades se mantengan centradas y del mismo tamaño
        actividades.append(html.Div(
            children=actividad_fila,
            style={
                "display": "flex",
                "justifyContent": "center",  # Esto centra las actividades en la última fila
                "marginTop": "20px",
                "flexWrap": "wrap",  # Esto permite que las actividades se ajusten a la fila
                "gap": "20px",  # Espacio entre las actividades
                "textAlign": "center"  # Alinea el contenido de las actividades
            }
        ))

    return actividades





