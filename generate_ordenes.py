"""Generate an interactive orders chart from SQL data."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text

from dataTransform import transformar_ordenes
from dbConnection import get_engine
from html_template import build_html


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
TABLE_NAME = "ordenes_del_punto_de_venta_pos_order_2"

# Columnas reales de la tabla:
# ref_de_la_orden, sesion, fecha, punto_de_venta, numero_de_recibo,
# cliente, responsable, total, estado, estado_de_la_factura
query_variable = (
    f"SELECT fecha, responsable, total FROM {TABLE_NAME}"
)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    engine = get_engine()
    try:
        dataframe = pd.read_sql(text(query_variable), con=engine)
    finally:
        engine.dispose()

    dataframe = transformar_ordenes(dataframe)

    # Asegura tipos correctos
    dataframe["fecha"] = pd.to_datetime(dataframe["fecha"], errors="coerce")
    dataframe["total"] = pd.to_numeric(dataframe["total"], errors="coerce")
    dataframe = dataframe.dropna(subset=["fecha", "total"])

    if dataframe.empty:
        raise ValueError("No hay órdenes válidas con fecha y total.")

    # Agrupamos por mes y por responsable (barras agrupadas)
    dataframe["mes"] = dataframe["fecha"].dt.to_period("M").dt.start_time
    grouped = (
        dataframe.groupby(["mes", "responsable"], as_index=False)["total"]
        .sum()
        .sort_values("mes")
    )

    responsables = sorted(grouped["responsable"].dropna().unique().tolist())
    meses = sorted(grouped["mes"].unique().tolist())
    meses_str = [pd.Timestamp(m).strftime("%Y-%m") for m in meses]

    palette = [
        "#58a6ff", "#d2a8ff", "#3fb950", "#f2cc60",
        "#ff9bce", "#d2a8ff", "#3fb950", "#f0883e",
        "#ff9bce", "#79c0ff", "#ff7b72", "#a5d6ff",
    ]

    figure = go.Figure()
    for idx, resp in enumerate(responsables):
        values = []
        for m in meses:
            row = grouped[(grouped["mes"] == m) & (grouped["responsable"] == resp)]
            values.append(float(row["total"].iloc[0]) if not row.empty else 0.0)

        figure.add_trace(
            go.Bar(
                x=meses_str,
                y=values,
                name=str(resp),
                marker_color=palette[idx % len(palette)],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "Mes: %{x}<br>"
                    "Importe: $%{y:,.2f} MXN<extra></extra>"
                ),
            )
        )

    total_facturado = float(dataframe["total"].sum())
    total_registros = int(len(dataframe))

    figure.update_layout(
        title="Importe Total Agrupado por Mes y Responsable",
        xaxis_title="Mes del Año",
        yaxis_title="Importe Total ($ MXN)",
        barmode="group",
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
            title=dict(text="Responsable"),
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
        "kpi1_label": "FACTURACIÓN TOTAL",
        "kpi1_valor": f"${total_facturado:,.2f} MXN",
        "kpi2_label": "REGISTROS EXTRAÍDOS",
        "kpi2_valor": f"{total_registros:,}",
    }

    html_final = build_html(
        titulo="Visualización de Órdenes",
        subtitulo="Datos alimentados directamente desde MySQL mediante SQLAlchemy",
        query_str=query_variable,
        kpis=kpis,
        plotly_div=plotly_div,
    )

    output_path = OUTPUT_DIR / "ordenes.html"
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html_final)

    print(f"Gráfica generada: {output_path}")


if __name__ == "__main__":
    main()