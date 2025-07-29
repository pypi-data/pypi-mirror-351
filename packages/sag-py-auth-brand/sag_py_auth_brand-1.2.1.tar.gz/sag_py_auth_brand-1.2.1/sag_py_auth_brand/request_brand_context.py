from contextvars import ContextVar

_request_brand: ContextVar[str | None] = ContextVar("request_brand", default=None)


def get_request_brand() -> str:
    """Gets the context local brand. This is always the brand of the request.
    See library contextvars for details.

    Returns: The brand
    """
    current_brand: str | None = _request_brand.get("")
    return current_brand or ""


def set_request_brand(brand_to_set: str | None) -> None:
    """Sets the context local brand. This is always the brand of the request.
    See library contextvars for details."""
    _request_brand.set(brand_to_set)
