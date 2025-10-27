from fastapi import APIRouter
from typing import List, Optional


def build_router(path: str, tags: Optional[List[str]] = None) -> APIRouter:
    return APIRouter(prefix=f"/v1/{path}", tags=tags or [])