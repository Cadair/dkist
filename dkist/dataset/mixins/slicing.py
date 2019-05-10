from astropy.wcs.wcsapi import BaseLowLevelWCS, SlicedLowLevelWCS
from astropy.wcs.wcsapi.sliced_low_level_wcs import sanitize_slices
from astropy.nddata.mixins.ndslicing import NDSlicingMixin

__all__ = ['DatasetSlicingMixin']


class DatasetSlicingMixin(NDSlicingMixin):
    """
    A class to override the wcs slicing behavior of `astropy.nddata.mixins.NDSlicingMixin`.
    """

    def _slice(self, item):
        """
        Construct a set of keyword arguments to initialise a new (sliced)
        instance of the class. This method is called in
        `astropy.nddata.mixins.NDSlicingMixin.__getitem__`.

        This method extends the `~astropy.nddata.mixins.NDSlicingMixin` method
        to add support for ``missing_axis`` and ``extra_coords`` and overwrites
        the astropy handling of wcs slicing.
        """
        kwargs = super()._slice(item)

        wcs, missing_axis = self._slice_wcs_missing_axes(item)
        kwargs['wcs'] = wcs
        kwargs['missing_axis'] = missing_axis

        return kwargs

    # Implement this to stop it throwing a warning.
    def _slice_wcs(self, item):
        return

    def _slice_wcs_missing_axes(self, item):
        if self.wcs is None:
            return None, None
        elif not isinstance(self.wcs, BaseLowLevelWCS):
            raise ValueError("wcs must be an APE 14 low level WCS object")

        item = sanitize_slices(item, self.wcs.pixel_n_dim)
        return SlicedLowLevelWCS(self.wcs, item[::-1]), None
