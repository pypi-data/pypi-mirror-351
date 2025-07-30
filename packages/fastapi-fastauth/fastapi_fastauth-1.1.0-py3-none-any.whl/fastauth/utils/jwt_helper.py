import jwt
from jwt import decode, encode
from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime

from fastauth.settings import FastAuthSettings
from fastauth.exceptions import FastAuthException, status
from fastauth.utils.time import now
from datetime import timedelta


class JWTPayload(BaseModel):
    model_config = ConfigDict(extra="allow", from_attributes=True)
    expires_in: int | None = Field(default=None, exclude=True)

    sub: str
    iat: datetime = Field(default_factory=now)
    exp: datetime | None = None
    aud: str | list[str] | None = None
    iss: str | list[str] | None = None
    nbf: datetime | None = None
    jti: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_expires_in(cls, data):
        if isinstance(data, dict):
            exp = data.get("exp", None)
            iat = data.get("iat", None)
            expires_in = data.get("expires_in", None)

            if exp is not None:
                return data

            if iat and expires_in:
                data["exp"] = iat + timedelta(seconds=expires_in)

        return data

    def to_token(self, key: str, algorithm: str = "HS256", **kwargs) -> str:
        payload = self.model_dump(exclude_none=True)
        return encode(payload, key=key, algorithm=algorithm, **kwargs)

    @classmethod
    def from_token(cls, token: str, key: str, algorithm: str = "HS256", **kwargs):
        try:
            payload = decode(token, key=key, algorithms=[algorithm], **kwargs)
            return cls.model_validate(payload)
        except jwt.ExpiredSignatureError as e:
            raise FastAuthException(
                status.HTTP_400_BAD_REQUEST, "Expired token", "Token expired", e
            )

        except jwt.InvalidTokenError as e:
            raise FastAuthException(
                status.HTTP_400_BAD_REQUEST, "Invalid token", "Invalid token", e
            )

        except Exception as e:
            raise FastAuthException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal Server Error",
                "Error when decoding token",
                e,
            )


def to_jwt_token(settings: FastAuthSettings, payload: JWTPayload, **kwargs) -> str:
    return payload.to_token(settings.SECRET_KEY, settings.JWT_ALGORITHM, **kwargs)


def to_jwt_payload(settings: FastAuthSettings, token: str, **kwargs) -> JWTPayload:
    return JWTPayload.from_token(
        token, settings.SECRET_KEY, settings.JWT_ALGORITHM, **kwargs
    )


__all__ = ["JWTPayload", "to_jwt_token", "to_jwt_payload"]
