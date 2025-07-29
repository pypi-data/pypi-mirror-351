====================
Tutorial: Parameters
====================

This tutorial shows which formats can be used in trianglechain

.. code:: python

    import numpy as np
    import pandas as pd
    from trianglechain import TriangleChain
    from trianglechain.params import add_derived, ensure_rec

.. code:: python

    def get_samples(n_samples=100000, n_dims=2):
        covmat = np.random.normal(size=(n_dims, n_dims))
        covmat = np.dot(covmat.T, covmat)
        mean = np.random.uniform(size=(n_dims))
        samples = np.random.multivariate_normal(mean=mean, cov=covmat, size=(n_samples))
        return samples
    
    
    samples = get_samples()

Plotting rec arrays
===================

.. code:: python

    # TriangleChain works best with rec arrays
    # If you want to transform your ndarray/dict/pandas.df in a rec_array, you can do
    samples_rec = ensure_rec(samples, names=["a", "b"])
    # for numpy arrays, you can specify the names, for dicts/pandas they are automatically generated

.. code:: python

    tri = TriangleChain()
    tri.contour_cl(samples_rec);

.. image:: output_5_1.png


Plotting numpy arrays
=====================

.. code:: python

    # Plotting a numpy array of shape (n_samples, n_dim) can be done like this
    # The parameters are labeled as numbers
    tri = TriangleChain()
    tri.contour_cl(samples);


.. image:: output_7_1.png


.. code:: python

    # You can add names to parameters
    tri = TriangleChain()
    tri.contour_cl(samples, names=["a", "b"]);


.. image:: output_8_1.png


.. code:: python

    # Or add a column prefix
    samples_prefix = ensure_rec(samples, column_prefix="col_")
    tri = TriangleChain()
    tri.contour_cl(samples_prefix);

.. image:: output_9_1.png


Plotting a dictionary
=====================

.. code:: python

    samples_dict = {}
    samples_dict["a"] = samples[:, 0]
    samples_dict["b"] = samples[:, 1]
    
    # dictionaries can also be passed directly to trianglechain
    tri = TriangleChain()
    tri.contour_cl(samples_dict);


.. image:: output_11_1.png


Plotting a pandas dataframe
===========================

.. code:: python

    df = pd.DataFrame({"a": samples[:, 0], "b": samples[:, 1]})
    
    # dictionaries can also be passed directly to trianglechain
    tri = TriangleChain()
    tri.contour_cl(df);


.. image:: output_13_1.png


Add a derived parameter
=======================

.. code:: python

    # Adding a derived parameters can again be done for all possibles types
    # If using a rec array/dict/pd.df, the names argument is not needed
    samples_c = add_derived(
        samples,
        new_param="c",
        derived=(samples[:, 0] - 3) * (samples[:, 1]),
        names=["a", "b"],
    )
    
    tri = TriangleChain()
    tri.contour_cl(samples_c);


.. image:: output_15_1.png


