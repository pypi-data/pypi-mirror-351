# -*- coding: utf-8 -*-
import logging
from functools import wraps

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from pathlib import Path

from search_me.exceptions import ApiError, SearchEngineParamsError

logger = logging.getLogger(__name__)


def retry(exceptions):
    """Retry func n times

    Parameters
    ----------
    exceptions : tuple
        Supported exceptions
    """
    def wrapper(func):
        """Retry func n times wrapper

        Parameters
        ----------
        func : function
            Function
        """
        async def inner(*args, **kwargs):
            """Retry func n times

            Returns
            -------
            any
                Any value
            """
            attempt = 0
            result = None
            obj = args[0]
            attempt_limit = obj.default_kwargs.get("retry", 3)
            while attempt < attempt_limit:
                try:
                    result = await func(*args, **kwargs)
                except exceptions as exc:
                    logger.error(f"Run {func.__qualname__}. Attempt {attempt}. Exception {str(exc)}")
                    attempt += 1
                else:
                    break
            return result
        return inner
    return wrapper


def check_params(*params):
    """Check params in kwargs
    """
    def wrapper(func):
        """Check params in kwargs wrapper

        Parameters
        ----------
        func : function
            Function
        """
        async def inner(*args, **kwargs):
            """Check params in kwargs

            Returns
            -------
            generator
                Generator

            Raises
            ------
            SearchEngineParamsError
                Raised if not set necessary fields
            """
            s1 = {*kwargs.keys()}
            s2 = {*params}
            if s2.issubset(s1):
                result = await func(*args, **kwargs)
                return result
            raise SearchEngineParamsError(params)
        return inner
    return wrapper


def count_calls(func):
    """Count number of calls for instances

    Parameters
    ----------
    func : function
        Function

    Returns
    -------
    Any
        Item
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        item = func(*args, **kwargs)
        if item:
            args[0].calls[item] += 1
        return item
    return wrapper


def validate_api_key(func):
    """Raise api error

    Parameters
    ----------
    func : function
        Function

    Returns
    -------
    Any
        Function result

    Raises
    ------
    SearchMeApiError
        If api key not valid
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, FileNotFoundError) as e:
            raise ApiError() from e
    return wrapper


def get_current_dir():
    """Get current dir

    Returns
    -------
    str
        Current dir
    """
    try:
        return files(__package__)
    except ModuleNotFoundError:
        return Path(__file__).parent
