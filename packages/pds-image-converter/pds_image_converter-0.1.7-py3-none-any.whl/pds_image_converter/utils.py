from pathlib import Path
from typing import Any

from loguru import logger as log


def path_or_none(value: Any) -> Path | None:
    log.debug(f"Conveting value {value} of type {type(value)}")
    return Path(value) if value else None
