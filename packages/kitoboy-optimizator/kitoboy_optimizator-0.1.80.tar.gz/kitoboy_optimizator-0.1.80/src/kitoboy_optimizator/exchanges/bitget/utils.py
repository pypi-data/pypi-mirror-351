from typing import Callable
import functools
from .exceptions import BitgetAPIException, BitgetParamsException, BitgetRequestException


def safe_api_request(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except BitgetAPIException as e:
                print("Bitget invalid API request", e.status_code, e.message, sep=" | ")
            except BitgetRequestException as e:
                print("Bitget API request failed", e.status_code, e.message, sep=" | ")
            except BitgetParamsException as e:
                print("Bitget API invalid request params", e.status_code, e.message, sep=" | ")
            except Exception as e:
                print("Bitget unknown API error", e, sep=" | ")
                raise e

        return wrapper