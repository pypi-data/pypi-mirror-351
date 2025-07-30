from abc import ABC, abstractmethod
from fastapi import Response

from fastauth.settings import FastAuthSettings
from fastauth.schemas.auth import TokenResponse


class BaseTransport(ABC):
    def __init__(self, settings: FastAuthSettings):
        self.settings = settings

    @abstractmethod
    def login_response(self, payload: TokenResponse, **kwargs) -> Response:
        pass

    @abstractmethod
    def logout_response(self, **kwargs) -> Response:
        pass

    @abstractmethod
    def get_schema(self):
        pass
