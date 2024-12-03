import pandas as pd
import plotly.graph_objects as go

def generar_mapa(df, predicciones):
    """
    Genera un mapa interactivo con etiquetas y colores basados en predicciones.

    Args:
        df (pd.DataFrame): DataFrame con columnas 'LATITUD', 'LONGITUD' y 'CP'.
        predicciones (dict): Diccionario con códigos postales como claves y predicciones como valores.

    Returns:
        go.Figure: Figura del mapa.
    """
    
    if df.empty:
        print("Error: DataFrame vacío")
        return go.Figure()

    # Mapear predicciones al DataFrame
    df['n_bicis'] = df['CP'].map(predicciones).fillna(0)

    # Calcular colores proporcionales
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
        mapbox_center={"lat": 40.416775, "lon": -3.703790},
        mapbox_zoom=10,
        height=800
    )

    return fig


