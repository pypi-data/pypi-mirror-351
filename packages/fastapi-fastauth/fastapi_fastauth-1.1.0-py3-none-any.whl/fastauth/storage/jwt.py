from .base import BaseTokenStorage
from fastauth.schemas.auth import TokenData
from fastauth.utils.jwt_helper import to_jwt_token, to_jwt_payload, JWTPayload


class JWTTokenStorage(BaseTokenStorage):
    # async def store_token(self, jti: str, token_data: TokenData, ttl: int) -> None:
    #     pass
    #
    # async def revoke_token(self, jti: str) -> None:
    #     pass
    #
    # async def is_token_revoked(self, jti: str) -> bool:
    #     return False
    #
    # async def get_token(self, jti: str) -> TokenData | None:
    #     pass

    def decode_token(self, token: str) -> TokenData:
        decoded = to_jwt_payload(
            self.settings, token, audience=self.settings.ACCESS_TOKEN_AUDIENCE
        )
        if decoded.exp:
            expires_in = int(decoded.exp.timestamp()) - int(decoded.iat.timestamp())
        else:
            expires_in = None

        return TokenData(
            **decoded.model_dump(), user_id=decoded.sub, expires_in=expires_in
        )

    def encode_token(self, payload: TokenData) -> str:
        jwt_payload = JWTPayload(
            sub=payload.user_id,
            aud=self.settings.ACCESS_TOKEN_AUDIENCE,
            jti=payload.jti,
            expires_in=payload.expires_in,
            token_type=payload.token_type,
            email=payload.email,
            roles=payload.roles,
            permissions=payload.permissions,
        )
        return to_jwt_token(self.settings, jwt_payload)
