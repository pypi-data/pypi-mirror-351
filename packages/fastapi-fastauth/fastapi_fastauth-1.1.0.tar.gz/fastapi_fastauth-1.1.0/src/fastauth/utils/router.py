from fastapi import APIRouter


def default_router(prefix: str, tags: list[str] = [], **kwargs):
    return APIRouter(prefix=prefix, tags=kwargs.get("tags", tags), **kwargs)
