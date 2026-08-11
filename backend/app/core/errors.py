from typing import Any


class AppError(Exception):
    def __init__(
        self,
        status_code: int,
        title: str,
        detail: str,
        error_type: str = "about:blank",
        instance: str | None = None,
        extra: dict[str, Any] | None = None,
    ):
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type = error_type
        self.instance = instance
        self.extra = extra or {}
        super().__init__(self.detail)
