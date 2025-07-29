import numpy as np
import numpy.typing as npt

from pds_image_converter.data import get_fpn_calibration_image


def apply_fpn_calibration(
    image: npt.NDArray[np.int_],
    start_row: int = 0,
    nrows: int = 2000,
    start_cols: int = 0,
    ncols: int = 1504,
    pattern: npt.NDArray[np.int_] | None = None,
) -> npt.NDArray[np.int_]:
    """Apply fixed pattern noise calibration to a JANUS image.

    start_row and start_cols are in a 0-based indexing format, as python.
    """

    if pattern is None:
        pattern = get_fpn_calibration_image()

    # sample the pattern appropriately
    pattern = pattern[start_row : start_row + nrows, start_cols : start_cols + ncols]
    return image - pattern
