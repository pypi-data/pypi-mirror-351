from logging import LogRecord

from sag_py_auth.models import AuthConfig


class BrandAuthConfig(AuthConfig):
    def __init__(self, issuer: str, audience: str, instance: str, stage: str) -> None:
        super().__init__(issuer, audience)
        self.instance: str = instance
        self.stage: str = stage


class BrandLogRecord(LogRecord):
    # The original brand of the request
    request_brand: str
