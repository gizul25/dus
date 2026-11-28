import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)

_listeners: dict[str, list[Callable[..., Any]]] = defaultdict(list)


def on(event: str, fn: Callable[..., Any]) -> None:
    _listeners[event].append(fn)


def clear_listeners() -> None:
    _listeners.clear()


def emit(event: str, **payload: Any) -> None:
    for fn in list(_listeners.get(event, [])):
        try:
            fn(**payload)
        except Exception:
            logger.exception("desk_session_event listener failed event=%s", event)