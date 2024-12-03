from dash import html, dcc, Input, Output, callback
from components import header  # Importa el encabezado
from shared_data import ESTACIONES  # Contiene el diccionario de estaciones

def estaciones_page():
    return html.Div([
        header(),  # Usa el encabezado común
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
                html.H2("Listado de Estaciones", style={"color": "#0044cc"}),
                dcc.Input(
                    id="buscador",
                    placeholder="Buscar por distrito o código postal...",
                    type="text",
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "marginBottom": "20px",
                        "fontSize": "1rem",
                        "borderRadius": "5px",
                        "border": "1px solid #ccc"
                    }
                ),
                html.Div(
                    id="lista-estaciones",  # Div donde se renderizan las estaciones dinámicamente
                    children=[
                        html.A(
                            f"Código Postal {codigo}: {distrito}",
                            href=f"/estacion_seleccionada/{codigo}",
                            style={
                                "display": "block",
                                "width": "100%",
                                "padding": "10px",
                                "marginBottom": "10px",
                                "textAlign": "left",
                                "border": "1px solid #ccc",
                                "backgroundColor": "#f0f8ff",
                                "borderRadius": "5px",
                                "cursor": "pointer",
                                "textDecoration": "none",
                                "color": "#333"
                            }
                        ) for codigo, distrito in list(ESTACIONES.items())[:7]  # Mostramos solo las primeras 7 estaciones al inicio
                    ]
                )
            ]
        ),
        html.Footer(
            style={
                "textAlign": "center",
                "padding": "1rem 0",
                "backgroundColor": "#0044cc",
                "color": "white",
                "fontSize": "0.9rem"
            },
            children=["© 2024 Bicimad Madrid"]
        )
    ])

# Callback para actualizar dinámicamente la lista de estaciones según la búsqueda
@callback(
    Output("lista-estaciones", "children"),  # Actualiza las estaciones mostradas
    Input("buscador", "value")  # Escucha cambios en el campo de búsqueda
)
def actualizar_estaciones(busqueda):
    if not busqueda:
        # Si no hay búsqueda, mostramos las primeras 7 estaciones
        estaciones_filtradas = list(ESTACIONES.items())[:7]
    else:
        # Filtrar las estaciones según el texto ingresado en el buscador
        estaciones_filtradas = [
            (codigo, distrito) for codigo, distrito in ESTACIONES.items()
            if busqueda.lower() in str(codigo) or busqueda.lower() in distrito.lower()
        ][:7]  # Limitar a 7 resultados

    # Generar los enlaces de las estaciones filtradas
    return [
        html.A(
            f"Código Postal {codigo}: {distrito}",
            href=f"/estacion_seleccionada/{codigo}",
            style={
                "display": "block",
                "width": "100%",
                "padding": "10px",
                "marginBottom": "10px",
                "textAlign": "left",
                "border": "1px solid #ccc",
                "backgroundColor": "#f0f8ff",
                "borderRadius": "5px",
                "cursor": "pointer",
                "textDecoration": "none",
                "color": "#333"
            }
        ) for codigo, distrito in estaciones_filtradas
    ]
