import os
import glob
from pathlib import Path

import asdf
import numpy as np
import astropy.units as u
from astropy.io import fits
from astropy.time import Time
from astropy.modeling.models import Shift, AffineTransformation2D, Pix2Sky_TAN, RotateNative2Celestial, Multiply

import gwcs
from gwcs import coordinate_frames as cf
from gwcs.lookup_table import LookupTable

import sunpy.map
from sunpy.time import parse_time


def map_to_transform(smap):
    # crval1u, crval2u = smap.reference_coordinate.Tx, smap.reference_coordinate.Ty
    # cdelt1u, cdelt2u = smap.scale
    # pcu = smap.rotation_matrix * u.arcsec

    # # First, shift the reference pixel from FITS (1) to Python (0) indexing
    # crpix1, crpix2 = u.Quantity(smap.reference_pixel) - 1 * u.pixel
    # # Then FITS WCS uses the negative of this value as the shift.
    # shiftu = Shift(-crpix1) & Shift(-crpix2)

    # # Next we define the Affine Transform.
    # # This also includes the pixel scale operation by using equivalencies
    # scale_e = {a: u.pixel_scale(scale) for a, scale in zip('xy', smap.scale)}
    # rotu = AffineTransformation2D(pcu, translation=(0, 0) * u.arcsec)
    # rotu.input_units_equivalencies = scale_e

    # # Handle the projection
    # tanu = Pix2Sky_TAN()

    # # Rotate from native spherical to celestial spherical coordinates
    # skyrotu = RotateNative2Celestial(crval1u, crval2u, 180 * u.deg)

    # # Combine the whole pipeline into one compound model
    # transu = shiftu | rotu | tanu | skyrotu

    crpix1u, crpix2u = u.Quantity(smap.reference_pixel)-1*u.pixel
    crval1u, crval2u = smap.reference_coordinate.Tx, smap.reference_coordinate.Ty
    cdelt1u, cdelt2u = smap.scale
    pcu = smap.rotation_matrix * u.arcsec
    shiftu = Shift(-crpix1u) & Shift(-crpix2u)
    scaleu = Multiply(cdelt1u) & Multiply(cdelt2u)
    rotu = AffineTransformation2D(pcu, translation=(0, 0)*u.arcsec)
    tanu = Pix2Sky_TAN()
    skyrotu = RotateNative2Celestial(crval1u, crval2u, 180*u.deg)
    transu = shiftu | scaleu | rotu | tanu | skyrotu
    transu.rename("spatial")

    return transu


def references_from_filenames(filename_array, relative_to=None):
    """
    Given an array of paths to FITS files create a set of nested lists of
    `asdf.external_reference.ExternalArrayReference` objects with the same
    shape.
    """

    from astropy.io.fits.hdu.base import BITPIX2DTYPE
    from asdf.tags.core.external_reference import ExternalArrayReference

    reference_array = np.empty_like(filename_array, dtype=object)
    for i, filepath in enumerate(filename_array.flat):
        with fits.open(filepath) as hdul:
            hdu_index = 0
            hdu = hdul[hdu_index]
            dtype = BITPIX2DTYPE[hdu.header['BITPIX']]
            shape = tuple(reversed(hdu.shape))

            # Convert paths to relative paths
            relative_path = filepath
            if relative_to:
                relative_path = os.path.relpath(filepath, relative_to)

            reference_array.flat[i] = ExternalArrayReference(
                relative_path, hdu_index, dtype, shape)

    return reference_array.tolist()


def main():
    path = Path('~/Git/DKIST/dkist/dkist/data/test/EIT').expanduser()
    files = glob.glob(str(path / '*.fits'))

    files.sort()
    files = np.array(files)

    # For each image get:
    # the index
    inds = []
    # the time
    times = []
    # the dt from the first image
    seconds = []

    for i, filepath in enumerate(files):
        with fits.open(filepath) as hdul:
            header = hdul[0].header
        time = parse_time(header['DATE-OBS'])
        if i == 0:
            start_time = time
        inds.append(i)
        times.append(time)
        seconds.append((time - start_time).total_seconds())

    # Extract a list of coordinates in time and wavelength
    # this assumes all wavelength images are taken at the same time
    time_coords = np.array([t.isoformat() for t in times])

    smap0 = sunpy.map.Map(files[0])
    spatial = map_to_transform(smap0)

    timemodel = LookupTable(lookup_table=seconds*u.s)

    hcubemodel = timemodel & spatial

    time_frame = cf.TemporalFrame(axes_order=(0, ), unit=u.s,
                                  reference_time=Time(time_coords[0]))
    sky_frame = cf.CelestialFrame(axes_order=(1, 2), name='helioprojective',
                                  reference_frame=smap0.coordinate_frame)

    sky_frame = cf.CompositeFrame([time_frame, sky_frame])

    wcs = gwcs.wcs.WCS(forward_transform=hcubemodel, output_frame=sky_frame)

    print(repr(wcs))

    print(wcs(*[1*u.pix]*4, output="numericals_plus"))

    ea = references_from_filenames(files, relative_to=str(path))

    tree = {
        'gwcs': wcs,
        'dataset': ea,
    }

    with asdf.AsdfFile(tree) as ff:
        # ff.write_to("test.asdf")
        filename = str(path / "eit_{}.asdf".format(time_coords[0]))
        ff.write_to(filename)
        print("Saved to : {}".format(filename))


if __name__ == "__main__":
    main()
