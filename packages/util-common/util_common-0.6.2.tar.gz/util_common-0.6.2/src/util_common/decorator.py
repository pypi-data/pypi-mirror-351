import asyncio
import logging
import os
import re
import time
import warnings
from functools import wraps
from typing import Any, Callable, Optional, Tuple

from util_common._log import log


def deprecated(src_func: Optional[str] = None, replacement: Optional[str] = None):
    def decorator(obj):
        nonlocal src_func
        if not src_func:
            src_func = obj.__name__

        message = f"{src_func} is deprecated and will be removed in a future version."
        if replacement:
            message += f" Use {replacement} instead."

        if isinstance(obj, type):
            # For classes
            original_init = obj.__init__

            @wraps(original_init)
            def new_init(self, *args, **kwargs):
                warnings.warn(message, DeprecationWarning, stacklevel=2)
                original_init(self, *args, **kwargs)

            obj.__init__ = new_init
            return obj
        else:
            # For functions
            @wraps(obj)
            def wrapper(*args, **kwargs):
                warnings.warn(message, DeprecationWarning, stacklevel=2)
                return obj(*args, **kwargs)

            return wrapper

    return decorator


def ticktock(name=None, print_fn=log.info):
    def decorator(fn: Callable):
        def _info(elapsed):
            return (fn.__name__ if name is None else name) + f">>> Elapsed time: {elapsed:.4f} secs"

        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = await fn(*args, **kwargs)
            elapsed = time.time() - start_time
            print_fn(_info(elapsed))
            return result

        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = fn(*args, **kwargs)
            elapsed = time.time() - start_time
            print_fn(_info(elapsed))
            return result

        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry(max_attempts: int, delay: int):
    def decorator(fn: Callable):

        def sync_wrapper(*args, **kwargs):
            attempts = 0
            error = None
            while attempts < max_attempts:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    log.error(
                        f">>>{fn.__name__} Attempt {attempts + 1} failed. "
                        f"Retry in {delay} seconds."
                    )
                    attempts += 1
                    time.sleep(delay)
                    error = e
            raise Exception(f">>> Max attempts exceeded.\nError: {error}")

        return sync_wrapper

    return decorator


def connect_pg(postgres, dbname):

    import psycopg2

    def parse_pg_connection(pg_conn) -> Tuple:
        regex = '(.+):(.+)@(.+):(.+)'
        matches = re.match(regex, pg_conn, re.M | re.I)
        if matches is None:
            raise Exception("Invalid Postgres connection string!")
        user, password, host, port = matches.groups()
        return user, password, host, port

    def decorator(function):
        def wrapper(**kwargs):
            user, password, host, port = parse_pg_connection(postgres)
            con = psycopg2.connect(
                user=user, password=password, host=host, port=port, database=dbname
            )
            logging.info("Database opened successfully")
            cur = con.cursor()
            result = function(cur=cur, **kwargs)
            con.commit()
            con.close()
            logging.info("Database closed successfully")
            return result

        return wrapper

    return decorator


def proxy(http_proxy: str = "", https_proxy: str = "", all_proxy: str = ""):
    def decorator(fn: Callable):
        def _get_proxy():
            http_proxy = os.environ.get("http_proxy", "")
            https_proxy = os.environ.get("https_proxy", "")
            all_proxy = os.environ.get("all_proxy", "")
            return http_proxy, https_proxy, all_proxy

        def _set_proxy(http_proxy, https_proxy, all_proxy):
            os.environ["http_proxy"] = http_proxy
            os.environ["https_proxy"] = https_proxy
            os.environ["all_proxy"] = all_proxy

        def sync_wrapper(*args, **kwargs) -> Any:
            org_http_proxy, org_https_proxy, org_all_proxy = _get_proxy()
            _set_proxy(http_proxy, https_proxy, all_proxy)
            try:
                result = fn(*args, **kwargs)
            finally:
                _set_proxy(org_http_proxy, org_https_proxy, org_all_proxy)
            return result

        return sync_wrapper

    return decorator
