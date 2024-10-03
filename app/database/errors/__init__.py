from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    OperationalError,
    ProgrammingError,
    InterfaceError,
    TimeoutError,
)
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseErrorDescription:
    error_code: int
    message: str


class DatabaseError(Exception):
    def __init__(self, error_code, message) -> None:
        self.error_code = error_code
        self.message = message
        self.sed_string = f"[{error_code}] {message}"
        super().__init__(self.sed_string)

    def __dict__(self):
        return self.sed.__dict__()


class SqlAlchemyDatabaseError(DatabaseError):
    """A class that wraps SqlAlchemy errors and dis
    them to the user in a more user-friendly way."""

    integrity_error_msg = "An integrity error occurred while accessing the database: {}"
    data_error_msg = "A data error occurred while accessing the database: {}"
    operational_error_msg = "A database error occurred while accessing the database: {}"
    programming_error_msg = (
        "A programming error occurred while accessing the database: {}"
    )
    interface_error_msg = "An interface error occurred while accessing the database: {}"
    timeout_error_msg = "A timeout error occurred while accessing the database: {}"

    error_messages = {
        IntegrityError: integrity_error_msg,
        DataError: data_error_msg,
        OperationalError: operational_error_msg,
        ProgrammingError: programming_error_msg,
        InterfaceError: interface_error_msg,
        TimeoutError: timeout_error_msg,
    }

    def __init__(self, original_exception, error_code, message):
        self.original_exception = original_exception
        error_type = type(original_exception)
        error_message = self.error_messages.get(
            error_type, "An error occurred while accessing the database: {}"
        )
        self.message = error_message.format(str(original_exception))
        super().__init__(error_code, message)
