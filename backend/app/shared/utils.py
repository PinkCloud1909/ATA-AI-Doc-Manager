import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generate_request_id() -> str:
    return uuid.uuid4().hex


def build_permission_key(method: str, route_path: str) -> str:
    return f"{method.upper()}:{route_path}"


def safe_filename(filename: str) -> str:
    name = Path(filename).name
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    return cleaned or "file"
