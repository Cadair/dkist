"""
This file contains code to lazy-load arrays from FITS files. It is designed to
minimise (virtual) memory usage and the number of open files.
"""

import abc
from pathlib import Path

import dask.array as da
import numpy as np
from dask import delayed

from astropy.io import fits
from sunpy.util.decorators import add_common_docstring

__all__ = ['BaseFITSLoader', 'AstropyFITSLoader']


common_parameters = """

    Parameters
    ----------

    externalarray: `asdf.ExternalArrayReference`
        The asdf array reference, must be to a FITS file (although this is not validated).

    basepath: `str`
        The base path for the filenames in the `asdf.ExternalArrayReference`,
        if not specified the filepaths are treated as absolute.
"""


@add_common_docstring(append=common_parameters)
class BaseFITSLoader(metaclass=abc.ABCMeta):
    """
    Base class for resolving an `asdf.ExternalArrayReference` to a FITS file.
    """

    def __init__(self, externalarray, array_container):
        self.externalarray = externalarray
        self.array_container = array_container
        # These are needed for this object to be array-like
        self.shape = self.externalarray.shape
        self.ndim = len(self.shape)
        self.dtype = self.externalarray.dtype

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "<FITS array in {0.fileuri} shape: {0.shape} dtype: {0.dtype}>".format(self.externalarray)

    def __array__(self):
        return self[:]

    def __getitem__(self, slc):
        return self.fits_array[slc]

    @property
    def basepath(self):
        return self.array_container.basepath

    @property
    def absolute_uri(self):
        """
        Construct a non-relative path to the file, using ``basepath`` if provided.
        """
        if self.basepath:
            return self.basepath / self.externalarray.fileuri
        else:
            return Path(self.externalarray.fileuri)


@add_common_docstring(append=common_parameters)
class AstropyFITSLoader(BaseFITSLoader):
    """
    Resolve an `~asdf.ExternalArrayReference` to a FITS file using `astropy.io.fits`.
    """

    def __getitem__(self, slc):
        if not self.absolute_uri.exists():
            # Use np.broadcast_to to generate an array of the correct size, but
            # which only uses memory for one value.
            return da.from_delayed(delayed(np.broadcast_to)(np.nan, self.shape) * np.nan,
                                   self.shape, self.dtype)

        supports_section = hasattr(fits.CompImageHDU, "section")
        with fits.open(self.absolute_uri,
                       memmap=not supports_section,  # don't load the whole array into memory, let dask access the part it needs
                       do_not_scale_image_data=True,  # don't scale as that would cause it to be loaded into memory
                       mode="denywrite") as hdul:

            hdul.verify('fix')
            hdu = hdul[self.externalarray.target]
            if supports_section:
                return hdu.section[slc]
            return hdu.data[slc]
