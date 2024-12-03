import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
from components import header
from utils import generar_mapa
import plotly.express as px


# Datos del DataFrame
file_path = './data/codigosPostales.xlsx'  # Cambia la ruta si es necesario
df_cp = pd.read_excel(file_path)

# Determinación de los límites de latitud y longitud para recortar el mapa
min_latitud = df_cp['LATITUD'].min() - 0.05  # Añadir un margen
max_latitud = df_cp['LATITUD'].max() + 0.05  # Añadir un margen
min_longitud = df_cp['LONGITUD'].min() - 0.05  # Añadir un margen
max_longitud = df_cp['LONGITUD'].max() + 0.05  # Añadir un margen

# Crear el mapa inicial sin predicciones, con puntos azules y solo el código postal
fig_inicial = go.Figure(go.Scattermapbox(
    lat=df_cp['LATITUD'],
    lon=df_cp['LONGITUD'],
    mode='markers',
    marker=go.scattermapbox.Marker(size=14, color='blue'),
    text=df_cp['CP'],
    hoverinfo='text'
))

# Actualizar el diseño del mapa inicial
fig_inicial.update_layout(
    mapbox_style="carto-positron",
    mapbox_center={"lat": 40.416775, "lon": -3.703790},  # Coordenadas de Madrid
    mapbox_zoom=10,
    mapbox=dict(
        bounds=dict(
            north=max_latitud,
            south=min_latitud,
            east=max_longitud,
            west=min_longitud
        ),
        style='carto-positron',
    ),
    height=800
)


def generar_histograma(predicciones):
    """
    Genera un histograma a partir de un diccionario de predicciones.

    Args:
        predicciones (dict): Diccionario con códigos postales como claves y valores predichos.

    Returns:
        fig: Figura del histograma.
    """
    # Ordenar las predicciones de mayor a menor
    predicciones_ordenadas = dict(sorted(predicciones.items(), key=lambda item: item[1], reverse=True))

    # Crear el DataFrame para el histograma
    df_histograma = pd.DataFrame({
        'Codigo Postal': list(predicciones_ordenadas.keys()),
        'Numero de Bicicletas': list(predicciones_ordenadas.values())
    })

    # Crear el histograma usando Plotly Express
    fig = px.bar(
        df_histograma, 
        x='Codigo Postal', 
        y='Numero de Bicicletas', 
        title='Predicción de Bicicletas por Código Postal',
        labels={'Codigo Postal': 'Código Postal', 'Numero de Bicicletas': 'Número de Bicicletas'},
    )
    
    fig.update_layout(
        xaxis_type='category',
        xaxis_title='Código Postal',
        yaxis_title='Número de Bicicletas',
        height=600
    )
    
    return fig


