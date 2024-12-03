from dash import Dash, html
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from inicio import homepage  # Importa la página de inicio
from estaciones import estaciones_page  # Importa la página de estaciones
from estacion_seleccionada import estacion_seleccionada_page  # Importa la página de estación seleccionada
from clima import clima_page  # Importa la página de clima
from sobreMadrid import sobre_madrid_page  # Importa la página sobre Madrid
from sobreMadrid import cargar_actividades, create_activities
import pandas as pd
from predictorBicis import predictor_page
from dash.dependencies import Input, Output, State
import requests
from datetime import datetime, timedelta
import dash
import os
import joblib
import pickle
import sklearn
import lightgbm
import random
import plotly.graph_objects as go
from utils import generar_mapa
from predictorBicis import fig_inicial, df_cp
from predictorBicis import generar_histograma
import math
from datetime import datetime
from datetime import date, timedelta
import pickle
import gzip


# Define tu clave API aquí
API_KEY = "e1191302c816272e38702d9bfe574df3"
app = Dash(__name__)
server = app.server

###########################################################################################################
# Cargar datos al inicio
data_path = './data'
try:
    trips_per_hour = pd.read_csv(f'{data_path}/trips_per_hour.csv')
    trips_per_week = pd.read_csv(f'{data_path}/trips_per_week.csv')
    trips_per_month = pd.read_csv(f'{data_path}/trips_per_month.csv')
    trips_per_year = pd.read_csv(f'{data_path}/trips_per_year.csv')
    #print("Datos cargados correctamente al iniciar la aplicación.")
except Exception as e:
    print(f"Error al cargar los datos: {e}")

# Cargar modelos al inicio
models = {}
models_path = './models'
try:
    for file_name in os.listdir(models_path):
        if file_name.endswith('.pkl'):
            model_name = os.path.splitext(file_name)[0]
            models[model_name] = joblib.load(os.path.join(models_path, file_name))
    #print(f"Modelos cargados correctamente")
except Exception as e:
    print(f"Error al cargar los modelos: {e}")

# Ruta al archivo de códigos postales
file_path = './data/codigosPostales.xlsx'
try:
    df_cp = pd.read_excel(file_path)
    if df_cp.empty or not all(col in df_cp.columns for col in ['CP', 'LATITUD', 'LONGITUD']):
        raise ValueError("El archivo debe contener las columnas 'CP', 'LATITUD', y 'LONGITUD'.")
except FileNotFoundError:
    print(f"Archivo no encontrado en la ruta: {file_path}")
    df_cp = pd.DataFrame(columns=['CP', 'LATITUD', 'LONGITUD'])  # Fallback
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    df_cp = pd.DataFrame(columns=['CP', 'LATITUD', 'LONGITUD'])  # Fallback


############################################################################################################

# Lista de días festivos en Madrid (actualiza según las festividades del año actual)
festivos_madrid = [
    "2024-01-01",  # Año Nuevo
    "2024-01-06",  # Reyes
    "2024-03-28",  # Jueves Santo
    "2024-03-29",  # Viernes Santo
    "2024-05-01",  # Día del Trabajo
    "2024-05-02",  # Día de la Comunidad de Madrid
    "2024-08-15",  # Asunción de la Virgen
    "2024-10-12",  # Fiesta Nacional de España
    "2024-11-01",  # Todos los Santos
    "2024-12-06",  # Día de la Constitución Española
    "2024-12-08",  # Inmaculada Concepción
    "2024-12-25",  # Navidad
]

def analizar_fecha(fecha, festivos_madrid):
    """
    Analiza una fecha para determinar:
    - Día de la semana.
    - Si es festivo en Madrid.
    - Número del día en el año.
    - Número de la semana.

    Parámetros:
    - fecha (str): Fecha en formato 'YYYY-MM-DD'.
    - festivos_madrid (list): Lista de días festivos en Madrid en formato 'YYYY-MM-DD'.

    Retorna:
    - dict: Diccionario con los resultados.
    """
    # Convertir fecha de string a datetime
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    
    # Calcular día de la semana
    dia_semana = fecha_dt.strftime("%A")  # Ejemplo: "Monday", "Tuesday"

    # Verificar si es festivo
    es_festivo = fecha in festivos_madrid

    # Calcular el número del día del año
    dia_del_año = fecha_dt.timetuple().tm_yday

    # Calcular el número de semana
    numero_semana = fecha_dt.isocalendar()[1]

    return {
        "dia_semana": dia_semana,
        "es_festivo": es_festivo,
        "dia_del_año": dia_del_año,
        "numero_semana": numero_semana
    }


