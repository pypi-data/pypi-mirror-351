from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pds_image_converter.filters import Filter


def get_default_filters() -> list[Filter]:
    """Returns some defaults filters, mostly for testing."""
    from pds_image_converter.filters import HistogramStretch, PDS4OrientForView

    return [HistogramStretch(), PDS4OrientForView()]
