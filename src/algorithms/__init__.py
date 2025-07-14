"""
Registry of available packing algorithms.
"""

from .first_fit_row_wise import pack_first_fit_row_wise
from .shelf_fit import pack_shelf_fit
from .maxrects_packer import pack_with_maxrects

PACKERS = [
    pack_first_fit_row_wise,
    pack_shelf_fit,
    pack_with_maxrects,
]