def get_season(date):
    """Determina la estación del año según la fecha."""
    if isinstance(date, str):
        # Convertir la fecha de string a datetime
        date = datetime.strptime(date, "%Y-%m-%d")  # Ajusta el formato según sea necesario

    month_day = (date.month, date.day)

    seasons = {
        "winter": [(1, 1), (3, 20)],  # Invierno: 1 de enero - 19 de marzo
        "spring": [(3, 21), (6, 20)],  # Primavera: 20 de marzo - 20 de junio
        "summer": [(6, 21), (9, 22)],  # Verano: 21 de junio - 22 de septiembre
        "fall": [(9, 23), (12, 20)],  # Otoño: 23 de septiembre - 20 de diciembre
        "winter_end": [(12, 21), (12, 31)],  # Invierno: 21 de diciembre - 31 de diciembre
    }

    for season, (start, end) in seasons.items():
        if start <= month_day <= end:
            return season
    return "winter"  # Fallback para fechas fuera del rango

def get_total_trips_by_zip(dataset, zip_code):
    """
    Obtiene el total de viajes (total_trips) para un código postal (zipCode_unlock) específico.

    Parámetros:
    - dataset (DataFrame): DataFrame con las columnas 'zipCode_unlock' y 'total_trips'.
    - zip_code (int/str): Código postal para el cual se desea obtener el total de viajes.

    Retorna:
    - int: Total de viajes para el código postal dado. Retorna 0 si no se encuentra.
    """
    # Filtrar el DataFrame para el código postal específico
    filtered = dataset[dataset['zipCode_unlock'] == zip_code]

    # Retornar el valor de total_trips si existe, de lo contrario, devolver 0
    if not filtered.empty:
        return int(filtered['total_trips'].iloc[0])
    else:
        return 0

def get_total_trips_by_zip_and_week(dataset, zip_code, week_number):
    """
    Obtiene el total de viajes (total_trips) para un código postal (zipCode_unlock) 
    y un número de semana específico.

    Parámetros:
    - dataset (DataFrame): DataFrame con las columnas 'zipCode_unlock', 'week_number', y 'total_trips'.
    - zip_code (int/str): Código postal para el cual se desea obtener el total de viajes.
    - week_number (int): Número de la semana.

    Retorna:
    - int: Total de viajes para el código postal y número de semana dados. Retorna 0 si no se encuentra.
    """
    # Filtrar el DataFrame para el código postal y la semana específicos
    filtered = dataset[(dataset['zipCode_unlock'] == zip_code) & 
                       (dataset['week_number'] == week_number)]

    # Retornar el valor de total_trips si existe, de lo contrario, devolver 0
    if not filtered.empty:
        return int(filtered['total_trips_per_week'].iloc[0])
    else:
        return 0
    
def get_month_from_day_of_year(day_of_year):
    """
    Determina el número del mes dado un número de día del año.

    Parámetros:
    - day_of_year (int): Número de día del año (1 para el 1 de enero, 32 para el 1 de febrero, etc.).

    Retorna:
    - int: Número del mes correspondiente (1 para enero, 2 para febrero, etc.).
    """
    import datetime

    # Año arbitrario no bisiesto para calcular (por ejemplo, 2023)
    base_date = datetime.date(2023, 1, 1)
    target_date = base_date + datetime.timedelta(days=day_of_year - 1)
    
    return target_date.month


