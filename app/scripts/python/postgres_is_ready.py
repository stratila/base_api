import sys
import logging
from psycopg2 import connect
from tenacity import Retrying, RetryError, stop_after_attempt, wait_exponential
from app.config import get_postgres_connection_string


# https://gist.github.com/oseme-techguy/8dc90d1808174fc4899bce448ea0e5de
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # set logger level
logFormatter = logging.Formatter("%(levelname)-2s [%(filename)s] %(message)s")
consoleHandler = logging.StreamHandler(sys.stdout)  # set streamhandler to stdout
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def postgres_is_ready():
    logger.info("Trying to connect to postgres server")
    try:
        for attempt in Retrying(
            stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, max=10)
        ):
            with attempt:
                connect(get_postgres_connection_string())
                logger.info("Connected to postgres server successfully")
    except RetryError as retry_error:
        logger.error(
            "Could not connect to postgres server with %s attempts",
            retry_error.last_attempt.attempt_number,
        )
        raise retry_error


if __name__ == "__main__":
    sys.exit(postgres_is_ready())
