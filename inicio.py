from dash import html
from components import header  # Importa el encabezado

def homepage():
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
                html.Section([
                    html.H2("Descubre Bicimad", style={"color": "#0044cc"}),
                    html.P("Bicimad es el sistema de bicicletas públicas de Madrid. Recorre la ciudad de forma rápida, cómoda y sostenible."),
                    html.A(
                        "¡Explorar estaciones!",
                        href="/estaciones",
                        style={
                            "backgroundColor": "#ff0000",
                            "color": "white",
                            "border": "none",
                            "padding": "10px 20px",
                            "cursor": "pointer",
                            "borderRadius": "5px",
                            "fontSize": "1rem",
                            "marginTop": "10px",
                            "textDecoration": "none"
                        }
                    )
                ])
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
            children=[
                html.P("© 2024 Bicimad Madrid")
            ]
        )
    ])
