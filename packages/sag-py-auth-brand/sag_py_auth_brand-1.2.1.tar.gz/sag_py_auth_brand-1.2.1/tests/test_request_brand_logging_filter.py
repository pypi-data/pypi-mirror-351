from logging import LogRecord
from typing import cast

from sag_py_auth_brand.models import BrandLogRecord
from sag_py_auth_brand.request_brand_context import set_request_brand as set_request_brand_to_context
from sag_py_auth_brand.request_brand_logging_filter import RequestBrandLoggingFilter


def test__get_field_value__with_brand() -> None:
    # Arrange
    logging_filter = RequestBrandLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    set_request_brand_to_context("myBrand")

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert cast(BrandLogRecord, log_entry).request_brand == "myBrand"


def test__get_field_value__without_data() -> None:
    # Arrange
    logging_filter = RequestBrandLoggingFilter()
    log_entry = LogRecord("LogRecord", 0, "path.py", 100, "A test message", None, None)

    set_request_brand_to_context(None)

    # Act
    logging_filter.filter(log_entry)

    # Assert
    assert log_entry.msg == "A test message"
    assert not hasattr(log_entry, "request_brand")
