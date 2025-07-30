from .base import BaseTransport
from fastauth.schemas.auth import TokenResponse
from fastapi import Response
from fastapi.security import APIKeyCookie


class CookieTransport(BaseTransport):
    def get_schema(self):
        return APIKeyCookie(name=self.settings.COOKIE_ACCESS_TOKEN_NAME)

    def login_response(self, payload: TokenResponse, **kwargs) -> Response:
        response = Response(status_code=204)
        response = self._set_cookie(
            response,
            self.settings.COOKIE_ACCESS_TOKEN_NAME,
            payload.access_token,
            self.settings.COOKIE_ACCESS_TOKEN_MAX_AGE,
        )
        if self.settings.USE_REFRESH_TOKEN:
            response = self._set_cookie(
                response,
                self.settings.COOKIE_REFRESH_TOKEN_NAME,
                payload.refresh_token,
                self.settings.COOKIE_REFRESH_TOKEN_MAX_AGE,
            )
        return response

    def logout_response(self, **kwargs) -> Response:
        response = Response(status_code=204)
        response = self._remove_cookie(response, self.settings.COOKIE_ACCESS_TOKEN_NAME)
        response = self._remove_cookie(
            response, self.settings.COOKIE_REFRESH_TOKEN_NAME
        )
        return response

    def _set_cookie(
        self, response: Response, key: str, value: str, max_age: int
    ) -> Response:
        response.set_cookie(key=key, value=value, max_age=max_age)
        return response

    def _remove_cookie(self, response: Response, key: str):
        response.delete_cookie(key=key)
        return response
