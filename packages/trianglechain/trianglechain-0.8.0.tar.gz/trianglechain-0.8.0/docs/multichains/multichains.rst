==================================
Tutorial: Plotting multiple chains
==================================

In this tutorial, we show how to plot multiple chains in the same plot

.. code:: python

    import numpy as np
    from trianglechain import TriangleChain
    from trianglechain.params import add_derived, ensure_rec
    from cosmic_toolbox.colors import set_cycle
    set_cycle()

.. code:: python

    def get_samples(n_samples=100000, n_dims=2, names=None):
        covmat = np.random.normal(size=(n_dims, n_dims))
        covmat = np.dot(covmat.T, covmat)
        mean = np.random.uniform(size=(n_dims))
        samples = np.random.multivariate_normal(mean=mean, cov=covmat, size=(n_samples))
        samples = ensure_rec(samples, names)
        return samples

Plot 2 chains with the same parameter
=====================================

.. code:: python

    # If you have two samples with the same parameters, plotting them on top of each other can be done like this:
    
    sample1 = get_samples(names=["a", "b"])
    sample2 = get_samples(names=["a", "b"])
    
    tri = TriangleChain()
    tri.contour_cl(sample1)
    tri.contour_cl(sample2);


.. image:: output_4_2.png


Plot 2 chains with different parameters
=======================================

.. code:: python

    # To plot all parameters of a samples, you can use the params_from argument
    
    sample1 = get_samples(names=["a", "b"])
    sample2 = get_samples(names=["b", "c"])
    
    tri = TriangleChain(params_from=[sample1, sample2])
    tri.contour_cl(sample1)
    tri.contour_cl(sample2);

.. image:: output_6_3.png


.. code:: python

    # ... or you can specify the plotted parameters directly
    # This also works if you only want to plot a subset of the parameters
    
    tri = TriangleChain(params=["a", "b", "c"])
    tri.contour_cl(sample1)
    tri.contour_cl(sample2);


.. image:: output_7_3.png


