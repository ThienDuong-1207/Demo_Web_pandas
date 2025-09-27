from typing import Any, Dict, Optional

import pandas as pd


def _dark_layout(title: str, x_title: Optional[str] = None, y_title: Optional[str] = None) -> Dict[str, Any]:
    return {
        "title": title,
        "paper_bgcolor": "#000000",
        "plot_bgcolor": "#000000",
        "font": {"color": "#ffffff"},
        "xaxis": {"gridcolor": "#333333", "title": {"text": x_title} if x_title else {}, "automargin": True},
        "yaxis": {"gridcolor": "#333333", "title": {"text": y_title} if y_title else {}, "automargin": True},
        "margin": {"l": 50, "r": 30, "t": 50, "b": 50},
        "showlegend": True,
    }


def build_bar_config(
    df: pd.DataFrame,
    category: str,
    value: str,
    agg: str = "sum",
    title: Optional[str] = None,
    color: Optional[str] = None,
) -> Dict[str, Any]:
    if color and color in df.columns:
        grouped = (
            df[[category, value, color]]
            .dropna()
            .groupby([category, color])[value]
            .agg(agg)
            .reset_index()
        )
        # Pivot to series per color for multiple legend entries
        pivot = grouped.pivot(index=category, columns=color, values=value).fillna(0)
        x_vals = pivot.index.astype(str).tolist()
        traces: list[Dict[str, Any]] = []
        palette = [
            "#3b82f6", "#22c55e", "#ef4444", "#a78bfa", "#f59e0b",
            "#10b981", "#eab308", "#8b5cf6", "#06b6d4", "#f97316",
        ]
        for idx, series_name in enumerate(pivot.columns.tolist()):
            traces.append({
                "type": "bar",
                "x": x_vals,
                "y": pivot[series_name].tolist(),
                "name": str(series_name),
                "marker": {"color": palette[idx % len(palette)]},
            })
        return {"data": traces, "layout": _dark_layout(title or f"{value} by {category}", x_title=category, y_title=f"{agg}({value})")}
    else:
        grouped = (
            df[[category, value]]
            .dropna()
            .groupby(category)[value]
            .agg(agg)
            .reset_index()
            .sort_values(value, ascending=False)
            .head(50)
        )
        x = grouped[category].astype(str).tolist()
        y = grouped[value].tolist()
        return {
            "data": [
                {
                    "type": "bar",
                    "x": x,
                    "y": y,
                    "name": value,
                    "marker": {"color": "#3b82f6"},
                }
            ],
            "layout": _dark_layout(title or f"{value} by {category}", x_title=category, y_title=f"{agg}({value})"),
        }


def build_line_config(df: pd.DataFrame, x: str, y: str, title: Optional[str] = None) -> Dict[str, Any]:
    dfx = df[[x, y]].dropna().sort_values(x).head(5000)
    return {
        "data": [
            {
                "type": "scatter",
                "mode": "lines",
                "x": dfx[x].astype(str).tolist(),
                "y": dfx[y].tolist(),
                "name": y,
                "line": {"color": "#22c55e"},
            }
        ],
        "layout": _dark_layout(title or f"{y} over {x}", x_title=x, y_title=y),
    }


def build_scatter_config(
    df: pd.DataFrame, x: str, y: str, color: Optional[str] = None, title: Optional[str] = None
) -> Dict[str, Any]:
    dfx = df[[x, y] + ([color] if color else [])].dropna().head(5000)
    if color and color in dfx.columns:
        # Multiple traces per category value for legend
        top_vals = dfx[color].astype(str).value_counts().head(10).index.tolist()
        palette = [
            "#f59e0b", "#3b82f6", "#22c55e", "#ef4444", "#a78bfa",
            "#10b981", "#eab308", "#8b5cf6", "#06b6d4", "#f97316",
        ]
        traces: list[Dict[str, Any]] = []
        for idx, val in enumerate(top_vals):
            sub = dfx[dfx[color].astype(str) == val]
            traces.append({
                "type": "scatter",
                "mode": "markers",
                "x": sub[x].tolist(),
                "y": sub[y].tolist(),
                "name": str(val),
                "marker": {"color": palette[idx % len(palette)]},
            })
        return {"data": traces, "layout": _dark_layout(title or f"{y} vs {x}", x_title=x, y_title=y)}
    else:
        trace: Dict[str, Any] = {
            "type": "scatter",
            "mode": "markers",
            "x": dfx[x].tolist(),
            "y": dfx[y].tolist(),
            "name": y,
            "marker": {"color": "#f59e0b"},
        }
        return {"data": [trace], "layout": _dark_layout(title or f"{y} vs {x}", x_title=x, y_title=y)}


def build_heatmap_config(
    df: pd.DataFrame, x: str, y: str, value_col: Optional[str] = None, title: Optional[str] = None
) -> Dict[str, Any]:
    if value_col is None:
        pivot = (
            df[[x, y]]
            .assign(_count=1)
            .groupby([x, y])
            ["_count"]
            .sum()
            .reset_index()
            .pivot(index=y, columns=x, values="_count")
            .fillna(0)
        )
    else:
        pivot = (
            df[[x, y, value_col]]
            .groupby([x, y])[value_col]
            .mean()
            .reset_index()
            .pivot(index=y, columns=x, values=value_col)
            .fillna(0)
        )

    z = pivot.values.tolist()
    x_vals = [str(v) for v in list(pivot.columns)]
    y_vals = [str(v) for v in list(pivot.index)]

    return {
        "data": [
            {
                "type": "heatmap",
                "z": z,
                "x": x_vals,
                "y": y_vals,
                "colorscale": "Viridis",
            }
        ],
        "layout": _dark_layout(title or "Heatmap", x_title=x, y_title=y),
    }


