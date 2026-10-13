"""Generate a sessions chart with average session duration per week per user."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text

from dataTransform import transformar_sesiones
from dbConnection import get_engine
from html_template import build_html


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"

# Nombre real de la tabla en MySQL
TABLE_NAME = "sesion_de_punto_de_venta_pos_session"

query_variable = (
    f"SELECT abierta_por, fecha_de_apertura, fecha_de_cierre "
    f"FROM {TABLE_NAME} "
    f"WHERE fecha_de_cierre IS NOT NULL"
)


def _prepare_dataframe(dataframe):
    """Convert date columns, compute duration in minutes, drop invalid rows."""
    dataframe = transformar_sesiones(dataframe)

    dataframe["fecha_de_apertura"] = pd.to_datetime(
        dataframe["fecha_de_apertura"], errors="coerce"
    )
    dataframe["fecha_de_cierre"] = pd.to_datetime(
        dataframe["fecha_de_cierre"], errors="coerce"
    )

    dataframe = dataframe.dropna(
        subset=["fecha_de_apertura", "fecha_de_cierre", "abierta_por"]
    )

    dataframe["duracion_min"] = (
        dataframe["fecha_de_cierre"] - dataframe["fecha_de_apertura"]
    ).dt.total_seconds() / 60.0

    dataframe = dataframe[
        (dataframe["duracion_min"] > 0) & (dataframe["duracion_min"] <= 24 * 60)
    ]

    dataframe["semana"] = (
        dataframe["fecha_de_apertura"].dt.to_period("W").dt.start_time
    )

    return dataframe


def _build_pivot(dataframe):
    pivot = dataframe.pivot_table(
        index="semana",
        columns="abierta_por",
        values="duracion_min",
        aggfunc="mean",
        fill_value=0,
    ).sort_index()
    return pivot


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    engine = get_engine()
    try:
        dataframe = pd.read_sql(text(query_variable), con=engine)
    finally:
        engine.dispose()

    dataframe = _prepare_dataframe(dataframe)

    if dataframe.empty:
        raise ValueError(
            "No hay sesiones válidas con fecha de apertura y cierre para calcular duraciones."
        )

    pivot = _build_pivot(dataframe)
    users = list(pivot.columns.astype(str))
    weeks = pivot.index.strftime("%Y-%m-%d").tolist()

    palette = [
        "#58a6ff", "#3fb950", "#f0883e", "#d2a8ff",
        "#ff7b72", "#79c0ff", "#f2cc60", "#ff9bce",
        "#a5d6ff", "#7ee787", "#ffa657", "#ffc9c9",
    ]

    figure = go.Figure()
    for idx, user in enumerate(users):
        figure.add_trace(
            go.Bar(
                x=weeks,
                y=pivot[user].tolist(),
                name=user,
                marker_color=palette[idx % len(palette)],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Semana: %{x}<br>"
                    "Duración promedio: %{y:.1f} min<extra></extra>"
                ),
            )
        )

    avg_duration = dataframe["duracion_min"].mean()
    total_sessions = len(dataframe)

    figure.update_layout(
        title="Duración promedio de sesiones por semana y usuario",
        xaxis_title="Semana (inicio)",
        yaxis_title="Duración promedio (min)",
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Poppins", color="#e6edf3"),
        margin=dict(l=60, r=30, t=60, b=80),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            title=dict(text="Usuario"),
        ),
        xaxis=dict(gridcolor="#2a3038", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#2a3038", tickfont=dict(color="#8b949e")),
    )

    plotly_div = figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False},
    )

    kpis = {
        "kpi1_label": "DURACIÓN PROMEDIO",
        "kpi1_valor": f"{avg_duration:,.1f} min",
        "kpi2_label": "SESIONES ANALIZADAS",
        "kpi2_valor": f"{total_sessions:,}",
    }

    html_final = build_html(
        titulo="Visualización de Sesiones",
        subtitulo="Duración promedio por semana y usuario — datos desde MySQL vía SQLAlchemy",
        query_str=query_variable,
        kpis=kpis,
        plotly_div=plotly_div,
    )

    output_path = OUTPUT_DIR / "sesiones.html"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_final)

    print(f"Gráfica generada: {output_path}")


if __name__ == "__main__":
    main()