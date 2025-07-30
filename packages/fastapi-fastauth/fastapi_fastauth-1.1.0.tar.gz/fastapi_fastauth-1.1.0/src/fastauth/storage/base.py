from abc import abstractmethod, ABC

from fastauth.schemas.auth import TokenData
from fastauth.settings import FastAuthSettings


class BaseTokenStorage(ABC):
    def __init__(self, settings: FastAuthSettings):
        self.settings = settings

    # @abstractmethod
    # async def store_token(self, jti: str, token_data: TokenData, ttl: int) -> None:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # async def get_token(self, jti: str) -> TokenData | None:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # async def revoke_token(self, jti: str) -> None:
    #     raise NotImplementedError
    #
    # @abstractmethod
    # async def is_token_revoked(self, jti: str) -> bool:
    #     raise NotImplementedError

    @abstractmethod
    def decode_token(self, token: str) -> TokenData:
        raise NotImplementedError

    @abstractmethod
    def encode_token(self, payload: TokenData) -> str:
        raise NotImplementedError
