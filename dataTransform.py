"""Reusable DataFrame transformations for imported spreadsheet data."""

import re
import unicodedata

import pandas as pd


def _normalize_name(value):
    value = unicodedata.normalize("NFKD", str(value))
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^0-9a-zA-Z]+", "_", value.strip().lower())
    return value.strip("_")


def limpiar_columnas(df):
    """Normalize column names to lowercase ASCII snake_case."""
    result = df.copy()
    result.columns = [_normalize_name(column) for column in result.columns]
    return result


def convertir_fechas(df, columnas):
    """Convert the named columns to pandas datetime values when present."""
    result = df.copy()
    for column in columnas:
        if column in result.columns:
            result[column] = pd.to_datetime(result[column], errors="coerce")
    return result


def eliminar_duplicados(df):
    """Remove fully duplicated rows."""
    return df.drop_duplicates().copy()


def convertir_numericos(df, columnas):
    """Convert the named columns to numeric values when present."""
    result = df.copy()
    for column in columnas:
        if column in result.columns:
            values = result[column]
            if values.dtype == object or pd.api.types.is_string_dtype(values):
                values = values.astype("string").str.replace(
                    r"[^\d,.\-]", "", regex=True
                )
                has_comma = values.str.contains(",", na=False)
                has_dot = values.str.contains(r"\.", na=False)
                has_both_separators = has_comma & has_dot
                european_decimal = (
                    has_both_separators
                    & (values.str.rfind(",") > values.str.rfind("."))
                ).fillna(False)
                us_decimal = (
                    has_both_separators
                    & (values.str.rfind(".") > values.str.rfind(","))
                ).fillna(False)
                comma_only = (has_comma & ~has_dot).fillna(False)
                trailing_digits = values.str.len() - values.str.rfind(",") - 1
                comma_thousands = (
                    comma_only
                    & (
                        (values.str.count(",") > 1)
                        | (trailing_digits == 3)
                    )
                ).fillna(False)
                comma_decimal = comma_only & ~comma_thousands
                values.loc[european_decimal] = (
                    values.loc[european_decimal]
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                )
                values.loc[us_decimal | comma_thousands] = values.loc[
                    us_decimal | comma_thousands
                ].str.replace(
                    ",", "", regex=False
                )
                values.loc[comma_decimal] = values.loc[comma_decimal].str.replace(
                    ",", ".", regex=False
                )
            result[column] = pd.to_numeric(values, errors="coerce")
    return result


def _columns_matching(columns, fragments):
    return [
        column
        for column in columns
        if any(fragment in column for fragment in fragments)
    ]


def _copy_first_available(df, target, candidates):
    if target in df.columns:
        return df
    for column in candidates:
        if column in df.columns:
            df[target] = df[column]
            break
    return df


def transformar_ordenes(df):
    """Normalize order data, dates, numeric fields, and duplicate rows."""
    result = limpiar_columnas(df)
    date_columns = _columns_matching(
        result.columns, ("fecha", "date", "time", "datetime")
    )
    numeric_columns = _columns_matching(
        result.columns,
        ("importe", "amount", "total", "precio", "price", "cantidad", "qty"),
    )
    result = convertir_fechas(result, date_columns)
    result = convertir_numericos(result, numeric_columns)
    return eliminar_duplicados(result)


def transformar_pagos(df):
    """Normalize payment data and add canonical importe/metodo_pago/fecha fields."""
    result = limpiar_columnas(df)
    result = _copy_first_available(
        result,
        "importe",
        (
            "importe",
            "amount",
            "payment_amount",
            "amount_paid",
            "total",
        ),
    )
    result = _copy_first_available(
        result,
        "metodo_pago",
        (
            "metodo_de_pago",     # ← columna real del xlsx
            "metodo_pago",
            "payment_method",
            "payment_method_id",
            "method",
            "journal_id",
        ),
    )
    result = _copy_first_available(
        result,
        "fecha",
        (
            "fecha",
            "payment_date",
            "date",
            "create_date",
            "write_date",
        ),
    )
    date_columns = _columns_matching(
        result.columns, ("fecha", "date", "time", "datetime")
    )
    numeric_columns = _columns_matching(
        result.columns, ("importe", "amount", "total", "price")
    )
    result = convertir_fechas(result, date_columns)
    result = convertir_numericos(result, numeric_columns)
    if "metodo_pago" in result.columns:
        result["metodo_pago"] = (
            result["metodo_pago"].astype("string").str.strip()
        )
    return eliminar_duplicados(result)

def transformar_sesiones(df):
    """Normalize session data: clean column names and convert dates."""
    result = limpiar_columnas(df)
    date_columns = _columns_matching(
        result.columns, ("fecha", "date", "time", "datetime")
    )
    numeric_columns = _columns_matching(
        result.columns, ("balance", "importe", "amount")
    )
    result = convertir_fechas(result, date_columns)
    result = convertir_numericos(result, numeric_columns)
    return eliminar_duplicados(result)