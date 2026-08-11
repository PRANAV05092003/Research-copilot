import base64
import json
import uuid
from datetime import datetime


def encode_cursor(created_at: datetime, item_id: uuid.UUID) -> str:
    data = {"c": created_at.isoformat(), "i": str(item_id)}
    json_str = json.dumps(data)
    return base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        json_str = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        data = json.loads(json_str)
        created_at = datetime.fromisoformat(data["c"])
        item_id = uuid.UUID(data["i"])
        return created_at, item_id
    except Exception:
        from app.core.errors import AppError

        raise AppError(status_code=400, title="Bad Request", detail="Invalid pagination cursor")
