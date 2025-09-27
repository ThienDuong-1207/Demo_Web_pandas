from typing import List, Dict

import pandas as pd


def _to_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", infer_datetime_format=True)


def _choose_freq_from_span(dates: pd.Series, default: str = "M") -> str:
    dates = pd.to_datetime(dates, errors="coerce").dropna()
    if dates.empty:
        return default
    span_days = (dates.max() - dates.min()).days or 1
    if span_days > 730:
        return "Q"
    if span_days > 365:
        return "M"
    if span_days > 90:
        return "W"
    return "D"


def chart_revenue_over_time(df: pd.DataFrame, freq: str | None = None) -> List[Dict]:
    df = df.copy()
    df["Date"] = _to_datetime(df["Date"])  # type: ignore
    df = df.dropna(subset=["Date", "Total Amount"])  # type: ignore
    f = freq or _choose_freq_from_span(df["Date"])  # type: ignore
    result = (
        df.resample(f, on="Date")["Total Amount"]  # type: ignore
        .sum()
        .reset_index()
        .rename(columns={"Total Amount": "Revenue"})
    )
    return result.to_dict(orient="records")


def chart_revenue_by_category(df: pd.DataFrame, top_k: int = 10) -> List[Dict]:
    result = (
        df.groupby("Product Category")["Total Amount"]  # type: ignore
        .sum()
        .reset_index()
        .sort_values("Total Amount", ascending=False)
    )
    if len(result) > top_k:
        top = result.head(top_k)
        others = pd.DataFrame([
            {"Product Category": "Others", "Total Amount": result["Total Amount"].iloc[top_k:].sum()}  # type: ignore
        ])
        result = pd.concat([top, others], ignore_index=True)
    result = result.rename(columns={"Total Amount": "Revenue"})
    return result.to_dict(orient="records")


def chart_revenue_by_gender(df: pd.DataFrame) -> List[Dict]:
    result = (
        df.groupby("Gender")["Total Amount"]  # type: ignore
        .sum()
        .reset_index()
        .rename(columns={"Total Amount": "Revenue"})
    )
    return result.to_dict(orient="records")


def chart_age_distribution(df: pd.DataFrame, bins: int = 10) -> List[Dict]:
    series = df["Age"].dropna()  # type: ignore
    cats, edges = pd.cut(series, bins=bins, retbins=True)
    result = (
        series.groupby(cats)
        .size()
        .reset_index(name="Count")
        .rename(columns={"Age": "Age Bin"})
    )
    result["Age Bin"] = result["Age"].astype(str) if "Age" in result.columns else result["Age Bin"].astype(str)
    return result[[result.columns[0], "Count"]].rename(columns={result.columns[0]: "Age Bin"}).to_dict(orient="records")


def chart_quantity_vs_revenue(df: pd.DataFrame, sample: int = 500) -> List[Dict]:
    sample_df = df[["Quantity", "Total Amount"]].dropna()  # type: ignore
    if len(sample_df) > sample:
        sample_df = sample_df.sample(n=sample, random_state=42)
    return sample_df.to_dict(orient="records")


