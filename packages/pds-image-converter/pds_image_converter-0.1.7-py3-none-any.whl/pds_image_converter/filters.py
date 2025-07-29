from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import (
    Path,  # this needs to be outside the type checking or we are gonna have issue with serialization
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pds_image_converter.image import PDS4Image

import numpy as np
from astropy.visualization import PercentileInterval
from attrs import define, field
from loguru import logger as log

from pds_image_converter.data import (
    get_default_fpn_pattern_file,
    get_fpn_pattern_from_file,
)
from pds_image_converter.fpn import apply_fpn_calibration

from .decorators import register_filter

import numpy.typing as npt


class FilterError(Exception):
    pass


@define
class Filter(ABC):
    enabled: bool = field(default=True, converter=bool)
    inplace: bool = field(default=True, converter=bool, init=True)

    def __call__(self, image: PDS4Image) -> PDS4Image:
        if not self.enabled:
            log.info(f"Skipping filter {self.name()} as it is not enabled.")
            return image
        return self._compute(image=image)

    @abstractmethod
    def _compute(self, image: PDS4Image) -> PDS4Image: ...

    def make_output(self, image: PDS4Image) -> PDS4Image:
        if self.inplace:
            return image
        return image.copy()

    @classmethod
    def name(cls) -> str:
        return cls.__name__


@register_filter
class JanusFPNCorrection(Filter):
    fpn_pattern_file: Path = field(factory=get_default_fpn_pattern_file)
    fpn_pattern: npt.NDArray[np.int_] = field(default=None, init=False)

    def _compute(self, image: PDS4Image) -> PDS4Image:
        log.info(f"Using pattern at {self.fpn_pattern_file} for correcting image.")
        self.fpn_pattern = get_fpn_pattern_from_file(self.fpn_pattern_file)
        if image.label is None:
            msg = f"Could not apply filter {self.name()}"
            raise FilterError(msg)

        try:
            sframe = image.label.find(".//img:Subframe")
            first_line = int(sframe.find(".//img:first_line").text)
            first_sample = int(sframe.find(".//img:first_sample").text)
            lines = int(sframe.find(".//img:lines").text)
            samples = int(sframe.find(".//img:samples").text)
        except Exception as e:
            msg = "Could not find subframe information to correctly apply FPN"
            raise FilterError(msg) from e

        fl = first_line
        fs = first_sample

        nl = lines
        ns = samples

        log.debug(f"Applying FPN correction with subframe {fl, fs, nl, ns}")

        array = apply_fpn_calibration(
            image.array,
            fl - 1,
            nl,
            fs - 1,
            ns,
            pattern=self.fpn_pattern,
        )

        out = self.make_output(image)
        out.array = array
        return out


@register_filter
class ReplaceNotValues(Filter):
    values: list[int | float] = field(factory=lambda: [-1000])

    def _compute(self, image: PDS4Image) -> PDS4Image:
        mask = np.zeros_like(image.array).astype(bool)
        for v in self.values:
            log.info(f"Replacing pixel with values {v} with the max of the matrix.")
            mask = mask | (image.array == v)

        value = np.nanmax(image.array[~mask])

        out = self.make_output(image)
        out.array[mask] = value

        return out


@register_filter
class HistogramStretch(Filter):
    percentile: float = field(default=99, converter=float)

    def _compute(self, image: PDS4Image) -> PDS4Image:
        log.info("Performing histogram stretch")
        preprocess = PercentileInterval(self.percentile)
        array = preprocess(image.array)

        out = self.make_output(image)
        out.array = array

        return out


@register_filter
class PDS4OrientForView(Filter):
    def _compute(self, image: PDS4Image) -> PDS4Image:
        try:
            hdir = (
                image.label.find(".//disp:Display_Direction")
                .find("disp:horizontal_display_direction")
                .text
            )
            vdir = (
                image.label.find(".//disp:Display_Direction")
                .find("disp:vertical_display_direction")
                .text
            )
        except:
            raise FilterError("Missing labels to perform orientation correctly.")

        imdata = image.array
        if hdir == "Right to Left":
            log.info("Flipping the image left-to-right")
            imdata = np.fliplr(imdata)

        if vdir == "Bottom to Top":
            log.info("Flipping the image upside down")
            imdata = np.flipud(imdata)

        out = self.make_output(image)

        out.array = imdata
        return out


@register_filter
class Resize(Filter):
    factor: float = field(default=3.0, converter=float)

    def _compute(self, image: PDS4Image) -> PDS4Image:
        arr = image.array

        from PIL import Image

        im = Image.fromarray(arr)

        newwidth, newheight = (
            int(im.width // self.factor),
            int(im.height // self.factor),
        )

        log.info(f"Resizing to {newwidth} x {newheight}")

        im = im.resize((newwidth, newheight), resample=Image.LANCZOS)

        out = self.make_output(image)
        out.array = np.asarray(im)
        return out
