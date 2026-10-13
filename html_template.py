"""Reusable HTML template with dark dashboard styling for all Viz2026 charts."""

from html import escape


def build_html(
    titulo: str,
    subtitulo: str,
    query_str: str,
    kpis: dict,
    plotly_div: str,
    badge_texto: str = "BASE DE DATOS MYSQL: VIZ2026 • REPORTE SQL",
) -> str:
    """
    Build the full HTML page for a Viz2026 chart.

    Parameters
    ----------
    titulo : str
        Big title at the top of the page.
    subtitulo : str
        Subtitle under the main title.
    query_str : str
        The query_variable content shown in the query box.
    kpis : dict
        Must contain keys: kpi1_label, kpi1_valor, kpi2_label, kpi2_valor.
    plotly_div : str
        The <div> returned by fig.to_html(full_html=False).
    badge_texto : str
        Text shown in the top badge.

    Returns
    -------
    str
        Complete HTML as a string.
    """

    kpi1_label = escape(str(kpis.get("kpi1_label", "")))
    kpi1_valor = escape(str(kpis.get("kpi1_valor", "")))
    kpi2_label = escape(str(kpis.get("kpi2_label", "")))
    kpi2_valor = escape(str(kpis.get("kpi2_valor", "")))
    query_safe = escape(query_str)
    badge_safe = escape(badge_texto)
    titulo_safe = escape(titulo)
    subtitulo_safe = escape(subtitulo)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{titulo_safe}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Fira+Code&display=swap"
        rel="stylesheet"
    />
    <style>
        /* ---------- Base ---------- */
        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 24px;
            background: #0e1117;
            color: #e6edf3;
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 15px;
            line-height: 1.5;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* ---------- Cards ---------- */
        .card {{
            background: #161b22;
            border: 1px solid #2a3038;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}

        /* ---------- Header ---------- */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #0d1f17;
            border: 1px solid #1f6f3f;
            color: #3fb950;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: 999px;
            margin-bottom: 20px;
        }}

        .badge .dot {{
            width: 8px;
            height: 8px;
            background: #3fb950;
            border-radius: 50%;
            display: inline-block;
        }}

        .header {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-start;
            gap: 24px;
        }}

        .header-left {{
            flex: 1 1 400px;
        }}

        .header h1 {{
            font-size: 36px;
            font-weight: 700;
            margin: 0 0 8px 0;
            color: #e6edf3;
            line-height: 1.2;
        }}

        .header .subtitulo {{
            color: #8b949e;
            font-size: 15px;
            margin: 0;
        }}

        .kpis {{
            display: flex;
            gap: 32px;
            align-items: flex-start;
        }}

        .kpi {{
            display: flex;
            flex-direction: column;
            min-width: 180px;
        }}

        .kpi + .kpi {{
            border-left: 1px solid #2a3038;
            padding-left: 32px;
        }}

        .kpi-label {{
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #8b949e;
            margin-bottom: 6px;
        }}

        .kpi-valor {{
            font-size: 28px;
            font-weight: 700;
            color: #58a6ff;
        }}

        .kpi:last-child .kpi-valor {{
            color: #e6edf3;
        }}

        /* ---------- Query box ---------- */
        .query-box {{
            border-left: 4px solid #58a6ff;
            background: #161b22;
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 24px;
        }}

        .query-label {{
            color: #8b949e;
            font-size: 12px;
            margin-bottom: 8px;
        }}

        .query-code {{
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 13px;
            color: #58a6ff;
            background: #0d1117;
            padding: 12px 16px;
            border-radius: 6px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-word;
            margin: 0;
        }}

        /* ---------- Chart card ---------- */
        .chart-title {{
            font-size: 18px;
            font-weight: 600;
            color: #e6edf3;
            margin: 0 0 16px 0;
        }}

        .chart-wrapper {{
            width: 100%;
        }}

        /* ---------- Plotly dark override ---------- */
        .js-plotly-plot .plotly .modebar {{
            background: transparent !important;
        }}

        .updatemenu-button {{
            background-color: #1f2630 !important;
            border: 1px solid #2a3038 !important;
            color: #e6edf3 !important;
            border-radius: 8px !important;
        }}

        .updatemenu-button:hover {{
            background-color: #262c37 !important;
        }}
    </style>
</head>
<body>
    <div class="container">

        <!-- Header card -->
        <div class="card">
            <div class="badge">
                <span class="dot"></span>
                <span>{badge_safe}</span>
            </div>
            <div class="header">
                <div class="header-left">
                    <h1>{titulo_safe}</h1>
                    <p class="subtitulo">{subtitulo_safe}</p>
                </div>
                <div class="kpis">
                    <div class="kpi">
                        <span class="kpi-label">{kpi1_label}</span>
                        <span class="kpi-valor">{kpi1_valor}</span>
                    </div>
                    <div class="kpi">
                        <span class="kpi-label">{kpi2_label}</span>
                        <span class="kpi-valor">{kpi2_valor}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Query card -->
        <div class="query-box">
            <div class="query-label">Variable de Consulta Utilizada:</div>
            <pre class="query-code">query_variable = "{query_safe}"</pre>
        </div>

        <!-- Chart card -->
        <div class="card">
            <div class="chart-wrapper">
                {plotly_div}
            </div>
        </div>

    </div>
</body>
</html>
"""