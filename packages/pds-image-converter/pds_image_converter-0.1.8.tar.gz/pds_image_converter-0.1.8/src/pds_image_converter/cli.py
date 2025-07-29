"""Cli to support user-operations of the module."""

from __future__ import annotations

import multiprocessing
import sys
from functools import partial
from typing import Literal

import click
from loguru import logger as log

from pds_image_converter.methods import convert_image
from pds_image_converter.utils import path_or_none


@click.command()
@click.argument("infiles", type=click.Path(exists=True), nargs=-1)
@click.option(
    "-o",
    "--out-folder",
    type=click.Path(),
    help="Override output path to point to another folder",
)
@click.option(
    "-r",
    "--relative-to",
    type=click.Path(),
    help="Part of infile to be used as relative root when saving the files",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(),
    help="Config file to use to perform the conversion. You can also pass just the name"
    " (without extension) for the defaults configs.",
)
@click.option(
    "-n",
    "--cpu",
    type=int,
    default=-1,
    help="Numeber of parallel processes to use. -1 means all available.",
    show_default=True,
)
@click.option("-l", "--loglevel", help="Logging level", default="WARNING")
# @click.option(
#     "-O",
#     "--option",
#     is_flag=False,
#     help="Override in config options [STILL NOT SUPPORTED]",
#     multiple=True,
# )
def convert_image_cli(  # noqa: D417, PLR0913
    infiles: list[click.Path],
    out_folder: click.Path,
    relative_to: click.Path,
    config: click.Path | str,
    cpu: int,
    loglevel: Literal["DEBUG", "INFO", "WARNING", "ERROR"],
    # option: Any, \ to be implemented
) -> None:
    """Command-line interface function that converts an input PDS4 to other formats.

    The tool takes a single config file which defines reading and output options
    together with an optional
    set of filters that are applied to the image data before writing.

    Arguments:
        INFILES (str): One or more paths to the input files.

    """
    from loguru import logger

    logger.enable("pds_image_converter")
    logger.remove()
    logger.add(level=loglevel, sink=sys.stderr)

    if not infiles:
        log.info("No input files. Nothing done.")
        return

    log.debug(f"Converting {infiles} to JPG")

    log.info(f"Config {config}")

    if cpu == -1:
        cpu = multiprocessing.cpu_count()

    log.debug(f"Type of config is {type(config)}")

    with multiprocessing.Pool(processes=cpu) as pool:
        pool.map(
            partial(
                convert_image,
                configfile=str(config),
                output_folder=path_or_none(out_folder),
                relative_to=path_or_none(relative_to),
            ),
            infiles,
        )


def main() -> None:
    """Entry point."""
    convert_image_cli()


if __name__ == "__main__":
    """Can use this as script if needed."""
    main()
