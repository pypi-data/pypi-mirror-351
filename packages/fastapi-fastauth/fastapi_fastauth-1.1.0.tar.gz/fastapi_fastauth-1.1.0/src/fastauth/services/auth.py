import uuid
from abc import abstractmethod
from fastapi import Request
from fastauth.repositories.oauths import IOAuthRepository
from fastauth.repositories.roles import IRoleRepository
from fastauth.repositories.users import IUserRepository
from fastauth.schemas.auth import TokenType, TokenData, TokenResponse
from fastauth.schemas.oauth import OAuthCreate
from fastauth.schemas.users import BaseUserCreate, BaseUserUpdate
from fastauth.settings import FastAuthSettings
from fastauth.storage.base import BaseTokenStorage
from typing import Generic
from fastauth.models import UM, URPM, UOAM
from fastauth.types import ID
from fastauth.exceptions import FastAuthException, status
from fastauth.utils.jwt_helper import JWTPayload, to_jwt_token, to_jwt_payload
from fastauth.utils.password import IPasswordHelper, PasswordHelper


class BaseAuthService(Generic[UM, ID]):
    def __init__(
        self,
        settings: FastAuthSettings,
        user_repo: IUserRepository[UM, ID],
        token_storage: BaseTokenStorage,
        role_repo: IRoleRepository | None = None,
        oauth_repo: IOAuthRepository | None = None,
        password_helper: IPasswordHelper = PasswordHelper(),
    ):
        self.settings = settings
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.oauth_repo = oauth_repo
        self.token_storage = token_storage
        self.password_helper = password_helper

    @abstractmethod
    def parse_user_id(self, value: str) -> ID:
        raise NotImplementedError

    async def verify_token(self, token: str, token_type: TokenType) -> TokenData:
        payload = self.token_storage.decode_token(token)
        if not payload.token_type == token_type:
            raise FastAuthException(
                status.HTTP_401_UNAUTHORIZED,
                "Invalid token type",
                f"{token_type} token type required.",
            )

        # jti = payload.jti
        # if jti and await self.token_storage.is_token_revoked(jti):
        #     raise FastAuthException(
        #         status.HTTP_401_UNAUTHORIZED,
        #         "Invalid token revoked",
        #         "Token was revoked, please login again later."
        #     )

        # Handle by token_storage
        # if datetime.now(UTC) > payload.exp:
        #     raise FastAuthException(
        #         status.HTTP_401_UNAUTHORIZED,
        #         "Token expired",
        #         "Token expired. Please login again later."
        #     )
        return payload

    async def verify_user(self, user: UM) -> UM:
        error = FastAuthException(
            status.HTTP_401_UNAUTHORIZED,
            "User not found",
            "User not found/in active/not verified.",
        )
        if user is None:
            raise error
        if not user.is_active and not self.settings.ALLOW_INACTIVE_USERS:
            raise error
        if not user.is_verified and not self.settings.ALLOW_UNVERIFIED_USERS:
            raise error
        return user

    async def authenticate(self, payload: TokenData) -> UM:
        user_id = self.parse_user_id(payload.user_id)
        user = await self.user_repo.get_by_pk(user_id)
        return await self.verify_user(user)

    @staticmethod
    def has_permission(user_permissions: list[str], required_permission: str) -> bool:
        return required_permission in user_permissions

    @staticmethod
    def has_role(user_roles: list[str], required_role: str) -> bool:
        return required_role in user_roles

    async def create_access_token(self, user: URPM, expires_in: int | None = None):
        jti = str(uuid.uuid4())
        roles = []
        if hasattr(user, "roles"):
            roles.extend([r.name for r in user.roles])
        permissions = []
        if hasattr(user, "permissions"):
            for role in user.roles:
                permissions.extend(
                    [f"{perm.resource}:{perm.action}" for perm in role.permissions]
                )
        token_data = TokenData(
            user_id=str(user.id),
            email=user.email,
            roles=roles,
            permissions=permissions,
            token_type=TokenType.ACCESS,
            expires_in=expires_in or self.settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            jti=jti,
        )
        token = self.token_storage.encode_token(token_data)
        # ttl = int((expire - datetime.now(UTC)).total_seconds())
        # await self.token_storage.store_token(jti, token_data, ttl)
        return token

    async def create_refresh_token(self, user: URPM):
        jti = str(uuid.uuid4())
        token_data = TokenData(
            user_id=str(user.id),
            email=user.email,
            roles=[],
            permissions=[],
            token_type=TokenType.REFRESH,
            expires_in=self.settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            jti=jti,
        )
        token = self.token_storage.encode_token(token_data)
        # ttl = int((expire - datetime.now(UTC)).total_seconds())
        # await self.token_storage.store_token(jti, token_data, ttl)
        return token

    async def create_tokens(self, user: URPM) -> TokenResponse:
        return TokenResponse(
            access_token=await self.create_access_token(user),
            refresh_token=await self.create_refresh_token(user)
            if self.settings.USE_REFRESH_TOKEN
            else None,
            expires_in=self.settings.ACCESS_TOKEN_EXPIRE_SECONDS,
        )

    async def refresh_access_token(self, token_payload: TokenData, **kwargs):
        user_id = self.parse_user_id(token_payload.user_id)
        user = await self.user_repo.get_by_pk(user_id)
        user = await self.verify_user(user)
        tokens = await self.create_tokens(user)
        await self.on_after_access_token_refresh(
            user, tokens, kwargs.get("request", None)
        )

    async def login(self, username: str, password: str, **kwargs) -> TokenResponse:
        user = await self.user_repo.get_by_login_fields(
            self.settings.USER_LOGIN_FIELDS, username
        )
        user = await self.verify_user(user)

        # Check user password
        is_valid_password, new_hash = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not is_valid_password:
            raise FastAuthException(
                status.HTTP_401_UNAUTHORIZED, "Invalid password", "Invalid password."
            )
        # Update password hash
        if new_hash:
            user = await self.user_repo.update(user, {"hashed_password": new_hash})

        tokens = await self.create_tokens(user)
        await self.on_after_login(user, tokens, kwargs.get("request", None))
        return tokens

    async def signup(self, payload: BaseUserCreate, safe: bool = True, **kwargs) -> UM:
        # Check if user already exist by login fields
        for field in self.settings.USER_LOGIN_FIELDS:
            if hasattr(payload, field):
                user = await self.user_repo.get_by_field(field, getattr(payload, field))
                if user is not None:
                    raise FastAuthException(
                        status.HTTP_400_BAD_REQUEST,
                        "User already exists.",
                        "User with provided credentials already exists.",
                    )

        # Generate hash from password
        payload_dict = payload.model_dump()
        payload_dict["hashed_password"] = self.password_helper.hash(
            payload_dict.pop("password")
        )

        # Set defaults is safe mode
        if safe:
            payload_dict["is_active"] = self.settings.DEFAULT_USER_IS_ACTIVE
            payload_dict["is_verified"] = self.settings.DEFAULT_USER_IS_VERIFIED

        # Check if user created with roles
        roles = payload_dict.pop("roles", [])
        if len(roles) > 0:
            if self.role_repo is not None:
                if safe:
                    roles = await self.role_repo.get_roles_by_list(
                        self.settings.DEFAULT_USER_ROLES
                    )
                else:
                    roles = await self.role_repo.get_roles_by_list(roles)
                payload_dict["roles"] = roles
            else:
                raise RuntimeError(
                    "To use RBAC you need to implement IRoleRepository and pass it to role_repo argument of BaseAuthService"
                )
        user = await self.user_repo.create(payload_dict)
        await self.on_after_register(user, kwargs.get("request", None))
        return user

    async def oauth_callback(
        self: "BaseAuthService[UOAM, ID]",
        payload: OAuthCreate,
        associate_by_email: bool | None = None,
        **kwargs,
    ):
        if self.oauth_repo is None:
            raise RuntimeError(
                "To use OAuth you need to implement IOAuthRepository and pass it to oauth_repo argument of BaseAuthService"
            )

        if associate_by_email is None:
            associate_by_email = self.settings.OAUTH_ASSOCIATE_BY_EMAIL

        user = await self.oauth_repo.get_user_by_oauth_account(
            payload.oauth_name, payload.account_id
        )
        if user is None:
            # associate account
            user = await self.user_repo.get_by_field("email", payload.account_email)
            if user is None:
                # create account
                password = self.password_helper.generate()
                user_payload = {
                    "email": payload.account_email,
                    "hashed_password": password,
                    "is_verified": self.settings.DEFAULT_USER_IS_VERIFIED,
                    "is_active": self.settings.DEFAULT_USER_IS_ACTIVE,
                }  # TODO: add roles

                user = await self.user_repo.create(user_payload)
                user = await self.oauth_repo.create_and_add_to_user(
                    user, payload.model_dump()
                )
                await self.on_after_register(user, kwargs.get("request", None))
            else:
                # try to associate account
                if not associate_by_email:
                    raise FastAuthException(
                        status.HTTP_400_BAD_REQUEST,
                        "User already exists.",
                        "User with provided credentials already exists.",
                    )
                user = await self.oauth_repo.create_and_add_to_user(
                    user, payload.model_dump()
                )

        for existing_oauth_account in user.oauth_accounts:
            if (
                existing_oauth_account.account_id == payload.account_id
                and existing_oauth_account.oauth_name == payload.oauth_name
            ):
                user = await self.oauth_repo.update_and_add_to_user(
                    user, existing_oauth_account, payload.model_dump()
                )

        return user

    async def patch_user(
        self, user: UM, payload: BaseUserUpdate, safe: bool = True, **kwargs
    ) -> UM:
        for field in self.settings.USER_LOGIN_FIELDS:
            if hasattr(payload, field):
                user = await self.user_repo.get_by_field(field, getattr(payload, field))
                if user is not None:
                    raise FastAuthException(
                        status.HTTP_400_BAD_REQUEST,
                        "User already exists.",
                        "User with provided credentials already exists.",
                    )

        payload_dict = payload.model_dump(
            exclude_none=True, exclude_defaults=True, exclude_unset=True
        )

        if safe:
            payload_dict.pop("is_active", None)
            payload_dict.pop("is_verified", None)

        if hasattr(payload_dict, "roles"):
            if self.role_repo is None:
                raise RuntimeError(
                    "To use roles you need to implement IRoleRepository and pass it to role_repo argument of BaseAuthService"
                )
            if safe:
                payload_dict.pop("roles", None)
            else:
                payload_dict["roles"] = await self.role_repo.get_roles_by_list(
                    payload_dict["roles"]
                )

        user = await self.user_repo.update(user, payload_dict)
        await self.on_after_user_update(user, payload, kwargs.get("request", None))
        return user

    async def request_verification(self, email: str, **kwargs):
        user = await self.user_repo.get_by_field("email", email)
        not_found_error = FastAuthException(
            status.HTTP_404_NOT_FOUND,
            "User doesn't exist.",
            "User with provided credentials doesn't exist.",
        )

        if user is None or not user.is_active:
            raise not_found_error

        if user.is_verified:
            raise FastAuthException(
                status.HTTP_400_BAD_REQUEST, "User already verified."
            )

        payload = JWTPayload(
            sub=str(user.id),
            email=str(user.email),
            aud=self.settings.VERIFICATION_TOKEN_AUDIENCE,
            expires_in=self.settings.VERIFICATION_TOKEN_EXPIRE_SECONDS,
        )
        token = to_jwt_token(self.settings, payload)
        await self.on_after_request_verification(
            user, token, kwargs.get("request", None)
        )
        return token

    async def user_verification(self, token: str, **kwargs):
        decode_token = to_jwt_payload(
            self.settings, token, audience=self.settings.VERIFICATION_TOKEN_AUDIENCE
        )
        user_id = self.parse_user_id(decode_token.sub)
        email = decode_token.email

        user = await self.user_repo.get_by_field("email", email)
        if user is None:
            raise FastAuthException(
                status.HTTP_404_NOT_FOUND,
                "User doesn't exist.",
                "User with provided credentials doesn't exist.",
            )

        if user_id != user.id:
            raise FastAuthException(
                status.HTTP_400_BAD_REQUEST, "Invalid verification token."
            )

        if user.is_verified:
            raise FastAuthException(
                status.HTTP_400_BAD_REQUEST, "User already verified."
            )

        user = await self.user_repo.update(user, payload={"is_verified": True})
        await self.on_after_verification(user, kwargs.get("request", None))
        return user

    async def request_forgot_password(self, email: str, **kwargs):
        user = await self.user_repo.get_by_field("email", email)
        user = await self.verify_user(user)

        jwt_payload = JWTPayload(
            sub=str(user.id),
            password_fgpt=self.password_helper.hash(user.hashed_password),
            aud=self.settings.RESET_TOKEN_AUDIENCE,
            expires_in=self.settings.RESET_TOKEN_EXPIRE_SECONDS,
        )
        token = to_jwt_token(self.settings, jwt_payload)
        await self.on_after_request_forgot_password(
            user, token, kwargs.get("request", None)
        )
        return token

    async def reset_user_password(self, token: str, new_password: str, **kwargs):
        decode_token = to_jwt_payload(
            self.settings, token, audience=self.settings.RESET_TOKEN_AUDIENCE
        )
        user_id = self.parse_user_id(decode_token.sub)

        user = await self.user_repo.get_by_pk(user_id)
        user = await self.verify_user(user)

        valid, _ = self.password_helper.verify_and_update(
            user.hashed_password, decode_token.password_fgpt
        )
        if not valid:
            raise FastAuthException(status.HTTP_400_BAD_REQUEST, "Invalid reset token")

        hashed_password = self.password_helper.hash(new_password)

        user = await self.user_repo.update(user, {"hashed_password": hashed_password})
        await self.on_after_reset_password(user, kwargs.get("request", None))
        return user

    async def on_after_register(self, user: UM, request: Request | None = None):
        """
        Call after user registration
        """

    async def on_after_login(
        self, user: UM, tokens: TokenResponse, request: Request | None = None
    ):
        """
        Call after user login
        """

    async def on_after_access_token_refresh(
        self, user: UM, tokens: TokenResponse, request: Request | None = None
    ):
        """
        Call after user access token refreshed
        """

    async def on_after_user_update(
        self, user: UM, payload: BaseUserUpdate, request: Request | None = None
    ):
        """
        Call after user update
        :param user:
        :param payload:
        :param request:
        :return:
        """

    async def on_after_request_verification(
        self, user: UM, token: str, request: Request | None = None
    ):
        """
        Call after user request verification,
        :param user:
        :param token:
        :param request:
        :return:
        """

    async def on_after_verification(self, user: UM, request: Request | None = None):
        """
        Call after user verification
        :param user:
        :param request:
        :return:
        """

    async def on_after_request_forgot_password(
        self, user: UM, token: str, request: Request | None = None
    ):
        """
        Call after user forgot password
        :param user:
        :param token:
        :param request:
        :return:
        """

    async def on_after_reset_password(self, user: UM, request: Request | None = None):
        """
        Call after user reset password
        :param user:
        :param request:
        :return:
        """


class UUIDMixin:
    def parse_user_id(self, value: str) -> uuid.UUID:
        return uuid.UUID(value)
