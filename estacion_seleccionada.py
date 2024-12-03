import pandas as pd
from dash import html, dcc, Input, Output, State, callback
import plotly.express as px
from components import header
from shared_data import DATA_BY_STATION


def estacion_seleccionada_page(codigo_postal):
    """
    Genera la página para una estación seleccionada, con un gráfico que puede cambiar según la agrupación seleccionada.

    Args:
        codigo_postal (int): Código postal de la estación seleccionada.

    Returns:
        html.Div: Página de la estación seleccionada.
    """
    # Obtener los datos prefiltrados para esta estación
    df_filtrado = DATA_BY_STATION.get(codigo_postal, pd.DataFrame())

    if df_filtrado.empty:
        return html.Div([
            header(),
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
                    html.H2(f"Estación CP {codigo_postal}", style={"color": "#0044cc"}),
                    html.P("No se encontraron datos para esta estación."),
                ]
            )
        ])

    # Asegúrate de que las fechas están en formato datetime
    df_filtrado["fecha_unlock"] = pd.to_datetime(df_filtrado["fecha_unlock"], errors="coerce")
    df_filtrado["tiempo"] = df_filtrado["fecha_unlock"] + pd.to_timedelta(df_filtrado["hora_unlock"], unit="h")

    return html.Div([
        header(),
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
                html.H2(f"Estación CP {codigo_postal}", style={"color": "#0044cc"}),
                html.P("Selecciona cómo deseas agrupar los datos:"),
                dcc.RadioItems(
                    id="agrupacion",
                    options=[
                        {"label": "Por hora", "value": "hora"},
                        {"label": "Por día", "value": "dia"},
                        {"label": "Por semana", "value": "semana"},
                        {"label": "Por mes", "value": "mes"},
                        {"label": "Día y Hora", "value": "dia_hora"}
                    ],
                    value="dia_hora",
                    style={"marginBottom": "20px"}
                ),
                html.Div([
                    html.Label("Fecha de inicio (2022):"),
                    dcc.DatePickerSingle(
                        id="fecha-inicio",
                        min_date_allowed="2022-01-01",
                        max_date_allowed="2022-12-31",
                        initial_visible_month="2022-01-01",
                        date="2022-01-01"
                    ),
                    html.Label("Fecha de fin (2022):"),
                    dcc.DatePickerSingle(
                        id="fecha-fin",
                        min_date_allowed="2022-01-01",
                        max_date_allowed="2022-12-31",
                        initial_visible_month="2022-12-31",
                        date="2022-12-31"
                    ),
                ], id="filtro-fechas", style={"marginBottom": "20px"}),
                dcc.Graph(id="grafico-agrupado"),
            ]
        )
    ])


@callback(
    Output("grafico-agrupado", "figure"),
    [
        Input("agrupacion", "value"),
        Input("url", "pathname"),
        Input("fecha-inicio", "date"),
        Input("fecha-fin", "date"),
    ]
)
def actualizar_grafico(agrupacion, pathname, fecha_inicio, fecha_fin):
    """
    Actualiza el gráfico según la agrupación seleccionada y las fechas seleccionadas.
    """
    # Extraer el código postal de la URL
    codigo_postal = int(pathname.split("/")[-1])
    df_filtrado = DATA_BY_STATION.get(codigo_postal, pd.DataFrame())

    if df_filtrado.empty:
        return px.scatter(title="No se encontraron datos para esta estación.")

    df_filtrado["fecha_unlock"] = pd.to_datetime(df_filtrado["fecha_unlock"], errors="coerce")
    df_filtrado["tiempo"] = df_filtrado["fecha_unlock"] + pd.to_timedelta(df_filtrado["hora_unlock"], unit="h")

    # Manejar rango de fechas
    if fecha_inicio and fecha_fin:
        fecha_inicio = pd.to_datetime(fecha_inicio)
        fecha_fin = pd.to_datetime(fecha_fin)

        if fecha_inicio > fecha_fin:
            return px.scatter(title="La fecha de inicio no puede ser mayor que la fecha final.")

        # Filtrar por rango de fechas
        df_filtrado = df_filtrado[(df_filtrado["fecha_unlock"] >= fecha_inicio) &
                                  (df_filtrado["fecha_unlock"] <= fecha_fin)]

    columnas_numericas = ["number_trips"]

    # Configurar los gráficos según la agrupación seleccionada
    if agrupacion == "hora":
        df_agrupado = df_filtrado.groupby("hora_unlock")[columnas_numericas].sum().reset_index()
        return px.line(
            df_agrupado,
            x="hora_unlock",
            y="number_trips",
            title="Viajes agrupados por hora",
            labels={"hora_unlock": "Hora", "number_trips": "Número de viajes"},
            color_discrete_sequence=["blue"]
        )
    elif agrupacion == "dia":
        df_filtrado["fecha_dia"] = df_filtrado["fecha_unlock"].dt.date
        df_agrupado = df_filtrado.groupby("fecha_dia")[columnas_numericas].sum().reset_index()
        return px.line(
            df_agrupado,
            x="fecha_dia",
            y="number_trips",
            title="Viajes agrupados por día",
            labels={"fecha_dia": "Día", "number_trips": "Número de viajes"},
            color_discrete_sequence=["red"]
        )
    elif agrupacion == "semana":
        df_filtrado["semana"] = df_filtrado["fecha_unlock"].dt.isocalendar().week
        df_agrupado = df_filtrado.groupby("semana")[columnas_numericas].sum().reset_index()
        return px.line(
            df_agrupado,
            x="semana",
            y="number_trips",
            title="Viajes agrupados por semana",
            labels={"semana": "Semana", "number_trips": "Número de viajes"},
            color_discrete_sequence=["green"]
        )
    elif agrupacion == "mes":
        df_filtrado["mes"] = df_filtrado["fecha_unlock"].dt.month
        df_agrupado = df_filtrado.groupby("mes")[columnas_numericas].sum().reset_index()
        fig = px.bar(
            df_agrupado,
            x="mes",
            y="number_trips",
            title="Viajes agrupados por mes",
            labels={"mes": "Mes", "number_trips": "Número de viajes"},
            color_discrete_sequence=["purple"]
        )
        fig.update_layout(
            bargap=0.2,
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                          "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            )
        )
        return fig
    elif agrupacion == "dia_hora":
        return px.line(
            df_filtrado,
            x="tiempo",
            y="number_trips",
            title="Viajes agrupados por Día y Hora",
            labels={"tiempo": "Día y Hora", "number_trips": "Número de viajes"},
            color_discrete_sequence=["blue"]
        )

    return px.scatter(title="Agrupación no reconocida.")

