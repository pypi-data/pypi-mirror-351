from copy import deepcopy
from pathlib import Path

import numpy as np
import numpy.typing as npt
from attrs import define, field
from loguru import logger as log
from pdr.pds4_tools.reader.label_objects import Label, read_label

from pds_image_converter.utils import path_or_none


def anyfile_to_labelfile(inputfile: str | Path) -> Path | None:
    """Given an input file (either a data or PDS4 label file) find the label.

    Args:
        inputfile (str | Path): the input file (e.g. a dat file or any other binary)

    Raises:
        FileNotFoundError: If the expected xml does not exists.

    Returns:
        Path | None: The path to the xml labelfile.

    Note:
        inputfile does not need to exists.

    """
    inputfile = Path(inputfile)

    if inputfile.suffix in [".xml", ".lblx"]:
        log.debug(f"Input file is an XML or LBLX label file {inputfile}")
        return inputfile

    log.debug(f"Trying to locate the XML labels for {inputfile}")

    filename = inputfile.name

    def find_file_with_extensions(file: Path, extensions: list[str]) -> Path | None:
        """Find a file with the given extensions in the same directory as the input file."""
        for ext in extensions:
            candidate = file.with_suffix(ext)
            if candidate.exists():
                return candidate
        return None

    label_file = find_file_with_extensions(inputfile, [".xml", ".lblx"])

    if not label_file:
        msg = f"No label file found for {inputfile}"
        raise FileNotFoundError(msg)

    labels = read_label(label_file)

    filename_from_xml = labels.find(
        ".//{*}File_Area_Observational/{*}File/{*}file_name",
    ).text

    if filename_from_xml != filename:
        log.debug(
            f"The xml was found but it points to a different filename! {filename} vs {filename_from_xml}",
        )
        return None

    log.debug(f"Correctly located header file at {label_file}")
    return label_file


def anyfile_to_datafile(inputfile: str | Path) -> Path | None:
    """Given an input file tries to locate the expected data-file.

    PDS4 can point to more than one datafile. This tries to locate the first File under
    File_Area_Observational.

    Args:
        inputfile (str | Path): an XML labelfile for which we need to locate
        the data file.

    Raises:
        FileNotFoundError: if the datafile does not actually exists.

    Returns:
        Path | None: the path of the datafile, if found, else None.

    """
    inputfile = Path(inputfile)

    if inputfile.suffix != ".xml":
        # assuming it is already a datafile
        log.debug(f"Input file is a datafile {inputfile}")
        return inputfile

    log.debug(f"Trying to locate the datafile related to header file {inputfile}")

    labels = read_label(inputfile)

    filename_from_xml = labels.find(
        ".//{*}File_Area_Observational/{*}File/{*}file_name",
    ).text

    fullpos = inputfile.parent / Path(filename_from_xml)

    log.debug(f"Looking for file {fullpos}")

    if not fullpos.exists():
        msg = f"Data file for label {inputfile} appear to be missing."
        log.debug(msg)
        raise FileNotFoundError(msg)
        return None

    log.debug(f"Locate data file at {fullpos}")
    return fullpos


@define(repr=False)
class PDS4Image:
    """A generic PDS4 image on disk.

    THis class instance is passed through the image creation pipeline.

    Raises:
        FileNotFoundError: if the file this objects points to cannot be loaded.

    """

    file: Path = field(converter=Path)

    array: npt.NDArray[np.int_ | np.double] | None = field(default=None, init=False)
    label: Label | None = field(default=None, init=False)  # type: ignore [no-any-unimported]

    datafile: Path | None = field(default=None, converter=path_or_none, init=False)
    labelfile: Path | None = field(default=None, converter=path_or_none, init=False)

    def __repr__(self) -> str:
        return f"<{self.file}>"

    def copy(self) -> "PDS4Image":
        return deepcopy(self)

    def __attrs_post_init__(self) -> None:
        self.update()
        if not self.file.exists():
            msg = f"Input image {self.file} could not be located."
            log.error(msg)
            raise FileNotFoundError(msg)

    def update(self) -> None:
        labelfile = anyfile_to_labelfile(self.file)  # try to locate a labelfile
        if labelfile:
            self.labelfile = labelfile

        if not self.labelfile:  # no labels? treat the file as if it is data.
            log.debug(
                f"Could not find any labels for {self.file}! We will assume this file has no labels",
            )
            self.datafile = self.file
        else:
            self.datafile = anyfile_to_datafile(self.file)
