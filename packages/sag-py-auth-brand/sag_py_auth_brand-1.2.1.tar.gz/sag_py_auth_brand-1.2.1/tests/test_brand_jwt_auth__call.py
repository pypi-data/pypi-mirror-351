from typing import Literal

import pytest
from fastapi import Request
from sag_py_auth.models import Token
from starlette.datastructures import Headers

from sag_py_auth_brand.brand_jwt_auth import BrandJwtAuth
from tests.helpers import build_sample_jwt_auth, get_token

pytest_plugins: tuple[Literal["pytest_asyncio"]] = ("pytest_asyncio",)


async def mock_jwt_auth_call(_: BrandJwtAuth, __: Request) -> Token:
    return get_token(None, None)


def mock_verify_brand(_: BrandJwtAuth, token: Token, request_brand: str) -> None:
    if token:
        token.token_dict["_verify_brand"] = "True"
        token.token_dict["_brand"] = request_brand


@pytest.mark.asyncio
async def test__call__correctly_processes_request(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    jwt: BrandJwtAuth = build_sample_jwt_auth(None)

    monkeypatch.setattr("sag_py_auth.JwtAuth.__call__", mock_jwt_auth_call)
    monkeypatch.setattr("sag_py_auth_brand.brand_jwt_auth.BrandJwtAuth._verify_brand", mock_verify_brand)

    request: Request = Request(scope={"type": "http"})
    request._headers = Headers({"Authorization": "Bearer validToken"})

    # Act
    actual: Token = await jwt(request, "mybrand")

    # Assert - Verify that all steps have been executed
    # Comment: the calls of the mocked function are verified via variables,
    # alternatively one could use unittest.mock and assertions like assert_called on the functions.
    assert actual.get_field_value("typ") == "Bearer"
    assert actual.get_field_value("azp") == "public-project-swagger"
    assert actual.get_field_value("_verify_brand") == "True"
    assert actual.get_field_value("_brand") == "mybrand"
