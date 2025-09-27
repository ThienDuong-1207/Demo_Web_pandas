import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".txt", ".xls", ".xlsx"}


def _read_file_to_dataframe(file_path: str) -> pd.DataFrame:
    _, ext = os.path.splitext(file_path.lower())
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    if ext in {".csv", ".tsv", ".txt"}:
        sep = "," if ext == ".csv" else ("\t" if ext == ".tsv" else None)
        return pd.read_csv(file_path, sep=sep)
    else:
        return pd.read_excel(file_path)


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize column names: strip spaces, replace multiple spaces with underscore
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    # Try to parse datetimes where appropriate
    for col in df.columns:
        if df[col].dtype == object:
            # Heuristic: try parse datetime; errors='ignore'
            try:
                parsed = pd.to_datetime(df[col], errors="ignore", infer_datetime_format=True)
                # If conversion changed dtype, accept it
                if not isinstance(parsed.dtype, pd.core.dtypes.dtypes.DatetimeTZDtype):
                    if str(parsed.dtype).startswith("datetime64"):
                        df[col] = parsed
            except Exception:
                pass
    return df


def _infer_simple_dtype(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "number"
    # Consider low-cardinality objects as category
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_categorical_dtype(series):
        nunique = series.nunique(dropna=True)
        total = len(series)
        if total > 0 and nunique / max(total, 1) < 0.2:
            return "category"
        return "text"
    return "text"


def _build_metadata(df: pd.DataFrame) -> Dict:
    columns_meta = []
    for col in df.columns:
        try:
            dtype = _infer_simple_dtype(df[col])
        except Exception:
            dtype = "text"
        columns_meta.append({"name": col, "dtype": dtype})
    return {"columns": columns_meta, "row_count": int(len(df))}


def process_uploaded_file(file_path: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Clean and standardize uploaded data
    Returns: (Processed DataFrame, metadata dict)
    """
    df = _read_file_to_dataframe(file_path)
    df = _normalize_dataframe(df)
    meta = _build_metadata(df)
    return df, meta


