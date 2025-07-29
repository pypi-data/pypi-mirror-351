from pathlib import Path

from attrs import define, field
from loguru import logger as log

from pds_image_converter.utils import path_or_none


@define
class OutputLocator:
    """Helper to create output paths for the files.

    todo: This could as well become just a function.
    """

    output_folder: Path | None = field(default=None, converter=path_or_none)
    relative_to_folder: Path | None = field(default=None, converter=path_or_none)

    def __call__(self, inpath: str | Path) -> Path:
        inpath = Path(inpath).absolute()

        log.debug("locating output path:")
        log.debug(f"output_folder: {self.output_folder}")
        log.debug(f"relative_to_folder: {self.relative_to_folder}")

        log.debug(f"type is {type(self.output_folder)}")
        log.debug(f"type is {type(self.relative_to_folder)}")

        if not self.output_folder:  # no output path -> as it is
            out = inpath.with_suffix("")

        elif self.output_folder and not self.relative_to_folder:
            out = self.output_folder / inpath.name

        elif self.output_folder and self.relative_to_folder:
            log.debug("Both output_folder and relative_path are defined")
            out = self.output_folder / inpath.relative_to(
                self.relative_to_folder.absolute()
            )

        else:
            msg = "This point in code should not be reached. That is a bug"
            raise ValueError(msg)

        return out.with_suffix("").absolute()  # no suffix
