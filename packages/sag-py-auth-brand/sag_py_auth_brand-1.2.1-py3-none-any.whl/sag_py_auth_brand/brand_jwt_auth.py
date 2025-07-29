import logging
from logging import Logger

from fastapi import Header
from sag_py_auth.jwt_auth import JwtAuth
from sag_py_auth.models import Token, TokenRole
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from .models import BrandAuthConfig
from .request_brand_context import set_request_brand as set_request_brand_to_context

logger: Logger = logging.getLogger(__name__)


class BrandJwtAuth(JwtAuth):
    def __init__(self, auth_config: BrandAuthConfig, required_endpoint_roles: list[str] | None) -> None:
        super().__init__(
            auth_config,
            required_roles=self._build_required_token_roles(auth_config, required_endpoint_roles),
            required_realm_roles=self._build_required_realm_roles(auth_config),
        )

    def _build_required_token_roles(
        self, auth_config: BrandAuthConfig, required_endpoint_roles: list[str] | None
    ) -> list[TokenRole]:
        token_roles: list[TokenRole] = [TokenRole("role-instance", auth_config.instance)]

        if required_endpoint_roles is not None:
            token_roles.extend(TokenRole("role-endpoint", item) for item in required_endpoint_roles)

        return token_roles

    def _build_required_realm_roles(self, auth_config: BrandAuthConfig) -> list[str]:
        return [auth_config.stage]

    async def __call__(self, request: Request, brand: str = Header(...)) -> Token:  # type: ignore
        token: Token = await super(BrandJwtAuth, self).__call__(request)
        self._verify_brand(token=token, request_brand=brand)
        return token

    def _verify_brand(self, token: Token, request_brand: str) -> None:
        token_has_brand: bool = token.has_role("role-brand", request_brand)

        if not token_has_brand:
            set_request_brand_to_context(None)
            self._raise_auth_error(HTTP_403_FORBIDDEN, "Missing brand.")

        set_request_brand_to_context(request_brand)
