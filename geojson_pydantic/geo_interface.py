"""Mixin for __geo_interface__ on GeoJSON objects."""

from typing import Any, Dict, Protocol


class _ModelDumpProtocol(Protocol):
    """Protocol for use as the type of self in the mixin."""

    def model_dump(self, *, exclude_unset: bool, **args: Any) -> Dict[str, Any]:
        """Define a dict function so the mixin knows it exists."""
        ...


class GeoInterfaceMixin:
    """Mixin for __geo_interface__ on GeoJSON objects."""

    @property
    def __geo_interface__(self: _ModelDumpProtocol) -> Dict[str, Any]:
        """GeoJSON-like protocol for geo-spatial (GIS) vector data.

        ref: https://gist.github.com/sgillies/2217756#__geo_interface
        """
        return self.model_dump(exclude_unset=True)