def build_hist_config(df: pd.DataFrame, col: str, bins: int = 30, title: Optional[str] = None) -> Dict[str, Any]:
    series = df[col].dropna().astype(float).tolist()
    return {
        "data": [
            {
                "type": "histogram",
                "x": series,
                "nbinsx": bins,
                "name": col,
                "marker": {"color": "#a78bfa"}
            }
        ],
        "layout": _dark_layout(title or f"Distribution of {col}", x_title=col, y_title="count"),
    }


def build_bar_count_config(df: pd.DataFrame, category: str, topk: int = 30, title: Optional[str] = None) -> Dict[str, Any]:
    counts = (
        df[category]
        .astype(str)
        .dropna()
        .value_counts()
        .reset_index()
        .rename(columns={"index": category, category: "count"})
        .head(topk)
    )
    x = counts[category].tolist()
    y = counts["count"].tolist()
    return {
        "data": [
            {
                "type": "bar",
                "x": x,
                "y": y,
                "marker": {"color": "#ef4444"}
            }
        ],
        "layout": _dark_layout(title or f"Top {topk} {category}", x_title=category, y_title="count"),
    }


def build_pie_config(
    df: pd.DataFrame, category: str, value: str, agg: str = "sum", title: Optional[str] = None
) -> Dict[str, Any]:
    grouped = (
        df[[category, value]]
        .dropna()
        .groupby(category)[value]
        .agg(agg)
        .reset_index()
        .sort_values(value, ascending=False)
        .head(20)
    )
    labels = grouped[category].astype(str).tolist()
    vals = grouped[value].tolist()
    return {
        "data": [
            {
                "type": "pie",
                "labels": labels,
                "values": vals,
                "textinfo": "label+percent",
                "hole": 0,
            }
        ],
        "layout": _dark_layout(title or f"{value} share by {category}"),
    }


def build_bar_bin_numeric_config(
    df: pd.DataFrame, numeric_col: str, value: str, bins: int = 10, agg: str = "sum", title: Optional[str] = None
) -> Dict[str, Any]:
    dfx = df[[numeric_col, value]].dropna()
    try:
        binned = pd.cut(dfx[numeric_col].astype(float), bins=bins)
    except Exception:
        binned = pd.qcut(dfx[numeric_col].astype(float), q=bins, duplicates="drop")
    grouped = dfx.assign(bin=binned).groupby("bin")[value].agg(agg).reset_index()
    x = grouped["bin"].astype(str).tolist()
    y = grouped[value].tolist()
    return {
        "data": [
            {"type": "bar", "x": x, "y": y, "name": value, "marker": {"color": "#3b82f6"}}
        ],
        "layout": _dark_layout(title or f"{value} by binned {numeric_col}"),
    }

def build_line_multi_config(
    df: pd.DataFrame, x: str, y: str, color: str, title: Optional[str] = None
) -> Dict[str, Any]:
    dfx = df[[x, y, color]].dropna().sort_values(x).head(10000)
    traces: list[Dict[str, Any]] = []
    palette = [
        "#3b82f6", "#22c55e", "#ef4444", "#a78bfa", "#f59e0b",
        "#10b981", "#eab308", "#8b5cf6", "#06b6d4", "#f97316",
    ]
    top_vals = dfx[color].astype(str).value_counts().head(12).index.tolist()
    for idx, val in enumerate(top_vals):
        sub = dfx[dfx[color].astype(str) == val]
        traces.append({
            "type": "scatter",
            "mode": "lines",
            "x": sub[x].astype(str).tolist(),
            "y": sub[y].tolist(),
            "name": str(val),
            "line": {"color": palette[idx % len(palette)]},
        })
    return {"data": traces, "layout": _dark_layout(title or f"{y} over {x}", x_title=x, y_title=y)}


def build_box_config(df: pd.DataFrame, col: str, title: Optional[str] = None) -> Dict[str, Any]:
    series = df[col].dropna().astype(float).tolist()
    return {
        "data": [
            {
                "type": "box",
                "y": series,
                "name": col,
                "marker": {"color": "#14b8a6"}
            }
        ],
        "layout": _dark_layout(title or f"Distribution (Box) of {col}", y_title=col),
    }


def build_scatter_numeric_color_config(
    df: pd.DataFrame, x: str, y: str, color_col: str, title: Optional[str] = None
) -> Dict[str, Any]:
    dfx = df[[x, y, color_col]].dropna().head(10000)
    return {
        "data": [
            {
                "type": "scatter",
                "mode": "markers",
                "x": dfx[x].tolist(),
                "y": dfx[y].tolist(),
                "marker": {
                    "color": dfx[color_col].tolist(),
                    "colorscale": "Viridis",
                    "showscale": True,
                },
                "name": f"{y} vs {x}",
            }
        ],
        "layout": _dark_layout(title or f"{y} vs {x}"),
    }

