"""Methods to retrieve data-files that are currently distributed within the package."""

from functools import lru_cache
from pathlib import Path

import numpy as np
import numpy.typing as npt
from loguru import logger as log


def get_data_path() -> Path:
    """Get this path at runtime."""
    return Path(__file__).parent


def get_default_fpn_pattern_file() -> Path:
    """Get the path to the default fpn pattern."""
    return get_data_path().joinpath("fpn_calibration_pipeline.npz")


@lru_cache
def get_fpn_pattern_from_file(file: str | Path) -> npt.NDArray[np.int_]:
    """Load the fpn pattern from file."""
    return np.load(file)["arr_0"]  # type: ignore [no-any-return]


@lru_cache
def get_fpn_calibration_image() -> npt.NDArray[np.int_]:
    """Return the FPN calibration image.

    The pattern needs to be subtracted from the image to suppress the FPN.
    """
    log.debug("Loading FPN calibration pattern")
    return get_fpn_pattern_from_file(get_default_fpn_pattern_file())
