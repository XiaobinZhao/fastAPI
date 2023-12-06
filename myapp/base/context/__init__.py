from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Optional, Any, Dict, Iterator


_request_context_var: ContextVar[Dict[Any, Any]] = ContextVar("request_context_var")
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
# Celery extension
celery_parent_id_var: ContextVar[Optional[str]] = ContextVar('celery_parent', default=None)
celery_current_id_var: ContextVar[Optional[str]] = ContextVar('celery_current', default=None)


@contextmanager
def request_cycle_context(
    initial_data: Optional[dict] = None,
) -> Iterator[None]:
    """Creates and resets a starlette-context context.

    Used in the Context and Raw middlewares, but can also be used to
    create a context out of a proper request cycle, such as in unit
    tests.
    ref https://github.com/tomwojcik/starlette-context/blob/v0.3.6/starlette_context/__init__.py
    """
    if initial_data is None:
        initial_data = {}
    token: Token = _request_context_var.set(initial_data.copy())
    yield
    _request_context_var.reset(token)


from myapp.base.context.ctx import request_context  # noqa: E402

__all__ = ["request_context", "request_cycle_context", "request_id_var"]

