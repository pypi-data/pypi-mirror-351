from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any

from attrs import define, field
from loguru import logger as log
from PIL import Image

from pds_image_converter.decorators import register_writer

if TYPE_CHECKING:
    from pds_image_converter.image import PDS4Image


@define
class Writer:
    """base class for writers. Inherit from this to create your own writer."""

    overwrite: bool = field(default=True)

    def __call__(self, image: PDS4Image, outfile: str | Path) -> Path | None:
        outfile = self.output_filename(outfile)
        """Export image to outfile"""
        log.info(f"Exporting image {image} to {outfile}")

        if outfile.exists() and not self.overwrite:
            log.warning(f"File {outfile} already exists. Not overwriting.")
            return None

        if outfile.exists() and self.overwrite:
            log.warning(f"Overwriting {outfile}.")

        # ensure output path existis
        if not outfile.parent.exists():
            outfile.parent.mkdir(parents=True)

        self._export(image, outfile)

        if not outfile.exists():
            msg = "Expected output file could not be found."
            raise FileExistsError(msg)

        return outfile

    @abstractmethod
    def _export(self, image: PDS4Image, outfile: Path) -> None: ...

    @classmethod
    @abstractmethod
    def extensions(cls) -> list[str]:
        """File extensions suitable for this writer."""
        ...

    @property
    def output_extension(self) -> str:
        """The preferred output extension for this writer."""
        return f".{self.extensions()[0]}"

    def output_filename(self, filename: str | Path) -> Path:
        """Build an outputfilename from the input filename."""
        filename = Path(filename)

        if filename.suffix and filename.suffix.strip(".") not in self.extensions():
            log.warning(
                "Output filename has the wrong extension for this writer. \
                    Automatically changing it",
            )

        return filename.with_suffix(self.output_extension)

    @classmethod
    def name(cls) -> str:
        """Name of the writer."""
        return cls.__name__


@define
class PILWriterBase(Writer):
    """Base class for PIL-based writers."""

    def _save_array(
        self,
        image: PDS4Image,
        outfile: Path,
        *,
        rescale: bool = True,
        **kwargs: Any,
    ) -> None:
        if rescale:
            pim = Image.fromarray(image.array * 255).convert("L")
        else:
            pim = Image.fromarray(image.array)

        pim.save(outfile.as_posix(), **kwargs)


@register_writer
class JPGWriter(PILWriterBase):
    """JPG writer."""

    jpeg_quality = field(default=95)
    jpeg_optimize = field(default=True)

    def _export(self, image: PDS4Image, outfile: Path) -> None:
        self._save_array(
            image,
            outfile,
            format="jpeg",
            quality=self.jpeg_quality,
            optimize=self.jpeg_optimize,
        )

    @classmethod
    def extensions(cls) -> list[str]:
        return ["jpg", "jpeg"]


@register_writer
class PNGWriter(PILWriterBase):
    """PNG writer to export in png."""

    def _export(self, image: PDS4Image, outfile: Path) -> None:
        self._save_array(
            image,
            outfile,
            format="png",
        )

    @classmethod
    def extensions(cls) -> list[str]:
        return ["png"]


@register_writer
class TIFFWriter(PILWriterBase):
    """Experimental tiff writer."""

    rescale: bool = field(default=False)

    def _export(self, image: PDS4Image, outfile: Path) -> None:
        self._save_array(
            image,
            outfile,
            rescale=self.rescale,
            format="tiff",
        )

    @classmethod
    def extensions(cls) -> list[str]:
        return ["tif", "tiff"]
