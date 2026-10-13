"""Load each .xlsx file from data/ into its own SQL table."""

import re
import unicodedata
from pathlib import Path

import pandas as pd

from dataTransform import (
    eliminar_duplicados,
    limpiar_columnas,
    transformar_ordenes,
    transformar_pagos,
)
from dbConnection import get_engine


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"


def nombre_tabla(filename):
    """Return an ASCII lowercase table name derived from an Excel filename."""
    stem = Path(filename).stem
    stem = unicodedata.normalize("NFKD", stem)
    stem = "".join(char for char in stem if not unicodedata.combining(char))
    return re.sub(r"[^0-9a-zA-Z]+", "_", stem.lower()).strip("_")


def transformar_archivo(filename, dataframe):
    normalized = nombre_tabla(filename)
    if "orden" in normalized or "order" in normalized:
        return transformar_ordenes(dataframe)
    if "pago" in normalized or "payment" in normalized:
        return transformar_pagos(dataframe)
    return eliminar_duplicados(limpiar_columnas(dataframe))


def main():
    if not DATA_DIR.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de datos: {DATA_DIR}")

    excel_files = sorted(DATA_DIR.glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError(f"No se encontraron archivos .xlsx en {DATA_DIR}")

    engine = get_engine()
    try:
        for file_path in excel_files:
            dataframe = pd.read_excel(file_path)
            transformed = transformar_archivo(file_path.name, dataframe)
            table_name = nombre_tabla(file_path.name)
            transformed.to_sql(
                table_name,
                con=engine,
                if_exists="replace",
                index=False,
            )
            print(
                f"Tabla '{table_name}' cargada desde '{file_path.name}' "
                f"({len(transformed)} filas)."
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
