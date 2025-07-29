from collections import OrderedDict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pds_image_converter.filters import Filter
    from pds_image_converter.readers import ImageReader
    from pds_image_converter.writers import Writer

filters_registry: OrderedDict[str, "Filter"] = OrderedDict()
readers_registry: OrderedDict[str, "ImageReader"] = OrderedDict()
writers_registry: OrderedDict[str, "Writer"] = OrderedDict()
