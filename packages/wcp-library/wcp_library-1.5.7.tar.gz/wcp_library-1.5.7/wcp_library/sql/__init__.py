import asyncio
import logging
from functools import wraps
from time import sleep

import oracledb
import psycopg

logger = logging.getLogger(__name__)


def retry(f: callable) -> callable:
    """
    Decorator to retry a function

    :param f: function
    :return: function
    """

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self._retry_count = 0
        while True:
            try:
                return f(self, *args, **kwargs)
            except (oracledb.OperationalError, oracledb.DatabaseError, psycopg.OperationalError) as e:
                if isinstance(e, (oracledb.OperationalError, oracledb.DatabaseError, psycopg.OperationalError, psycopg.DatabaseError)):
                    error_obj, = e.args
                    if error_obj.full_code in self.retry_error_codes and self._retry_count < self.retry_limit:
                        self._retry_count += 1
                        logger.debug("Oracle connection error")
                        logger.debug(error_obj.message)
                        logger.info("Waiting 5 minutes before retrying Oracle connection")
                        sleep(300)
                    else:
                        raise e
                raise e
    return wrapper


def async_retry(f: callable) -> callable:
    """
    Decorator to retry a function

    :param f: function
    :return: function
    """

    @wraps(f)
    async def wrapper(self, *args, **kwargs):
        self._retry_count = 0
        while True:
            try:
                return await f(self, *args, **kwargs)
            except (oracledb.OperationalError, oracledb.DatabaseError, psycopg.OperationalError) as e:
                if isinstance(e, (oracledb.OperationalError, oracledb.DatabaseError, psycopg.OperationalError, psycopg.DatabaseError)):
                    error_obj, = e.args
                    if error_obj.full_code in self.retry_error_codes and self._retry_count < self.retry_limit:
                        self._retry_count += 1
                        logger.debug(f"{self._db_service} connection error")
                        logger.debug(error_obj.message)
                        logger.info("Waiting 5 minutes before retrying Oracle connection")
                        await asyncio.sleep(300)
                    else:
                        raise e
                else:
                    raise e
    return wrapper
