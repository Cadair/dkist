import dkist.config as _config
from dkist.io.array_containers import (BaseFITSArrayContainer, DaskFITSArrayContainer,
                                       NumpyFITSArrayContainer)
from dkist.io.loaders import AstropyFITSLoader, BaseFITSLoader

__all__ = ['BaseFITSLoader', 'AstropyFITSLoader', 'BaseFITSArrayContainer',
           'NumpyFITSArrayContainer', 'DaskFITSArrayContainer', 'conf']


class Conf(_config.ConfigNamespace):
    """
    Configuration Parameters for the IO Package.
    """

    preferred_fits_library = _config.ConfigItem('astropy',
                                                "Name of the preferred FITS module.")


conf = Conf()
