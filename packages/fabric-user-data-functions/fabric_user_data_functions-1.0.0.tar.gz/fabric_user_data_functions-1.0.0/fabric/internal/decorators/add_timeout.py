# flake8: noqa: I003
from functools import wraps
import queue
import threading
import time
import traceback
from typing import Callable, Optional, TypeVar

from fabric.functions.udf_exception import UserDataFunctionTimeoutError
from fabric.internal.logging import UdfLogger
from fabric.internal.decorators.function_parameter_keywords import CONTEXT_PARAMETER

from .constants import Timeout

import asyncio
import inspect
import functools

T = TypeVar('T')

logger = UdfLogger(__name__)

def add_timeout(func: Callable[..., T], function_timeout: int = Timeout.FUNC_TIMEOUT_IN_SECONDS):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # This will raise a TimeoutError if the function takes longer than the timeout
            loop = asyncio.get_event_loop()
            func_task = None

            if inspect.iscoroutinefunction(func):
                # Since user code can contain blocking code, we need to run it in a thread pool
                def blocking_function_runner():
                    return asyncio.run(func(*args, **kwargs))
                
                func_task = loop.run_in_executor(None, blocking_function_runner)
            else:
                func_task = loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

            return await asyncio.wait_for(func_task, timeout=function_timeout)

        except asyncio.TimeoutError:
            return UserDataFunctionTimeoutError(function_timeout)
        
    return wrapper