def actualizar_grafico(df, predicciones):
    """
    Actualiza la figura del mapa con colores y etiquetas basadas en las predicciones.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'LATITUD', 'LONGITUD' y 'CP'.
        predicciones (dict): Diccionario con códigos postales como claves y valores predichos.

    Returns:
        go.Figure: Figura del mapa actualizada.
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío. Verifica los datos de códigos postales.")

    # Añadir las predicciones al DataFrame
    df['n_bicis'] = df['CP'].map(predicciones).fillna(0)

    # Calcular colores proporcionales a los valores predichos
    max_bicis = df['n_bicis'].max()
    min_bicis = df['n_bicis'].min()
    colors = [
        f"rgb({int(255 * (bicis - min_bicis) / (max_bicis - min_bicis))},0,{int(255 * (1 - (bicis - min_bicis) / (max_bicis - min_bicis)))})"
        for bicis in df['n_bicis']
    ]

    # Crear la figura del mapa
    fig = go.Figure(go.Scattermapbox(
        lat=df['LATITUD'],
        lon=df['LONGITUD'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color=colors,
            opacity=0.7
        ),
        text=[f"Código postal: {cp}<br>Número de bicis: {bicis}" for cp, bicis in zip(df['CP'], df['n_bicis'])],
        hoverinfo='text'
    ))

    # Configurar el diseño del mapa
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": 40.416775, "lon": -3.703790},  # Coordenadas de Madrid
        mapbox_zoom=10,
        height=800
    )

    return fig

def get_total_trips_by_zip_and_month(dataset, zip_code, month):
    """
    Obtiene el total de viajes (total_trips_per_month) para un código postal (zipCode_unlock)
    y un mes específico.

    Parámetros:
    - dataset (DataFrame): DataFrame con las columnas 'zipCode_unlock', 'month', y 'total_trips_per_month'.
    - zip_code (int/str): Código postal para el cual se desea obtener el total de viajes.
    - month (int): Mes para el cual se desea obtener el total de viajes (1 a 12).

    Retorna:
    - int: Total de viajes para el código postal y mes dados. Retorna 0 si no se encuentra.
    """
    # Validar si las columnas necesarias existen
    required_columns = {'zipCode_unlock', 'month', 'total_trips_per_month'}
    if not required_columns.issubset(dataset.columns):
        raise KeyError(f"El DataFrame debe contener las columnas: {required_columns}")

    # Filtrar el DataFrame para el código postal y el mes específicos
    filtered = dataset[(dataset['zipCode_unlock'] == zip_code) & 
                       (dataset['month'] == month)]

    # Retornar el valor de total_trips_per_month si existe, de lo contrario, devolver 0
    if not filtered.empty:
        return int(filtered['total_trips_per_month'].iloc[0])
    else:
        return 0


def get_total_trips_by_zip_and_hour(dataset, zip_code, hour):
    """
    Obtiene el total de viajes (total_trips_per_hour) para un código postal (zipCode_unlock)
    y una hora específica.

    Parámetros:
    - dataset (DataFrame): DataFrame con las columnas 'zipCode_unlock', 'hora_unlock', y 'total_trips_per_hour'.
    - zip_code (int/str): Código postal para el cual se desea obtener el total de viajes.
    - hour (int): Hora para la cual se desea obtener el total de viajes (0-23).

    Retorna:
    - int: Total de viajes para el código postal y la hora dados. Retorna 0 si no se encuentra.
    """
    # Validar si las columnas necesarias existen
    required_columns = {'zipCode_unlock', 'hora_unlock', 'total_trips_per_hour'}
    if not required_columns.issubset(dataset.columns):
        raise KeyError(f"El DataFrame debe contener las columnas: {required_columns}")

    # Filtrar el DataFrame para el código postal y la hora específicos
    filtered = dataset[(dataset['zipCode_unlock'] == zip_code) & 
                       (dataset['hora_unlock'] == hour)]

    # Retornar el valor de total_trips_per_hour si existe, de lo contrario, devolver 0
    if not filtered.empty:
        return int(filtered['total_trips_per_hour'].iloc[0])
    else:
        return 0


# 2. Cargar el modelo desde un archivo
def load_model():
    """
    Carga un modelo desde un archivo local.
    """
    # Cargar el modelo comprimido
    with gzip.open("./models/modelo_cargado_comprimido.pkl.gz", "rb") as compressed_file:
        model = pickle.load(compressed_file)
    #print(f"Modelo cargado desde: {filepath}")
    return model

# 3. Predecir con el modelo cargado
def predict_with_model(model, new_data):
    """
    Realiza predicciones con un modelo dado y nuevos datos.
    """
    if not isinstance(new_data, pd.DataFrame):
        raise ValueError("Los datos nuevos deben estar en un DataFrame.")
    predictions = model.predict(new_data)
    return predictions

############################################################################################################
# Define la estructura de navegación
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Maneja la URL actual
    html.Div(id='page-content')  # Contenedor dinámico para las páginas
])

############################################################################################################

# Callback para cambiar el contenido de la página
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')  # Escucha cambios en la URL
)
def display_page(pathname):
    if pathname == '/estaciones':
        return estaciones_page()
    elif pathname.startswith('/estacion_seleccionada/'):
        # Extrae el código postal de la URL
        codigo_postal = int(pathname.split('/')[-1])
        return estacion_seleccionada_page(codigo_postal)
    elif pathname == '/clima':
        return clima_page(API_KEY)
    elif pathname == '/sobre-madrid' or pathname == "/sobre-Madrid":
        return sobre_madrid_page()  # Página sobre Madrid
    elif pathname == '/predictor-bicis':
        return predictor_page()
    else:
        return homepage()  # Página de inicio por defecto
    

# Callback para actualizar actividades
@app.callback(
    Output('activities-container', 'children'),
    [Input('date-picker', 'date'),
     Input('gratis-checklist', 'value')]  # Input adicional para filtrar por "gratis"
)
def update_activities(selected_date, filtros_gratis):
    df_actividades = cargar_actividades()  # Cargar las actividades desde el CSV
    fecha_seleccionada = pd.to_datetime(selected_date).date()  # Convertir la fecha seleccionada a un objeto de tipo 'date'
    return create_activities(df_actividades, fecha_seleccionada, filtros_gratis)  # Filtrar y devolver las actividades


@app.callback(
    [
        Output('mapa-predictor', 'figure'),  # Actualiza el mapa ya existente
        Output('histograma-prediccion', 'figure'),  # Añadir la salida del histograma
        Output('prcp-x', 'value'),
        Output('wdir-x', 'value'),
        Output('wspd-x', 'value'),
        Output('pres-x', 'value'),
        Output('temp', 'value'),  # Previsión de temperatura en ese momento
        Output('t_min', 'value'),  # Temperatura mínima del día
        Output('t_max', 'value'),  # Temperatura máxima del día
        Output('t_avg', 'value'),  # Temperatura media del día
        Output('rhum', 'value'),
        Output('weather-type', 'value'),
        Output('dwpt', 'value'),
        Output('output-prediction', 'children')
    ],
    [
        Input('trust-forecast-btn', 'n_clicks'),
        Input('predict-btn', 'n_clicks')
    ],
    [
        State('fecha-picker', 'date'),
        State('hora-unlock', 'value'),
        State('prcp-x', 'value'),
        State('wdir-x', 'value'),
        State('wspd-x', 'value'),
        State('pres-x', 'value'),
        State('temp', 'value'),
        State('t_min', 'value'),
        State('t_max', 'value'),
        State('t_avg', 'value'),
        State('rhum', 'value'),
        State('weather-type', 'value'),
        State('dwpt', 'value')
    ]
)
def handle_buttons(
    trust_forecast_clicks, predict_clicks,
    fecha, hora, prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt
):
    # Obtener el contexto del callback para verificar qué lo activó
    ctx = dash.callback_context

    # Si no se ha activado ningún botón, devolver el mapa inicial
    if not ctx.triggered:
        return [fig_inicial, go.Figure(), prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt, ""]

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Lógica para el botón de 'trust-forecast-btn'
    if triggered_id == 'trust-forecast-btn' and trust_forecast_clicks:
        if not fecha:
            return [dash.no_update, dash.no_update, prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt, "Selecciona una fecha válida antes de continuar."]

        # Llamada a la API de OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/forecast?q=Madrid,ES&units=metric&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()

        if 'list' not in data:
            return [dash.no_update, dash.no_update, prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt, "Error al obtener datos meteorológicos. Intenta de nuevo."]

        # Filtrar datos para el día seleccionado
        fecha_seleccionada = datetime.strptime(fecha, "%Y-%m-%d").date()
        datos_dia = [
            forecast["main"]
            for forecast in data["list"]
            if datetime.strptime(forecast["dt_txt"], "%Y-%m-%d %H:%M:%S").date() == fecha_seleccionada
        ]

        if not datos_dia:
            return [dash.no_update, dash.no_update, prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt, "No hay datos disponibles para el día seleccionado."]

        # Calcular estadísticas de temperatura del día completo
        temperaturas_dia = [dato["temp"] for dato in datos_dia]
        temp_media = sum(temperaturas_dia) / len(temperaturas_dia)
        temp_max = max(temperaturas_dia)
        temp_min = min(temperaturas_dia)

        # Seleccionar el pronóstico más cercano a la hora seleccionada
        target_datetime = datetime.strptime(f"{fecha} {str(hora).zfill(2)}:00:00", "%Y-%m-%d %H:%M:%S")
        closest_forecast = None
        closest_difference = timedelta.max

        for forecast in data["list"]:
            forecast_time = datetime.strptime(forecast["dt_txt"], "%Y-%m-%d %H:%M:%S")
            difference = abs(forecast_time - target_datetime)

            if difference < closest_difference:
                closest_difference = difference
                closest_forecast = forecast

        if closest_forecast:
            main = closest_forecast["main"]
            wind = closest_forecast["wind"]
            weather_main = closest_forecast["weather"][0]["main"]

            # Mapeo de los tipos de clima
            weather_mapping = {
                "Clear": "clear",
                "Clouds": "cloudy",
                "Fair": "fair",
                "Fog": "fog",
                "Rain": "rain",
                "Overcast": "overcast",
                "Drizzle": "rain",
                "Thunderstorm": "rain shower",
                "Snow": "snow"
            }
            weather_type = weather_mapping.get(weather_main, "unknown")

            # Calcular el punto de rocío
            temp_actual = main["temp"]
            rh = main["humidity"]
            dew_point = temp_actual - ((100 - rh) / 5)

            return [
                dash.no_update,  # No se actualiza el mapa con este botón, solo datos meteorológicos
                dash.no_update,  # No se actualiza el histograma
                closest_forecast.get("rain", {}).get("3h", 0),  # Precipitación
                wind["deg"],  # Dirección del viento
                wind["speed"],  # Velocidad del viento
                main["pressure"],  # Presión
                temp_actual,  # Temperatura actual en el momento seleccionado
                temp_min,  # Temperatura mínima del día
                temp_max,  # Temperatura máxima del día
                temp_media,  # Temperatura media del día
                main["humidity"],  # Humedad relativa
                weather_type,  # Tipo de clima
                round(dew_point, 2),  # Punto de rocío
                ""
            ]

    # Lógica para el botón de 'predict-btn'
    if triggered_id == 'predict-btn' and predict_clicks:
        if not fecha:
            return [fig_inicial, go.Figure(), prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt, "Selecciona una fecha antes de continuar."]

        # Generar predicciones simuladas
        #predicciones = {cp: random.randint(3, 50) for cp in df_cp["CP"]}
        predicciones = {}
        modelo_cargado = load_model()
        season=get_season(fecha)
        season_winter=0
        season_fall=0
        season_spring=0
        season_summer=0
        if season=="winter":
            season_winter=0
        elif season=="fall":
            season_fall=1
        elif season=="spring":
            season_spring=1
        else:
            season_summer=1
        analisisFecha=analizar_fecha(fecha, festivos_madrid)
        dia_del_año=analisisFecha["dia_del_año"]
        es_festivo=analisisFecha["es_festivo"]
        if es_festivo==True:
            es_festivo=1
        else:
            es_festivo=0
        numero_semana=analisisFecha["numero_semana"]
        dia_semana=analisisFecha["dia_semana"]
        dia_semana_Friday=0
        dia_semana_Monday=0
        dia_semana_Saturday=0
        dia_semana_Sunday=0
        dia_semana_Thursday=0
        dia_semana_Tuesday=0
        dia_semana_Wednesday=0
        if dia_semana == "Friday":
            dia_semana_Friday = 1
        elif dia_semana == "Monday":
            dia_semana_Monday = 1
        elif dia_semana == "Saturday":
            dia_semana_Saturday = 1
        elif dia_semana == "Sunday":
            dia_semana_Sunday = 1
        elif dia_semana == "Thursday":
            dia_semana_Thursday = 1
        elif dia_semana == "Tuesday":
            dia_semana_Tuesday = 1
        elif dia_semana == "Wednesday":
            dia_semana_Wednesday = 1
        coco_x_hourly_Clear=0
        coco_x_hourly_Cloudy=0
        coco_x_hourly_Fair=0
        coco_x_hourly_Fog=0
        coco_x_hourly_Light_Rain=0
        coco_x_hourly_Overcast=0
        coco_x_hourly_Rain=0
        coco_x_hourly_Rain_Shower=0
        
        if weather_type=="snow":
            nieve=1
        elif weather_type=="clear":
            coco_x_hourly_Clear=1
        elif weather_type=="cloudy":
            coco_x_hourly_Cloudy=1
            coco_x_hourly_Overcast=1
        elif weather_type=="fair":
            coco_x_hourly_Fair=1
        elif weather_type=="fog":
            coco_x_hourly_Fog=1
        elif weather_type=="rain":
            coco_x_hourly_Rain=1
            coco_x_hourly_Rain_Shower=1
            coco_x_hourly_Light_Rain=1
        else:
            coco_x_hourly_Clear=1
        
        for cp in df_cp["CP"]:
            new_data = pd.DataFrame({
                'dia_año': [dia_del_año],
                'zipCode_unlock': [cp],
                'prcp_x_daily': [prcp],
                'wspd_x_daily': [wspd],
                'pres_x_daily': [pres],
                'temp_x_daily': [temp],
                'rhum_x_daily': [rhum],
                'dwpt_x_daily': [dwpt],
                'semana_año': [numero_semana], 
                'es_festivo': [es_festivo], 
                'tmin_daily': [t_min],
                'tmax_daily': [t_max],
                'tavg_daily': [t_avg],
                'total_trips_year': [get_total_trips_by_zip(trips_per_year, cp)], 
                'total_trips_week': [get_total_trips_by_zip_and_week(trips_per_week, cp, numero_semana)],  
                'total_trips_hour': [get_total_trips_by_zip_and_hour(trips_per_hour, cp, hora)],   #
                'total_trips_month': [get_total_trips_by_zip_and_month(trips_per_month, cp, get_month_from_day_of_year(dia_del_año))], #
                'dia_semana_Friday': [dia_semana_Friday],
                'dia_semana_Monday': [dia_semana_Monday],
                'dia_semana_Saturday': [dia_semana_Saturday],
                'dia_semana_Sunday': [dia_semana_Sunday],
                'dia_semana_Thursday': [dia_semana_Thursday],
                'dia_semana_Tuesday': [dia_semana_Tuesday],
                'dia_semana_Wednesday': [dia_semana_Wednesday],
                'estacion_Invierno': [season_winter],
                'estacion_Otoño': [season_fall],
                'estacion_Primavera': [season_spring],
                'estacion_Verano': [season_summer],
                'coco_x_hourly_Clear': [coco_x_hourly_Clear], 
                'coco_x_hourly_Cloudy': [coco_x_hourly_Cloudy],
                'coco_x_hourly_Fair': [coco_x_hourly_Fair],
                'coco_x_hourly_Fog': [coco_x_hourly_Fog],
                'coco_x_hourly_Light Rain': [coco_x_hourly_Light_Rain],
                'coco_x_hourly_Overcast': [coco_x_hourly_Overcast],
                'coco_x_hourly_Rain': [coco_x_hourly_Rain],
                'coco_x_hourly_Rain Shower': [coco_x_hourly_Rain_Shower] 
            })
            pred_i = predict_with_model(modelo_cargado, new_data)
            predicciones[cp] = math.trunc(pred_i[0])


        #print(predicciones)
        #print("Predicciones generadas:", predicciones)
        #MODIFICAR ESTO DE AQUÍ PARA QUE LAS PREDICCIONES SEAN LOS MODELOS

        # Actualizar la figura del mapa con las predicciones
        fig = generar_mapa(df_cp, predicciones)

        # Generar el histograma con las predicciones
        fig_histograma = generar_histograma(predicciones)

        return [
            fig,  # Actualiza el mapa existente
            fig_histograma,  # Actualiza el histograma
            prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt,
            "Predicción actualizada correctamente"
        ]

    # Si no se cumple ninguna condición, devuelve el mapa inicial
    return [fig_inicial, go.Figure(), prcp, wdir, wspd, pres, temp, t_min, t_max, t_avg, rhum, weather_type, dwpt, "Acción no reconocida."]


if __name__ == '__main__':
    app.run_server(debug=True)
