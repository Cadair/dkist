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

First we can load the dataset in the same way as level 1 datasets:

```{code-cell} ipython3
inv = dkist.load_dataset(data_path)
```

The object returned is an `Inversion` class:

```{code-cell} ipython3
inv
```

Unlike the L1 datasets, inversions have keys, which correspond to different physical parameters, each physical parameter is represented by the `dkist.Dataset` object which is the same object used for all Level 1 data.

```{code-cell} ipython3
inv["temperature"]
```

Because each of the physical parameters have the same array dimensions, ndcube says they have "aligned axes", so you can slice all the physical parameters at once:

```{code-cell} ipython3
small_inv = inv[100:200, 200:300]
small_inv
```

```{code-cell} ipython3
small_inv["temperature"]
```

Each physical parameter has it's own file manager, the same as level 1

```{code-cell} ipython3
inv["temperature"].files
```

However, they all reference different HDUs in the same set of FITS files.

```{code-cell} ipython3
inv["temperature"].files.filenames
```

```{code-cell} ipython3
inv["optical_depth"].files.filenames == inv["temperature"].files.filenames
```

You can plot a single quantity in the same way as level 1 data:

```{code-cell} ipython3
fig = plt.figure()
small_inv["temperature"].plot(fig=fig, plot_axes=["y", "x", None], colorbar=True)
```

```{code-cell} ipython3
fig = plt.figure(figsize=(12,10))
_ = small_inv.plot(np.s_[:,:,0], figure=fig, inversions=["mag_strength", "temperature"])
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

## Profiles

```{code-cell} ipython3
inv.profiles
```

```{code-cell} ipython3
inv.profiles["NaID_orig"]
```

```{code-cell} ipython3
inv.plot(0)
```

```{code-cell} ipython3

```
