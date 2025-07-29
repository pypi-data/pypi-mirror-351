"""Implements readers classes that can be used."""

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from attrs import define, field
from JanusReader import JanusReader
from pdr.pds4_tools import pds4_read
from pdr.pds4_tools.reader.array_objects import ArrayStructure
from pdr.pds4_tools.reader.general_objects import StructureList
from pdr.pds4_tools.reader.label_objects import Label

from pds_image_converter.image import PDS4Image

from .decorators import register_reader


@define
class ImageReader(ABC):
    """Base interface for any reader supported by the converter."""

    @classmethod
    def name(cls) -> str:
        """Name of the reader."""
        return cls.__name__

    @abstractmethod
    def __call__(self, inputfile: str | Path) -> PDS4Image:
        """Read the input file into a PDS4Image class or raise an error.

        Need to be implemented by real classes.
        """
        ...


@register_reader
class JanusPDS4Reader(ImageReader):
    """Reader that uses the official JANUS Reader module."""

    _data: JanusReader = field(init=False, default=None, repr=False)

    def __call__(self, inputfile: str | Path) -> PDS4Image:
        im = PDS4Image(inputfile)
        self._data = JanusReader(im.datafile)
        im.array = self._data.image
        im.label = Label.from_file(im.labelfile)
        return im


@register_reader
class PILImageReader(ImageReader):
    """Experimental PIL-based reader."""

    def __call__(self, inputfile: str | Path) -> PDS4Image:
        from numpy import asarray
        from PIL import Image

        im = PDS4Image(inputfile)

        image = Image.open(inputfile)
        data = asarray(image)

        im.array = data
        # im.label = Label() # no labels sorry
        return im


@register_reader
class PDS4ToolsReader(ImageReader):
    """PDS4-tools-based reader."""

    _data: StructureList = field(init=False, default=None, repr=False)

    def __call__(self, inputfile: str | Path) -> PDS4Image:
        im = PDS4Image(inputfile)

        labelfile = im.labelfile

        if labelfile is None:
            msg = f"Could not locate the label file for inut file {inputfile}. \
                Which is necessary for this Reader"
            raise FileExistsError(msg)

        self._data = pds4_read(labelfile.as_posix(), quiet=True)

        image_struct = None
        for item in self._data:
            if isinstance(item, ArrayStructure) and item.meta_data["axes"] == 2:
                image_struct = item
                break

        if not image_struct:
            msg = "Could not locate any Array Stcuture (images) with 2 dimension in \
                  the dataset."
            raise ValueError(msg)

        imdata = np.array(image_struct.data)

        im.array = imdata
        im.label = self._data.label
        return im