def predictor_page():
    # Página del predictor de bicicletas
    return html.Div([
        # Agregar el header
        header(),

        # Dividir la pantalla en dos columnas: izquierda para el formulario y derecha para el mapa
        dbc.Row([
            # Columna izquierda (formulario)
            dbc.Col(
                html.Div([
                    html.H3("Introduce los parámetros:", style={"textAlign": "center", "marginBottom": "20px"}),

                    # Sección destacada para Fecha y Hora Unlock
                    html.Div([
                        html.H4("Paso 1: Selecciona la Fecha y Hora", style={"textAlign": "center", "marginBottom": "20px", "color": "#007BFF"}),
                        dbc.Row(
                            [
                                # Columna para la fecha
                                dbc.Col([
                                    html.Label("Fecha:", style={"textAlign": "center", "display": "block"}),
                                    dcc.DatePickerSingle(
                                        id="fecha-picker",
                                        display_format="YYYY-MM-DD",
                                        placeholder="Selecciona una fecha",
                                        min_date_allowed=datetime.now().date(),
                                        style={"width": "100%", "height": "40px", "textAlign": "center"}
                                    )
                                ], width=6, style={"textAlign": "center"}),  # Centrado
                                # Columna para la hora
                                dbc.Col([
                                    html.Label("Hora Unlock:", style={"textAlign": "center", "display": "block"}),
                                    dcc.Input(
                                        id="hora-unlock",
                                        type="number",
                                        placeholder="Introduce la hora (0-23)",
                                        min=0,
                                        max=23,
                                        style={"width": "45%", "height": "40px", "textAlign": "center"}
                                    )
                                ], width=6, style={"textAlign": "center"})  # Centrado
                            ],
                            justify="center",  # Centra la fila horizontalmente
                            align="center",    # Alinea verticalmente en el centro
                            style={"marginBottom": "20px"}
                        )
                    ], style={
                        "border": "2px solid #007BFF",
                        "borderRadius": "10px",
                        "backgroundColor": "#f0f8ff",
                        "marginBottom": "20px",
                        "padding": "20px",
                        "textAlign": "center"
                    }),

                    # Botón azul reposicionado entre la fecha/hora y las previsiones
                    dbc.Button("Me fío de la previsión", id="trust-forecast-btn", color="primary", style={"width": "100%", "marginBottom": "20px"}),

                    # Métricas meteorológicas agrupadas
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Precipitación (prcp_x):"),
                                dcc.Input(id="prcp-x", type="number", placeholder="mm", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                            dbc.Col([
                                html.Label("Dirección del viento (wdir_x):"),
                                dcc.Input(id="wdir-x", type="number", placeholder="grados", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                            dbc.Col([
                                html.Label("Velocidad del viento (wspd_x):"),
                                dcc.Input(id="wspd-x", type="number", placeholder="km/h", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Presión atmosférica (pres_x):"),
                                dcc.Input(id="pres-x", type="number", placeholder="hPa", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                            dbc.Col([
                                html.Label("Temperatura (temp):"),
                                dcc.Input(id="temp", type="number", placeholder="°C", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                            dbc.Col([
                                html.Label("Punto de rocío (dwpt):"),
                                dcc.Input(id="dwpt", type="number", placeholder="°C", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Temperatura mínima (t_min):"),
                                dcc.Input(id="t_min", type="number", placeholder="°C", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                            dbc.Col([
                                html.Label("Temperatura máxima (t_max):"),
                                dcc.Input(id="t_max", type="number", placeholder="°C", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                            dbc.Col([
                                html.Label("Temperatura media (t_avg):"),
                                dcc.Input(id="t_avg", type="number", placeholder="°C", style={"width": "100%", "marginBottom": "10px"})
                            ], width=4),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Humedad relativa (rhum):"),
                                dcc.Input(id="rhum", type="number", placeholder="%", style={"width": "100%", "marginBottom": "10px"})
                            ], width=6),
                            dbc.Col([
                                html.Label("Tipo de clima:"),
                                dcc.Dropdown(
                                    id="weather-type",
                                    options=[
                                        {"label": "Clear", "value": "clear"},
                                        {"label": "Cloudy", "value": "cloudy"},
                                        {"label": "Fair", "value": "fair"},
                                        {"label": "Fog", "value": "fog"},
                                        {"label": "Rain", "value": "rain"},
                                        {"label": "Overcast", "value": "overcast"},
                                        {"label": "Rain Shower", "value": "rain shower"}
                                    ],
                                    placeholder="Selecciona el tipo de clima",
                                    style={"width": "100%", "marginBottom": "10px"}
                                )
                            ], width=6)
                        ])
                    ], style={"padding": "10px"}),

                    # Contenedor para mostrar mensajes
                    html.Div(id="output-prediction", style={"marginTop": "20px"}),

                    # Botón inferior
                    dbc.Button("Predecir", id="predict-btn", color="success", style={"width": "100%", "marginTop": "20px"})
                ], style={"padding": "20px", "backgroundColor": "#f8f9fa", "borderRadius": "10px"}),
                width=6
            ),

            # Columna derecha (con el mapa)
             dbc.Col([
                dcc.Graph(id="mapa-predictor", figure=fig_inicial),  # Mapa inicial
                dcc.Graph(id="histograma-prediccion"),
            ], width=6)
        ])
    ])


