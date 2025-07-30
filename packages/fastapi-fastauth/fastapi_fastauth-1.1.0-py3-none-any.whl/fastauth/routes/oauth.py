from fastauth import FastAuth
from httpx_oauth.oauth2 import BaseOAuth2, OAuth2Token
from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback
from fastapi import Query, Depends, Request
from fastauth.utils.router import default_router
from fastauth.exceptions import FastAuthException, status
from fastauth.schemas.oauth import OAuth2AuthorizeResponse, OAuthCreate
from fastauth.services import BaseAuthService
from fastauth.utils.jwt_helper import JWTPayload, to_jwt_payload, to_jwt_token


def get_oauth_router(
    security: FastAuth,
    client: BaseOAuth2,
    redirect_url: str | None = None,
    associate_with_email: bool | None = None,
    **kwargs,
):
    router = default_router(
        security.settings.ROUTER_AUTH_PREFIX, tags=["OAuth", client.name], **kwargs
    )

    callback_route_name = f"oauth:{client.name.lower()}.callback"

    if redirect_url is not None:
        oauth_authorize_callback = OAuth2AuthorizeCallback(
            client, redirect_url=redirect_url
        )
    else:
        oauth_authorize_callback = OAuth2AuthorizeCallback(
            client, route_name=callback_route_name
        )

    @router.get("/authorize", response_model=OAuth2AuthorizeResponse)
    async def authorize(request: Request, scopes: list[str] = Query(default=[])):
        if redirect_url is not None:  # pragma: no cover
            authorize_redirect_url = redirect_url
        else:
            authorize_redirect_url = str(request.url_for(callback_route_name))
        state_payload = JWTPayload(
            sub="",
            expires_in=security.settings.STATE_TOKEN_EXPIRE_SECONDS,
            aud=security.settings.STATE_TOKEN_AUDIENCE,
        )
        state = to_jwt_token(security.settings, state_payload)
        authorization_url = await client.get_authorization_url(
            authorize_redirect_url,
            state,
            scopes,
        )
        return OAuth2AuthorizeResponse(authorization_url=authorization_url)

    @router.get("/callback", name=callback_route_name)
    async def callback(
        request: Request,
        access_token_state: tuple[OAuth2Token, str] = Depends(oauth_authorize_callback),
        service: BaseAuthService = Depends(security.service_dep),
    ):
        token, state = access_token_state
        account_id, account_email = await client.get_id_email(token["access_token"])
        if account_email is None:
            raise FastAuthException(
                status.HTTP_400_BAD_REQUEST,
                "OAuth Error",
                "OAuth does not provide an account email",
            )

        # Try decode state token
        to_jwt_payload(
            security.settings, state, audience=security.settings.STATE_TOKEN_AUDIENCE
        )

        oauth_payload = OAuthCreate(
            oauth_name=client.name,
            access_token=token["access_token"],
            account_id=account_id,
            account_email=account_email,
            expires_at=token.get("expires_at"),
            refresh_token=token.get("refresh_token"),
        )

        user = await service.oauth_callback(oauth_payload, associate_with_email)
        tokens = await service.create_tokens(user)
        return security.transport.login_response(tokens)

    return router
