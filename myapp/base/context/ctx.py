from collections import UserDict
from contextvars import copy_context
from typing import Any
from myapp.base.context import _request_context_var
from myapp.base.context.errors import ConfigurationError, ContextDoesNotExistError


class _RequestContext(UserDict):
    """
    A mapping with dict-like interface.
    It is using request context as a data store.
    Can be used only if context has been created in the middleware.

    If you know Flask, it can be compared to g object.
    ref https://github.com/tomwojcik/starlette-context/blob/v0.3.6/starlette_context/ctx.py
    """

    def __init__(self, *args: Any, **kwargs: Any):  # noqa
        # not calling super on purpose
        if args or kwargs:
            raise ConfigurationError("Can't instantiate with attributes")

    @property
    def data(self) -> dict:  # type: ignore
        """Dump this to json.

        Object itself it not serializable.
        """
        try:
            return _request_context_var.get()
        except LookupError:
            raise ContextDoesNotExistError()

    def exists(self) -> bool:
        return _request_context_var in copy_context()

    def copy(self) -> dict:  # type: ignore
        """Read only context data."""
        import copy

        return copy.copy(self.data)

    def __repr__(self) -> str:
        # Opaque type to avoid default implementation
        # that could try to look into data while out of request cycle
        try:
            return f"<{__name__}.{self.__class__.__name__} {self.data}>"
        except ContextDoesNotExistError:
            return f"<{__name__}.{self.__class__.__name__} {dict()}>"

    def __str__(self):
        try:
            return str(self.data)
        except ContextDoesNotExistError:
            return str({})


request_context = _RequestContext()
