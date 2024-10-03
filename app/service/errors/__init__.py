from contextlib import contextmanager
from dataclasses import dataclass
from app.database.errors import DatabaseError
from http import HTTPStatus


@dataclass
class ServiceErrorDescription:
    error_code: int
    message: str


class ServiceError(Exception):
    def __init__(self, http_code: HTTPStatus, error_code, message) -> None:
        self.http_code = http_code
        self.error_code = error_code
        self.message = message
        super().__init__(f"[{self.error_code}] {self.message}")

    def __dict__(self):
        err_desc = ServiceErrorDescription(self.error_code, self.message).__dict__
        return {"http_code": self.http_code.value, **err_desc}


@contextmanager
def cm_error_handler(*args, **kwargs):
    try:
        yield
    except DatabaseError as exc:
        raise ServiceError(
            HTTPStatus.BAD_REQUEST,
            exc.error_code,
            f"Databsase error: {exc.message}",
        )
