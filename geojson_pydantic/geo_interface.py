"""Mixin for __geo_interface__ on GeoJSON objects."""

from typing import Any, Dict, Protocol


class _DictProtocol(Protocol):
    """Protocol for use as the type of self in the mixin."""

    def dict(self, *, exclude_unset: bool, **args: Any) -> Dict[str, Any]:
        """Define a dict function so the mixin knows it exists."""
        ...


class GeoInterfaceMixin:
    """Mixin for __geo_interface__ on GeoJSON objects."""

    @property
    def __geo_interface__(self: _DictProtocol) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        return self.dict(exclude_unset=True)
