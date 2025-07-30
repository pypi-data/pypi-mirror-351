from fastapi import FastAPI, Request
from starlette import status as status
from fastapi.responses import JSONResponse


class FastAuthException(Exception):
    def __init__(
        self,
        code: int,
        title: str,
        message: str | None = None,
        debug: Exception | None = None,
        headers: dict | None = None,
    ):
        self.code = code
        self.title = title
        self.message = message
        self.debug = str(debug) if debug is not None else None
        self.headers = headers or {}

    def to_response(self, debug: bool = False):
        payload = {
            "code": self.code,
            "title": self.title,
            "message": self.message,
            "debug": self.debug if debug else None,
        }
        return JSONResponse(
            status_code=self.code, content=payload, headers=self.headers
        )


def set_exception_handler(app: FastAPI, debug: bool = False):
    @app.exception_handler(FastAuthException)
    async def set_exception_handler(
        request: Request, exc: FastAuthException
    ) -> JSONResponse:
        return exc.to_response(debug)

    return app


__all__ = ["FastAuthException", "status", "set_exception_handler"]
