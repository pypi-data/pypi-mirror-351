from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `atom_tickets.resources` module.

    This is used so that we can lazily import `atom_tickets.resources` only when
    needed *and* so that users can just import `atom_tickets` and reference `atom_tickets.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("atom_tickets.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
