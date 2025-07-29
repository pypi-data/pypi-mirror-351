"""The serialization for the ImageConverter class."""

from functools import partial
from typing import Union

from cattr import override
from cattrs.gen import make_dict_unstructure_fn
from cattrs.preconf.tomlkit import TomlkitConverter
from cattrs.strategies import configure_tagged_union, include_subclasses

from pds_image_converter.converter import ImageConverter
from pds_image_converter.filters import Filter
from pds_image_converter.output_locator import OutputLocator
from pds_image_converter.readers import ImageReader
from pds_image_converter.registers import (
    filters_registry,
    readers_registry,
    writers_registry,
)
from pds_image_converter.writers import Writer


def build_image_converter_toml_serializer() -> TomlkitConverter:
    """Return the tomlkit serializer for the ImageConverter class."""
    converter = TomlkitConverter()

    # here below we have quite of a lot of type ignore as we are dyanamically defining
    # types unions to be used by cattrs
    filters_union = Union[tuple(filters_registry.values())]  # type: ignore[valid-type] # noqa: UP007
    readers_union = Union[tuple(readers_registry.values())]  # type: ignore[valid-type] # noqa: UP007
    writers_union = Union[tuple(writers_registry.values())]  # type: ignore[valid-type] # noqa: UP007

    # set up what cattrs will consider as a tagget union
    union_strategy = partial(configure_tagged_union, tag_name="type_name")
    configure_tagged_union(filters_union, converter)
    configure_tagged_union(readers_union, converter)
    configure_tagged_union(writers_union, converter)

    # Include all the subclasses for each base.
    include_subclasses(Filter, converter, union_strategy=union_strategy)
    include_subclasses(ImageReader, converter, union_strategy=union_strategy)
    include_subclasses(Writer, converter, union_strategy=union_strategy)

    # some customization for the classes
    hook = make_dict_unstructure_fn(
        ImageConverter,
        converter,
        # do not write out output_locator if in default state.
        output_locator=override(omit_if_default=True),
    )
    converter.register_unstructure_hook(ImageConverter, hook)

    hook = make_dict_unstructure_fn(
        OutputLocator,  # type: ignore[arg-type] # Looks like a mypy bug or wrong typing in cattrs.
        converter,
        # do not write out output_folder and relative_to_folder parameter if in default.
        output_folder=override(omit_if_default=True),
        relative_to_folder=override(omit_if_default=True),
    )
    converter.register_unstructure_hook(OutputLocator, hook)

    return converter
