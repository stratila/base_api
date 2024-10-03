import logging
import traceback
from contextlib import contextmanager
from sqlalchemy import exc, Connection
from app.database.errors import DatabaseError, SqlAlchemyDatabaseError
from app.database.errors.messages import DATABASE_COMMON_ERROR

logger = logging.getLogger(__name__)


class BaseDataAccessObject:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    @staticmethod
    @contextmanager
    def cm_error_handler(*args, **kwargs):
        """
        Context manager for error handling
        """
        try:
            yield
        except exc.SQLAlchemyError as err:
            sqlalchemy_exc = SqlAlchemyDatabaseError(
                err, DATABASE_COMMON_ERROR.error_code, DATABASE_COMMON_ERROR.message
            )
            # log detailed message
            logger.error(
                f"Exception: {err}, Message: {sqlalchemy_exc.message}, "
                f"Trace:\n{traceback.print_exc()}"
            )
            raise sqlalchemy_exc
        except DatabaseError as err:
            logger.error(
                f"Exception: {err}, Message: {err.message}, "
                f"Trace:\n{traceback.print_exc()}"
            )
            raise err
