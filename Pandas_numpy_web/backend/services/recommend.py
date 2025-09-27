from typing import Any, Dict, List

import pandas as pd

from .adapters.plotly_adapter import (
    build_bar_config,
    build_line_config,
    build_hist_config,
    build_bar_count_config,
    build_line_multi_config,
    build_box_config,
    build_pie_config,
    build_bar_bin_numeric_config,
)


def _dtype_of(meta: Dict, col: str) -> str:
    for c in meta.get("columns", []):
        if c.get("name") == col:
            return c.get("dtype", "text")
    return "text"


def _ensure_datetime(series: pd.Series) -> pd.Series:
    if not pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors="coerce", infer_datetime_format=True)
    return series


def _choose_freq(dt_series: pd.Series) -> str:
    dt_series = pd.to_datetime(dt_series, errors="coerce")
    dt_series = dt_series.dropna()
    if dt_series.empty:
        return "D"
    span_days = (dt_series.max() - dt_series.min()).days or 1
    if span_days > 730:
        return "Q"
    if span_days > 365:
        return "M"
    if span_days > 90:
        return "W"
    return "D"


def _aggregate_time_measure(df: pd.DataFrame, time_col: str, measure: str, agg: str = "sum") -> pd.DataFrame:
    dfx = df[[time_col, measure]].dropna().copy()
    dfx[time_col] = _ensure_datetime(dfx[time_col])
    freq = _choose_freq(dfx[time_col])
    out = (
        dfx.set_index(time_col)[measure]
        .resample(freq)
        .agg(agg)
        .fillna(0)
        .reset_index()
    )
    return out


def _aggregate_time_cat_measure(df: pd.DataFrame, time_col: str, category: str, measure: str, agg: str = "sum") -> pd.DataFrame:
    dfx = df[[time_col, category, measure]].dropna().copy()
    dfx[time_col] = _ensure_datetime(dfx[time_col])
    freq = _choose_freq(dfx[time_col])
    out = (
        dfx.groupby([pd.Grouper(key=time_col, freq=freq), category])[measure]
        .agg(agg)
        .reset_index()
    )
    return out


