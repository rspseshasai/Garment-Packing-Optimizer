from .first_fit_row_wise import pack_first_fit_row_wise
from .maxrects_packer import pack_with_maxrects
from .shelf_algorithms import pack_shelf_fit_bwf, pack_shelf_fit_bfdh
from .shelf_fit_bhf import pack_shelf_fit_bhf

PACKERS = [
    pack_first_fit_row_wise,
    pack_shelf_fit_bwf,
    pack_shelf_fit_bfdh,
    # pack_shelf_fit_bhf,
    pack_with_maxrects,
]
