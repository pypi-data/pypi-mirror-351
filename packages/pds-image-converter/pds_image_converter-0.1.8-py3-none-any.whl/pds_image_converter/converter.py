"""The converter class performing the actual conversion."""

from pathlib import Path
from typing import Any, TypeVar

from attrs import define, field
from cattrs.preconf.tomlkit import TomlkitConverter
from loguru import logger as log

from pds_image_converter.filters import Filter, FilterError
from pds_image_converter.output_locator import OutputLocator

from .config import get_default_filters
from .readers import ImageReader, PDS4ToolsReader
from .writers import JPGWriter, Writer

T = TypeVar("T")

# currently not used.
# def set_config_on_item(item, config, obj_debug_name=None):
#     if obj_debug_name is None:
#         obj_debug_name = item.__class__.__name__

#     for key, value in config.items():
#         log.debug(f"Setting {key} on {obj_debug_name}: value {value}")
#         if hasattr(item, key):
#             setattr(item, key, value)
#         else:
#             log.warning(
#                 f"Option {key} does not exists on object {obj_debug_name}.
# Check your configuration.",
#             )


class ImageConversionError(Exception):
    """Exception raised when the conversion fails."""


@define
class ImageConverter:
    """A configurable image converter.

    It is used to produce derived products from pds images, mostly.
    But it can be adapted to any simple image processing needs.
    """

    # known readers and filters to be applied, can be configured by the user
    reader: ImageReader = field(factory=PDS4ToolsReader)
    filters: list[Filter] = field(factory=get_default_filters)
    writers: list[Writer] = field(factory=lambda: [JPGWriter()])
    output_locator: OutputLocator = field(factory=OutputLocator)

    skip_if_exists: bool = field(default=False, converter=bool)

    def __call__(self, infile: Path | str, outfile: Path | str = "") -> None:
        """Perform a conversion from infile to outfile."""
        if not outfile:
            log.debug(
                "No output path provided. Using the currently set output locator to \
                    generate a path.",
            )
            outfile = self.output_locator(infile)
            log.debug(f"Generated output path is {outfile}")

        if self.skip_if_exists and self.output_exists(outfile):
            log.warning("The outputs for this image is already in place. Skipping")
            return

        pds4_image = self.reader(inputfile=infile)

        for i, current_filter in enumerate(self.filters):
            filter_string = f"{current_filter.name()} ({i + 1}/{len(self.filters)})"
            log.info(
                f"Applying filter {filter_string}",
            )
            try:
                pds4_image = current_filter(pds4_image)

            except FilterError as e:
                msg = f"Filter {current_filter.name()} could not be applied and the \
                        output file might be invalid."
                raise ImageConversionError(msg) from e

            except Exception as e:
                msg = f"Filter {current_filter.name()} could not be applied due to an \
                    unexpeced error raised by the filter."
                raise ImageConversionError(msg) from e

        for j, w in enumerate(self.writers):
            log.info(f"Running writer {w.name()} ({j + 1}/{len(self.writers)})")
            w(pds4_image, outfile)

    def output_exists(self, outfilename: str | Path) -> bool:
        """Say if output already there."""
        status = [w.output_filename(outfilename).exists() for w in self.writers]
        return all(status)

    def make_exif(self) -> bytes:
        """Build exif bytes content. Just a stub."""
        raise NotImplementedError
        # import piexif
        # # here is just a stub for future ref.
        # exif_dict = {
        #     "Exif": {
        #         piexif.ExifIFD.UserComment: "Your custom comment".encode("ASCII"),
        #         piexif.ExifIFD.DateTimeOriginal: "2022:01:01T00:00:00",
        #         piexif.ExifIFD.ImageUniqueID: "123456789",
        #     },
        # }

        # return piexif.dump(exif_dict)

    @classmethod
    def serializer(cls) -> TomlkitConverter:
        """Get the cattrs serializer (toml) for self."""
        from pds_image_converter.serializer import build_image_converter_toml_serializer

        return build_image_converter_toml_serializer()

    def to_config_dict(self) -> Any:
        """Get configuration as a dict."""
        c = self.serializer()
        return c.unstructure(self)

    @classmethod
    def from_config_dict(cls, config: Any) -> "ImageConverter":
        """Build an ImageConverter from a config dict."""
        c = cls.serializer()
        return c.structure(config, cls)

    def save_config(self, file: str | Path) -> None:
        """Save config to file (toml)."""
        with Path(file).open("w") as r:
            c = self.serializer()
            r.write(c.dumps(self))

    @classmethod
    def from_config(cls, file: str | Path) -> "ImageConverter":
        """Load config from file and make an ImageConverter instance."""
        with Path(file).open() as f:
            c = cls.serializer()
            return c.loads(f.read(), cls)