def _rule_based_suggestions(df: pd.DataFrame, meta: Dict, selected: List[str]) -> List[Dict[str, Any]]:
    suggestions: List[Dict[str, Any]] = []

    # Sort selected to have deterministic output
    selected = [c for c in selected if c in df.columns]

    if len(selected) == 2:
        a, b = selected
        ta, tb = _dtype_of(meta, a), _dtype_of(meta, b)
        title_suffix = f"{a} vs {b}"

        # Scatter removed
        if (ta == "datetime" and tb == "number") or (tb == "datetime" and ta == "number"):
            time_col = a if ta == "datetime" else b
            measure = b if ta == "datetime" else a
            agg_df = _aggregate_time_measure(df, time_col, measure, agg="sum")
            suggestions.append(
                {
                    "id": f"sg_line_{time_col}_{measure}",
                    "type": "line",
                    "title": f"Sum of {measure} over {time_col}",
                    "library": "plotly",
                    "config": build_line_config(agg_df, x=time_col, y=measure),
                }
            )
        if (ta == "category" and tb == "number") or (tb == "category" and ta == "number"):
            cat = a if ta == "category" else b
            num = b if ta == "category" else a
            suggestions.append(
                {
                    "id": f"sg_bar_{cat}_{num}",
                    "type": "bar",
                    "title": f"{num} by {cat}",
                    "library": "plotly",
                    "config": build_bar_config(df, category=cat, value=num, agg="sum"),
                }
            )
        # Heatmap removed

    # time + category + (optional) measure
    if len(selected) == 2:
        a, b = selected
        ta, tb = _dtype_of(meta, a), _dtype_of(meta, b)
        if (ta == "datetime" and tb == "category") or (tb == "datetime" and ta == "category"):
            time_col = a if ta == "datetime" else b
            cat = b if ta == "datetime" else a
            # default to count over time by category
            dfx = df[[time_col, cat]].dropna().copy()
            dfx[time_col] = _ensure_datetime(dfx[time_col])
            freq = _choose_freq(dfx[time_col])
            count_df = (
                dfx.assign(_count=1)
                .groupby([pd.Grouper(key=time_col, freq=freq), cat])["_count"]
                .sum()
                .reset_index()
                .rename(columns={"_count": "count"})
            )
            suggestions.append(
                {
                    "id": f"sg_line_multi_count_{time_col}_{cat}",
                    "type": "line",
                    "title": f"Count over {time_col} by {cat}",
                    "library": "plotly",
                    "config": build_line_multi_config(count_df, time_col, "count", cat),
                }
            )

    if len(selected) == 3:
        cols = selected
        types = [_dtype_of(meta, c) for c in cols]
        if "datetime" in types and "number" in types and "category" in types:
            time_col = cols[types.index("datetime")]
            measure = cols[types.index("number")]
            cat = cols[types.index("category")]
            agg_df = _aggregate_time_cat_measure(df, time_col, cat, measure, agg="sum")
            suggestions.append({
                "id": f"sg_line_multi_{time_col}_{measure}_{cat}",
                "type": "line",
                "title": f"Sum of {measure} over {time_col} by {cat}",
                "library": "plotly",
                "config": build_line_multi_config(agg_df, time_col, measure, cat),
            })

    # 3 columns logic (Retail targets)
    if len(selected) == 3:
        cols = selected
        types = [_dtype_of(meta, c) for c in cols]
        if "datetime" in types and "number" in types and "category" in types:
            x = cols[types.index("datetime")]
            y = cols[types.index("number")]
            color = cols[types.index("category")]
            suggestions.append({
                "id": f"sg_line_multi_{x}_{y}_{color}",
                "type": "line",
                "title": f"{y} over {x} by {color}",
                "library": "plotly",
                "config": build_line_multi_config(df, x, y, color),
            })
        # 3 numeric scatter removed

    # Correlation heatmap removed

    # Single column selections: suggest histogram/box for numeric, count bar/pie for category
    if len(selected) == 1:
        col = selected[0]
        t = _dtype_of(meta, col)
        if t == "number":
            suggestions.append(
                {
                    "id": f"sg_hist_{col}",
                    "type": "histogram",
                    "title": f"Distribution of {col}",
                    "library": "plotly",
                    "config": build_hist_config(df, col),
                }
            )
            suggestions.append(
                {
                    "id": f"sg_box_{col}",
                    "type": "box",
                    "title": f"Box of {col}",
                    "library": "plotly",
                    "config": build_box_config(df, col),
                }
            )
        if t == "category":
            suggestions.append(
                {
                    "id": f"sg_count_{col}",
                    "type": "bar",
                    "title": f"Top {col}",
                    "library": "plotly",
                    "config": build_bar_count_config(df, col),
                }
            )
            # Also a pie (e.g., Gender share)
            num_candidates = [c for c in df.columns if _dtype_of(meta, c) == "number"]
            if num_candidates:
                val = num_candidates[0]
                suggestions.append(
                    {
                        "id": f"sg_pie_{col}_{val}",
                        "type": "pie",
                        "title": f"{val} share by {col}",
                        "library": "plotly",
                        "config": build_pie_config(df, col, val),
                    }
                )

    return suggestions


def get_chart_recommendations(df: pd.DataFrame, meta: Dict, selected_columns: List[str], limit: int = 5) -> List[Dict[str, Any]]:
    """
    Use rule-based logic primarily; optionally augment with Lux if available
    Returns: List of chart configurations with type and settings
    """
    suggestions = _rule_based_suggestions(df, meta, selected_columns)

    # Optional: try Lux to add ideas
    try:
        import lux  # type: ignore

        # Attach Lux to df
        _ = df  # no-op; Lux integrates via accessor when imported
        # Note: For simplicity we skip deep Lux programmatic API here
        # and rely on rule-based suggestions primarily
    except Exception:
        pass

    # Deduplicate by id and limit
    seen = set()
    unique: List[Dict[str, Any]] = []
    for s in suggestions:
        if s["id"] in seen:
            continue
        seen.add(s["id"])
        unique.append(s)
        if len(unique) >= limit:
            break
    return unique


def create_chart_from_spec(df: pd.DataFrame, meta: Dict, spec: Dict[str, Any]) -> Dict[str, Any]:
    ctype = spec.get("type")
    if ctype == "bar":
        return {
            "chart_id": f"c_bar_{spec.get('category')}_{spec.get('value')}",
            "library": "plotly",
            "config": build_bar_config(
                df,
                category=spec["category"],
                value=spec["value"],
                agg=spec.get("agg", "sum"),
                color=spec.get("color"),
            ),
        }
    if ctype == "line":
        return {
            "chart_id": f"c_line_{spec.get('x')}_{spec.get('y')}",
            "library": "plotly",
            "config": build_line_config(df, x=spec["x"], y=spec["y"]),
        }
    # scatter and heatmap removed
    return {"error": f"Unsupported chart type: {ctype}"}


