---
jupytext:
  formats: md:myst,ipynb
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.1
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# A Quick Introduction to Level 2 Inversions

+++

```{warning}
The level 2 functionality is still in *beta* expect it to change before the 2.0 release.
```

```{code-cell} ipython3
%matplotlib inline
```

```{code-cell} ipython3
import numpy as np
import matplotlib.pyplot as plt

import dkist
```

```{code-cell} ipython3
from astropy.coordinates import SkyCoord, SpectralCoord, StokesCoord
from astropy.time import Time
import astropy.units as u
```

```{code-cell} ipython3
data_path = "/data/dkist/globus/inv.PUYATW/"
```

```{code-cell} ipython3
inv = dkist.load_dataset(data_path)
```

```{code-cell} ipython3
inv
```

```{code-cell} ipython3
fig = inv.plot(np.s_[:,:,0], figure=plt.figure(figsize=(12,10)), inversions=["temperature"])
plt.colorbar(label=f"Temperature [{inv['temperature'].unit:latex}]")
```

Now let's see if we can plot a 1D temperature vs optical depth line for a single spatial pixel:

```{code-cell} ipython3
one_pix = inv["temperature"][300, 400, :]
one_pix
```

```{code-cell} ipython3
fig = one_pix.plot()
```

Well that doesn't seem right, it doesn't have an x-axis.

```{code-cell} ipython3
one_pix.axis_world_coords()
```

Well that's a list of coords, although why one of them is suddenly -2e-16 I don't know.

+++

## Profiles

```{code-cell} ipython3
inv.profiles
```

```{code-cell} ipython3
inv.profiles["NaID_orig"]
```

```{code-cell} ipython3
# yes this is horrible
celestial_frame = inv.profiles["NaID_orig"].wcs.output_frame.frames[2].reference_frame
```

```{code-cell} ipython3
inv.profiles["NaID_orig"].wcs.world_to_pixel(
    StokesCoord(0),
    SpectralCoord(589.7*u.nm),
    SkyCoord(350*u.arcsec, 540*u.arcsec, frame=celestial_frame),
    Time("2024-04-17T20:25:26.704"),
)
```

```{code-cell} ipython3
inv["temperature"]
```

```{code-cell} ipython3
inv["temperature"].wcs.world_to_pixel(
    0*u.pix,  # optical depth
    SkyCoord(350*u.arcsec, 540*u.arcsec, frame=celestial_frame),  # lon/lat
    Time("2024-04-17T20:25:26.704"), # time
    StokesCoord(0),  # Stokes??!
)
```
