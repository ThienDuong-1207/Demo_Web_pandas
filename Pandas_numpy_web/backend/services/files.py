import os
import uuid
import json
from datetime import datetime
from typing import Dict, Optional, Tuple, List

import pandas as pd
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


_DATAFRAMES: Dict[str, pd.DataFrame] = {}
_METADATA: Dict[str, Dict] = {}
_REGISTRY: Dict[str, Dict] = {}


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def _storage_dir() -> str:
    custom = os.getenv("DATA_DIR")
    if custom:
        return custom
    return os.path.join(_project_root(), "backend", "storage")


def ensure_storage_dirs() -> Tuple[str, str]:
    base = _storage_dir()
    uploads = os.path.join(base, "uploads")
    cache = os.path.join(base, "cache")
    os.makedirs(uploads, exist_ok=True)
    os.makedirs(cache, exist_ok=True)
    return uploads, cache


def _registry_path() -> str:
    base = _storage_dir()
    return os.path.join(base, "registry.json")


def _load_registry_from_disk() -> None:
    global _REGISTRY
    try:
        path = _registry_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    _REGISTRY = data
        _reconcile_registry_from_uploads()
    except Exception:
        # ignore corrupt registry
        _REGISTRY = {}


def _save_registry_to_disk() -> None:
    try:
        path = _registry_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_REGISTRY, f)
    except Exception:
        pass


def _reconcile_registry_from_uploads() -> None:
    """Ensure files present on disk exist in registry; add minimal entries if missing."""
    uploads_dir, _ = ensure_storage_dirs()
    try:
        for name in os.listdir(uploads_dir):
            path = os.path.join(uploads_dir, name)
            if not os.path.isfile(path):
                continue
            file_id, ext = os.path.splitext(name)
            if len(file_id) < 8:
                continue
            if file_id not in _REGISTRY:
                stat = os.stat(path)
                _REGISTRY[file_id] = {
                    "file_id": file_id,
                    "filename": name,
                    "path": path,
                    "created_at": datetime.utcfromtimestamp(stat.st_mtime).isoformat(),
                }
        _save_registry_to_disk()
    except Exception:
        pass


def save_uploaded_file(file_storage: FileStorage) -> Tuple[str, str, str]:
    uploads_dir, _ = ensure_storage_dirs()
    original_name = secure_filename(file_storage.filename or "upload")
    file_id = str(uuid.uuid4())
    _, ext = os.path.splitext(original_name)
    saved_path = os.path.join(uploads_dir, f"{file_id}{ext}")
    file_storage.save(saved_path)
    # Register minimal info immediately; will enrich after processing
    _REGISTRY[file_id] = {
        "file_id": file_id,
        "filename": original_name,
        "path": saved_path,
        "created_at": datetime.utcnow().isoformat(),
    }
    _save_registry_to_disk()
    return file_id, saved_path, original_name


def store_dataframe(file_id: str, df: pd.DataFrame, metadata: Dict) -> None:
    _DATAFRAMES[file_id] = df
    _METADATA[file_id] = metadata
    if file_id in _REGISTRY:
        _REGISTRY[file_id]["columns"] = metadata.get("columns", [])
        _REGISTRY[file_id]["row_count"] = metadata.get("row_count", len(df))
        _save_registry_to_disk()


def get_dataframe(file_id: str) -> Optional[pd.DataFrame]:
    return _DATAFRAMES.get(file_id)


def get_metadata(file_id: str) -> Optional[Dict]:
    return _METADATA.get(file_id)


def list_files() -> List[Dict]:
    # Return newest first (order by created_at desc)
    return sorted(_REGISTRY.values(), key=lambda x: x.get("created_at", ""), reverse=True)


def get_file_record(file_id: str) -> Optional[Dict]:
    return _REGISTRY.get(file_id)


# Load registry once at import
_load_registry_from_disk()


