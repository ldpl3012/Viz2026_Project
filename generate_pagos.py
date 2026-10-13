"""Generate a payment chart with day/week/month/quarter aggregation controls."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text

from dataTransform import transformar_pagos
from dbConnection import get_engine
from html_template import build_html


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
TABLE_NAME = "pagos_en_punto_de_venta_pos_payment_1"

# Columnas reales de la tabla:
#   fecha, metodo_de_pago, orden, empleado, importe
# Renombramos metodo_de_pago a metodo_pago al vuelo para que el script
# no dependa de transformaciones extra.
query_variable = (
    f"SELECT importe, metodo_de_pago AS metodo_pago, fecha FROM {TABLE_NAME}"
)


def _period_pivot(dataframe, period):
    """Pivot importe by periodo and metodo_pago."""
    frame = dataframe.copy()
    frame["periodo"] = frame["fecha"].dt.to_period(period).dt.start_time
    pivot = frame.pivot_table(
        index="periodo",
        columns="metodo_pago",
        values="importe",
        aggfunc="sum",
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

    dataframe = transformar_pagos(dataframe)

    # Asegura tipos correctos
    dataframe["fecha"] = pd.to_datetime(dataframe["fecha"], errors="coerce")
    dataframe["importe"] = pd.to_numeric(dataframe["importe"], errors="coerce")
    dataframe["metodo_pago"] = dataframe["metodo_pago"].astype("string").str.strip()

    dataframe = dataframe.dropna(subset=["fecha", "importe", "metodo_pago"])

    # Filtro 2025-2026
    dataframe = dataframe[dataframe["fecha"].dt.year.between(2025, 2026)]

    if dataframe.empty:
        raise ValueError("No hay pagos válidos en el rango 2025-2026.")

    aggregations = [
        ("Día", "D"),
        ("Semana", "W"),
        ("Mes", "M"),
        ("Trimestre", "Q"),
    ]

    # Construye los pivotes para cada agregación
    pivots = [(label, _period_pivot(dataframe, period)) for label, period in aggregations]

    # Lista única de métodos de pago (columnas) ordenada
    methods = sorted(
        {str(method) for _, pivot in pivots for method in pivot.columns}
    )

    palette = [
        "#58a6ff", "#3fb950", "#f0883e", "#d2a8ff",
        "#ff7b72", "#79c0ff", "#f2cc60", "#ff9bce",
        "#a5d6ff", "#7ee787", "#ffa657", "#ffc9c9",
    ]

    # Trazas iniciales: usa el pivote "Día" para arrancar
    first_label, first_pivot = pivots[0]
    first_pivot = first_pivot.reindex(columns=methods, fill_value=0)
    x_values = first_pivot.index.strftime("%Y-%m-%d").tolist()

    figure = go.Figure()
    for idx, method in enumerate(methods):
        figure.add_trace(
            go.Bar(
                x=x_values,
                y=first_pivot[method].tolist(),
                name=str(method),
                marker_color=palette[idx % len(palette)],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "%{x}<br>"
                    "Importe: $%{y:,.2f} MXN<extra></extra>"
                ),
            )
        )

    # Botones para alternar agregación (Día/Semana/Mes/Trimestre)
    buttons = []
    for label, pivot in pivots:
        selected = pivot.reindex(columns=methods, fill_value=0)
        button_x = [selected.index.strftime("%Y-%m-%d").tolist()] * len(methods)
        button_y = [selected[method].tolist() for method in methods]
        buttons.append(
            {
                "label": label,
                "method": "update",
                "args": [
                    {"x": button_x, "y": button_y},
                    {"xaxis": {"title": label}},
                ],
            }
        )

    total_importe = float(dataframe["importe"].sum())
    total_registros = int(len(dataframe))

    figure.update_layout(
        title="Importe de Pagos por Método (2025-2026)",
        xaxis_title="Día",
        yaxis_title="Importe ($ MXN)",
        barmode="stack",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Poppins", color="#e6edf3"),
        margin=dict(l=60, r=30, t=60, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            title=dict(text="Método de pago"),
        ),
        xaxis=dict(gridcolor="#2a3038", tickfont=dict(color="#8b949e")),
        yaxis=dict(gridcolor="#2a3038", tickfont=dict(color="#8b949e")),
        updatemenus=[
            {
                "buttons": buttons,
                "direction": "down",
                "showactive": True,
                "x": 1,
                "xanchor": "right",
                "y": 1.15,
                "yanchor": "top",
                "bgcolor": "#1f2630",
                "bordercolor": "#2a3038",
                "font": {"color": "#e6edf3"},
            }
        ],
    )

    plotly_div = figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displayModeBar": False},
    )

    kpis = {
        "kpi1_label": "IMPORTE TOTAL 2025-2026",
        "kpi1_valor": f"${total_importe:,.2f} MXN",
        "kpi2_label": "REGISTROS EXTRAÍDOS",
        "kpi2_valor": f"{total_registros:,}",
    }

    html_final = build_html(
        titulo="Visualización de Pagos 2025-2026",
        subtitulo="Datos alimentados directamente desde MySQL mediante SQLAlchemy",
        query_str=query_variable,
        kpis=kpis,
        plotly_div=plotly_div,
    )

    output_path = OUTPUT_DIR / "pagos.html"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_final)

    print(f"Gráfica generada: {output_path}")


if __name__ == "__main__":
    main()