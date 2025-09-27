import io
import os
import uuid
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request

from ..services.files import (
    save_uploaded_file,
    store_dataframe,
    get_dataframe,
    get_metadata,
    list_files,
)
from ..services.preprocess import process_uploaded_file
from ..services.recommend import get_chart_recommendations, create_chart_from_spec
from ..services.analytics import (
    chart_revenue_over_time,
    chart_revenue_by_category,
    chart_revenue_by_gender,
    chart_age_distribution,
    chart_quantity_vs_revenue,
)


api_bp = Blueprint("api", __name__)


@api_bp.post("/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    file_storage = request.files["file"]
    if file_storage.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_id, saved_path, original_name = save_uploaded_file(file_storage)

    df, meta = process_uploaded_file(saved_path)
    store_dataframe(file_id, df, meta)

    # Small sample for preview
    sample_records = df.head(5).to_dict(orient="records")

    return jsonify(
        {
            "file_id": file_id,
            "filename": original_name,
            "columns": meta["columns"],
            "row_count": int(meta.get("row_count", len(df))),
            "sample": sample_records,
        }
    )


@api_bp.get("/columns/<file_id>")
def get_columns(file_id: str):
    meta = get_metadata(file_id)
    if meta is None:
        return jsonify({"error": "file_id not found"}), 404
    return jsonify({"file_id": file_id, "columns": meta.get("columns", [])})


@api_bp.get("/files")
def get_files():
    return jsonify({"files": list_files()})


@api_bp.post("/suggest-charts")
def suggest_charts():
    payload = request.get_json(silent=True) or {}
    file_id: str = payload.get("file_id")
    selected_columns: List[str] = payload.get("selected_columns", [])
    limit: int = int(payload.get("limit", 5))

    if not file_id or not selected_columns:
        return jsonify({"error": "file_id and selected_columns are required"}), 400

    df = get_dataframe(file_id)
    meta = get_metadata(file_id)
    if df is None or meta is None:
        return jsonify({"error": "file_id not found"}), 404

    suggestions = get_chart_recommendations(df, meta, selected_columns, limit=limit)
    return jsonify({"suggestions": suggestions})


@api_bp.post("/create-chart")
def create_chart():
    payload = request.get_json(silent=True) or {}
    file_id: str = payload.get("file_id")
    spec: Dict[str, Any] = payload.get("spec", {})

    if not file_id or not spec:
        return jsonify({"error": "file_id and spec are required"}), 400

    df = get_dataframe(file_id)
    meta = get_metadata(file_id)
    if df is None or meta is None:
        return jsonify({"error": "file_id not found"}), 404

    chart = create_chart_from_spec(df, meta, spec)
    return jsonify(chart)


# --------- Analytics pre-aggregated charts ---------

@api_bp.get("/charts/revenue-over-time")
def api_revenue_over_time():
    file_id = request.args.get("file_id")
    freq = request.args.get("freq") or None
    df = get_dataframe(file_id) if file_id else None
    if df is None:
        return jsonify({"error": "file_id not found"}), 404
    data = chart_revenue_over_time(df, freq=freq)
    return jsonify({"data": data})


@api_bp.get("/charts/revenue-by-category")
def api_revenue_by_category():
    file_id = request.args.get("file_id")
    top_k = int(request.args.get("top_k", 10))
    df = get_dataframe(file_id) if file_id else None
    if df is None:
        return jsonify({"error": "file_id not found"}), 404
    data = chart_revenue_by_category(df, top_k=top_k)
    return jsonify({"data": data})


@api_bp.get("/charts/revenue-by-gender")
def api_revenue_by_gender():
    file_id = request.args.get("file_id")
    df = get_dataframe(file_id) if file_id else None
    if df is None:
        return jsonify({"error": "file_id not found"}), 404
    data = chart_revenue_by_gender(df)
    return jsonify({"data": data})


@api_bp.get("/charts/age-distribution")
def api_age_distribution():
    file_id = request.args.get("file_id")
    bins = int(request.args.get("bins", 10))
    df = get_dataframe(file_id) if file_id else None
    if df is None:
        return jsonify({"error": "file_id not found"}), 404
    data = chart_age_distribution(df, bins=bins)
    return jsonify({"data": data})


@api_bp.get("/charts/quantity-vs-revenue")
def api_quantity_vs_revenue():
    file_id = request.args.get("file_id")
    sample = int(request.args.get("sample", 500))
    df = get_dataframe(file_id) if file_id else None
    if df is None:
        return jsonify({"error": "file_id not found"}), 404
    data = chart_quantity_vs_revenue(df, sample=sample)
    return jsonify({"data": data})


