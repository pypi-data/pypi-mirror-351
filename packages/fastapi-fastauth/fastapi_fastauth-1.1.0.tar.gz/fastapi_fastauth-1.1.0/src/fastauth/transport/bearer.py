from starlette.responses import JSONResponse, Response
from .base import BaseTransport
from fastauth.schemas.auth import TokenResponse
from fastapi.security import OAuth2PasswordBearer


class BearerTransport(BaseTransport):
    def get_schema(self):
        return OAuth2PasswordBearer(tokenUrl=self.settings.LOGIN_URL)

    def login_response(self, payload: TokenResponse, **kwargs) -> JSONResponse:
        return JSONResponse(status_code=200, content=payload.model_dump())

    def logout_response(self, **kwargs) -> Response:
        return Response(status_code=204)
