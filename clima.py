import requests
from dash import html, dcc, callback
from dash.dependencies import Input, Output, ALL
import plotly.graph_objects as go
import pandas as pd
from components import header
from dash import callback_context

# Función para obtener la previsión por días
def obtener_prevision(api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Madrid,ES&units=metric&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    prevision = []
    fechas = {item['dt_txt'].split(" ")[0] for item in data['list']}  # Fechas únicas

    for fecha in sorted(fechas):
        # Filtra los datos para cada fecha específica
        items_dia = [item for item in data['list'] if item['dt_txt'].startswith(fecha)]
        
        # Obtén temperaturas, descripciones e iconos del día
        temps = [item['main']['temp'] for item in items_dia]
        descripcion = items_dia[0]['weather'][0]['description']  # Usa la descripción del primer intervalo del día
        icono = items_dia[0]['weather'][0]['icon']  # Usa el icono del primer intervalo del día

        temp_min = round(min(temps))  # Temperatura mínima del día
        temp_max = round(max(temps))  # Temperatura máxima del día

        prevision.append({
            "fecha": fecha,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "descripcion": descripcion,
            "icono": f"http://openweathermap.org/img/wn/{icono}.png"
        })

    return prevision[:5]



# Función para obtener previsión horaria
def obtener_prevision_por_horas(api_key, fecha):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Madrid,ES&units=metric&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    prevision_horas = []
    for item in data['list']:
        if item['dt_txt'].startswith(fecha):
            hora = item['dt_txt'].split(" ")[1][:5]
            temp = round(item['main']['temp'])
            precipitacion = max(0, item.get('rain', {}).get('3h', 0))  # Asegura valores positivos
            prevision_horas.append({"hora": hora, "temp": temp, "precipitacion": precipitacion})

    if not prevision_horas:
        raise ValueError(f"No se encontraron datos para la fecha seleccionada: {fecha}")

    return prevision_horas


# Página de clima
def clima_page(api_key):
    prevision = obtener_prevision(api_key)

    return html.Div([
        header(),
        dcc.Store(id="selected-day"),
        html.Main(
            style={
                "padding": "2rem",
                "backgroundColor": "white",
                "margin": "20px auto",
                "maxWidth": "800px",
                "boxShadow": "0 0 10px rgba(0, 0, 0, 0.1)",
                "borderRadius": "10px"
            },
            children=[
                html.H2("Previsión del Clima en Madrid (Próximos 5 días)", style={"color": "#0044cc"}),
                html.Table(
                    style={
                        "width": "100%",
                        "borderCollapse": "collapse",
                        "marginTop": "20px",
                        "textAlign": "center",
                    },
                    children=[
                        html.Thead(
                            html.Tr([html.Th(dia["fecha"]) for dia in prevision])
                        ),
                        html.Tbody([
                            html.Tr([
                                html.Td(html.Img(
                                    src=dia["icono"],
                                    style={"width": "50px", "cursor": "pointer"},
                                    id={"type": "icono-dia", "index": dia["fecha"]}
                                )) for dia in prevision
                            ]),
                            html.Tr([
                                html.Td([
                                    html.Span(f"{dia['temp_min']}°C", style={"color": "blue"}),
                                    " / ",
                                    html.Span(f"{dia['temp_max']}°C", style={"color": "red"})
                                ]) for dia in prevision
                            ])
                        ])
                    ]
                ),
                html.Div(id="grafico-horas")
            ]
        )
    ])


# Callback para actualizar el gráfico
@callback(
    Output("grafico-horas", "children"),
    Input({"type": "icono-dia", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def mostrar_prevision_horaria(*n_clicks):
    ctx = callback_context.triggered
    if not ctx:
        return html.Div("Selecciona un día válido.")

    input_id = ctx[0]["prop_id"].split(".")[0]
    fecha_seleccionada = eval(input_id)["index"]

    try:
        prevision_horas = obtener_prevision_por_horas("e1191302c816272e38702d9bfe574df3", fecha_seleccionada)
        df = pd.DataFrame(prevision_horas)

        # Crear gráfico combinado
        fig = go.Figure()

        # Precipitación en barras azules oscuro con mínima altura visible
        bar_width = 0.6
        fig.add_trace(go.Bar(
            x=df["hora"],
            y=[prec if prec > 0 else 0.01 for prec in df["precipitacion"]],
            name="Precipitación (mm)",
            marker_color="darkblue",
            yaxis="y2",
            width=bar_width,
            opacity=0.8  # Añadir transparencia
        ))

        # Temperatura en línea roja
        fig.add_trace(go.Scatter(
            x=df["hora"],
            y=df["temp"],
            mode="lines+markers",
            name="Temperatura (°C)",
            line=dict(color="red", width=2),
            marker=dict(size=8)
        ))

        # Configuración de ejes
        fig.update_layout(
            title=f"Climograma para {fecha_seleccionada}",
            xaxis=dict(title="Hora"),
            yaxis=dict(
                title="Temperatura (°C)",
                titlefont=dict(color="red"),
                tickfont=dict(color="red")
            ),
            yaxis2=dict(
                title="Precipitación (mm)",
                titlefont=dict(color="darkblue"),
                tickfont=dict(color="darkblue"),
                anchor="x",
                overlaying="y",
                side="right",
                range=[0, max(1, max(df["precipitacion"]) + 1)]
            ),
            legend=dict(x=0, y=1),
            margin=dict(l=40, r=40, t=40, b=40)
        )

        return dcc.Graph(figure=fig)
    except ValueError as ve:
        return html.Div(str(ve))



"""
Hacer la previsión del tiempo guay y luego hacer un climograma también que esté chulo
Sacar algunas estadísticas del tiempo

"""
