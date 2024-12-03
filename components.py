from dash import html

def header():
    """Encabezado común para todas las páginas."""
    return html.Header(
        style={
            "backgroundColor": "#0044cc",
            "color": "white",
            "padding": "1rem 0",
            "textAlign": "center"
        },
        children=[
            html.H1("Bicimad", style={"margin": "0", "fontSize": "2.5rem"}),
            html.Nav(
                html.Ul(
                    style={
                        "listStyle": "none",
                        "padding": "0",
                        "margin": "0.5rem 0 0",
                        "display": "flex",  # Alineación en una fila
                        "justifyContent": "center",
                        "gap": "20px"  # Espaciado entre elementos
                    },
                    children=[
                        html.Li(
                            html.A("Inicio", href="/",
                                   style={"color": "white", "textDecoration": "none", "fontSize": "1.1rem"})
                        ),
                        html.Li(
                            html.A("Estaciones", href="/estaciones",
                                   style={"color": "white", "textDecoration": "none", "fontSize": "1.1rem"})
                        ),
                        html.Li(
                            html.A("Predictor Abastecimiento", href="/predictor-bicis",
                                   style={"color": "white", "textDecoration": "none", "fontSize": "1.1rem"})
                        ),
                        html.Li(
                            html.A("Sobre Madrid", href="/sobre-madrid", 
                                   style={"color": "white", "textDecoration": "none", "fontSize": "1.1rem"})

                        ),
                        html.Li(
                            html.A("Sobre el clima de Madrid", href="/clima",
                                   style={"color": "white", "textDecoration": "none", "fontSize": "1.1rem"})
                        ),
                    ]
                )
            )
        ]
    )

