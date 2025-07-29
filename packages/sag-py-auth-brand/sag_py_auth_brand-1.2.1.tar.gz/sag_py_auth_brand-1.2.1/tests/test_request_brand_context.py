from sag_py_auth_brand.request_brand_context import get_request_brand as get_request_brand_from_context
from sag_py_auth_brand.request_brand_context import set_request_brand as set_request_brand_to_context


def test__get_brand__not_set() -> None:
    # Arrange
    set_request_brand_to_context(None)

    # Act
    actual_request_brand: str = get_request_brand_from_context()

    assert not actual_request_brand


def test__get_brand__with_previously_set_brand() -> None:
    # Arrange
    set_request_brand_to_context("myBrand")

    # Act
    actual_request_brand: str = get_request_brand_from_context()

    assert actual_request_brand == "myBrand"
