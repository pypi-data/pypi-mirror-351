from pds_image_converter.converter import ImageConverter
from pds_image_converter.filters import HistogramStretch

from astropy.visualization import PercentileInterval
from PIL import Image


def quick_save_to_jpg(data, out_file):
    preprocess = PercentileInterval(99)
    data = preprocess(data)

    pim = Image.fromarray(data * 255).convert("L")

    pim.save(out_file, quality=97, optimize=True)
