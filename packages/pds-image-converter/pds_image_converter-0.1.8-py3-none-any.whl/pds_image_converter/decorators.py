from typing import Any

from attrs import define
from loguru import logger as log


def register_filter(cls: Any) -> Any:
    """Class decorator to register a new filter"""
    from pds_image_converter.registers import filters_registry

    cls = define(cls)
    log.debug(f"registering filter {cls.name()}")
    filters_registry[cls.name()] = cls
    return cls


def register_reader(cls: Any) -> Any:
    """Class decorator to register a new reader"""
    from pds_image_converter.registers import readers_registry

    cls = define(cls)
    log.debug(f"registering reader {cls.name()}")
    readers_registry[cls.name()] = cls
    return cls


def register_writer(cls: Any) -> Any:
    """Class decorator to register a new writer"""
    from pds_image_converter.registers import writers_registry

    cls = define(cls)
    log.debug(f"registering writer {cls.name()}")
    writers_registry[cls.name()] = cls
    return cls
