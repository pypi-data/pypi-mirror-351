from sag_py_auth.models import TokenRole

from sag_py_auth_brand.brand_jwt_auth import BrandJwtAuth
from sag_py_auth_brand.models import BrandAuthConfig
from tests.helpers import build_sample_auth_config


def _verify_token_role(jwt: BrandJwtAuth, item_no: int, client: str, role: str) -> None:
    instance: TokenRole = jwt.required_roles[item_no]
    assert instance.client == client
    assert instance.role == role


def test__jwt_auth__init__with_endpoint_role() -> None:
    # Arrange
    auth_config: BrandAuthConfig = build_sample_auth_config()
    required_endpoint_roles: list[str] = ["myEndpoint"]

    # Act
    jwt = BrandJwtAuth(auth_config, required_endpoint_roles)

    # Assert
    assert len(jwt.required_realm_roles) == 1
    assert "myStage" in jwt.required_realm_roles

    assert len(jwt.required_roles) == 2
    _verify_token_role(jwt, 0, "role-instance", "myInstance")
    _verify_token_role(jwt, 1, "role-endpoint", "myEndpoint")


def test__jwt_auth__init__without_endpoint_role() -> None:
    # Arrange
    auth_config: BrandAuthConfig = build_sample_auth_config()

    # Act
    jwt = BrandJwtAuth(auth_config, None)

    # Assert
    assert len(jwt.required_realm_roles) == 1
    assert "myStage" in jwt.required_realm_roles

    assert len(jwt.required_roles) == 1
    _verify_token_role(jwt, 0, "role-instance", "myInstance")
