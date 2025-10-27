from fastapi import HTTPException
from typing import Dict, Type, Callable, Optional
from threading import Lock


class ErrorHandler:
    _messages: Dict[int, str] = {
        100: "continue",
        101: "switching protocols",
        102: "processing",
        200: "ok",
        201: "created",
        202: "accepted",
        204: "no content",
        301: "moved permanently",
        302: "found",
        304: "not modified",
        307: "temporary redirect",
        308: "permanent redirect",
        400: "bad request",
        401: "unauthorized",
        403: "forbidden",
        404: "not found",
        405: "method not allowed",
        408: "request timeout",
        409: "conflict",
        410: "gone",
        415: "unsupported media type",
        422: "unprocessable entity",
        429: "too many requests",
        500: "internal server error",
        501: "not implemented",
        502: "bad gateway",
        503: "service unavailable",
        504: "gateway timeout",
    }
    _cache: Dict[str, Dict[int, HTTPException]] = {}
    _lock = Lock()

    def __init__(self, name: str):
        self.modelname = name.lower()
        with self._lock:
            if self.modelname not in self._cache:
                self._cache[self.modelname] = {}

    def get(self, status_code: int, detail: str = None) -> HTTPException:
        if detail:
            return HTTPException(status_code=status_code, detail=detail)
        model_cache = self._cache[self.modelname]
        if status_code not in model_cache:
            base_msg = self._messages.get(status_code, "error")
            message = f"{self.modelname} {base_msg}"
            model_cache[status_code] = HTTPException(
                status_code=status_code,
                detail=message
            )
        return model_cache[status_code]
