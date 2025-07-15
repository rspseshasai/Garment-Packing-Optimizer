from .first_fit_row_wise import pack_first_fit_row_wise
from .pack_shelf_fit_bfdh import pack_shelf_fit_bfdh
from .maxrects_packer import pack_with_maxrects

PACKERS = [
    pack_first_fit_row_wise,
    pack_shelf_fit_bfdh,
    pack_with_maxrects,
]
