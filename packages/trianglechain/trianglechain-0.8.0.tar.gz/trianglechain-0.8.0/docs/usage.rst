=====
Usage
=====

TriangleChain is optimized to work with structured arrays, however dictionaries or standard numpy arrays are also supported.

A basic contour plot can then be created by::

	from trianglechain import TriangleChain
	tri = TriangleChain()
	tri.contour_cl(data);

TriangleChain offers a variety of plotting types:

* contour_cl:

	A standard contour plot with confidence levels

* density_image:

	Instead of confidence levels, a density image is shown using a colormap

* scatter:

	Plot of every data point as a single dot

* scatter_density:

	Same as "scatter" but the color of the dot is defined by the local density

* scatter_prob:

	Same as "scatter" but the color of the dot is defined by the probability of 
	the dot given by the argument `prob`

For examples of all these plotting types and further use of arguments, we refer to our `demos
<https://cosmo-gitlab.phys.ethz.ch/cosmo_public/trianglechain/-/blob/main/demo>`_.

To get an overview of possible arguements that can be passed, use::

	help(TriangleChain)