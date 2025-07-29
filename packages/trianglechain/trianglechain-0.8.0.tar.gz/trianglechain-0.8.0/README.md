trianglechain
=============

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/trianglechain.svg)](https://pypi.python.org/pypi/trianglechain/)
[![PyPI version](https://badge.fury.io/py/trianglechain.svg)](https://badge.fury.io/py/trianglechain)
[![Latest Release](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain/-/badges/release.svg)](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain/-/releases)
[![pipeline](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain/badges/main/pipeline.svg)](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain)
[![coverage](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain/badges/main/coverage.svg)](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain)

[![image](http://img.shields.io/badge/arXiv-2203.09616-B31B1B.svg?logo=arxiv&style=flat)](https://arxiv.org/abs/2203.09616)
[![image](http://img.shields.io/badge/arXiv-2207.01627-B31B1B.svg?logo=arxiv&style=flat)](https://arxiv.org/abs/2207.01627)
[![Docs](https://badgen.net/badge/icon/Documentation?icon=https://cdn.jsdelivr.net/npm/simple-icons@v13/icons/gitbook.svg&label)](https://cosmo-docs.phys.ethz.ch/trianglechain/)
[![Source Code](https://badgen.net/badge/icon/Source%20Code?icon=gitlab&label)](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain)

Code for plotting multidimensional marginal distributions. If you use it, please cite [arXiv-2203.09616](https://arxiv.org/abs/2203.09616) and [arXiv-2207.01627](https://arxiv.org/abs/2207.01627).

[Source](https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain)

[Documentation](http://cosmo-docs.phys.ethz.ch/trianglechain)


Basic Usage
-----------

To plot a standard triangle plot, you use

``` python
from trianglechain import TriangleChain
import numpy as np

# generate samples
samples = np.random.multivariate_normal(
    mean=np.zeros(3),
    cov=np.diag(np.ones(3)),
    size=(10000)
)

tri = TriangleChain()
tri.contour_cl(samples);
```
The input data can be rec arrays, numpy array, pandas dataframes or dictionaries.
For more example plots, see the [documentation](http://cosmo-docs.phys.ethz.ch/trianglechain)

Credits
-------

This package was created by Tomasz Kacprzak and further developed and extended by Silvan Fischbacher.
The package is maintained by Silvan Fischbacher: silvanf@phys.ethz.ch.

Contributions
-------------
Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.
