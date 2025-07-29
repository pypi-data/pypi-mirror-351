"""Hosts the predefined configs shipped with the package."""

from pathlib import Path

from loguru import logger as log


def get_default_config_dir() -> Path:
    """Get the dir with configfiles."""
    return Path(__file__).parent


def available_config_files() -> list[Path]:
    """List all shipped configfiles."""
    files = get_default_config_dir().glob("*.toml")

    return [Path(f) for f in files]


def resolve_configfile_from_name(name: str) -> Path:
    """Loacated the path for a known configfile from just the filename.

    Only configfiles under `configs` dir is searched. In the future we might add a
    PATH-like beahavior
    """
    files = available_config_files()

    for f in files:
        if f.with_suffix("").name == name:
            return f

    msg = (
        f"Could not find any configfile matchinv {name}. known config files are {files}"
    )

    log.error(msg)
    raise ValueError(msg)
