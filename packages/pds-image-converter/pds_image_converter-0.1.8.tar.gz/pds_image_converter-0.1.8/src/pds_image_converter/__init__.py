import importlib.metadata as metadata

__version__ = metadata.version("pds_image_converter")

import sys

from loguru import logger

logger.disable("pds_image_converter")

from pds_image_converter.methods import convert_image

__all__ = ["convert_image"]


def log_enable(level: str = "INFO") -> None:
    logger.enable("pds_image_converter")
    logger.remove()
    logger.add(level=level, sink=sys.stderr)


def log_debug() -> None:
    log_enable("DEBUG")


# experiment to redirect logging
# import logging

# logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

# # Create a standard logger
# # logging.basicConfig(level=logging.DEBUG)
# standard_logger = logging.getLogger("simage_converter")


# class PropagateHandler(logging.Handler):
#     def emit(self, record: logging.LogRecord) -> None:
#         logging.getLogger(record.name).handle(record)


# logger.add(PropagateHandler(), format="{message}")
