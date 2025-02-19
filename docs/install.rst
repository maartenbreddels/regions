************
Installation
************

Requirements
============

Regions has the following strict requirements:

* `Python <https://www.python.org/>`_ 3.6 or later

* `Numpy <https://numpy.org/>`_ 1.16 or later

* `Astropy`_ 3.2 or later

Region also optionally depends on other packages for some features:

* `matplotlib <https://matplotlib.org/>`_ 2.0 or later

Regions depends on `pytest-astropy
<https://github.com/astropy/pytest-astropy>`_ (0.4 or later) and
`pytest-arraydiff <https://github.com/astropy/pytest-arraydiff>`_ (0.3
or later) to run the test suite.


Installing the latest released version
======================================

The latest released (stable) version of Regions can be installed either
with `pip`_ or `conda`_.

Using pip
---------

To install Regions with `pip`_, run::

    pip install regions

If you want to make sure that none of your existing dependencies get
upgraded, instead you can do::

    pip install regions --no-deps

Note that you may need a C compiler (e.g., ``gcc`` or ``clang``) to be
installed for the installation to succeed.

If you get a ``PermissionError``, this means that you do not have the
required administrative access to install new packages to your Python
installation.  In this case you may consider using the ``--user``
option to install the package into your home directory.  You can read
more about how to do this in the `pip documentation
<https://pip.pypa.io/en/stable/user_guide/#user-installs>`_.

Do **not** install Regions or other third-party packages using
``sudo`` unless you are fully aware of the risks.

Using conda
-----------

Regions can be installed with `conda`_ if you have installed
`Anaconda <https://www.anaconda.com/products/individual>`_ or
`Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_.
To install Regions using the `conda-forge Anaconda channel
<https://anaconda.org/conda-forge/photutils>`_, run::

    conda install -c conda-forge regions


Installing the latest development version from Source
=====================================================

Prerequisites
-------------

You will need `Cython <https://cython.org/>`_ (0.28 or later), a
compiler suite, and the development headers for Python and Numpy in
order to build Regions from the source distribution. On Linux, using the
package manager for your distribution will usually be the easiest route.

On MacOS X you will need the `XCode`_ command-line tools, which can be
installed using::

    xcode-select --install

Follow the onscreen instructions to install the command-line tools
required.  Note that you do not need to install the full `XCode`_
distribution (assuming you are using MacOS X 10.9 or later).


Building and installing manually
--------------------------------

Regions is being developed on `GitHub`_. The latest development version
of the Regions source code can be retrieved using git::

    git clone https://github.com/astropy/regions.git

Then to build and install Regions, run::

    cd regions
    pip install ".[all]"

If you wish to install the package in "editable" mode, instead include
the "-e" option::

    pip install -e ".[all]"


Building and installing using pip
---------------------------------

Alternatively, `pip`_ can be used to retrieve, build, and install the
latest development version from `GitHub`_::

    pip install git+https://github.com/astropy/regions.git

Again, if you want to make sure that none of your existing
dependencies get upgraded, instead you can do::

    pip install git+https://github.com/astropy/regions.git --no-deps


Testing an installed Regions
============================

The easiest way to test your installed version of Regions is running
correctly is to use the :func:`regions.test` function:

.. doctest-skip::

    >>> import regions
    >>> regions.test()

Note that this may not work if you start Python from within the Regions
source distribution directory.

The tests should run and report any failures,
which you can report to the `Regions issue tracker
<https://github.com/astropy/regions/issues>`_.


.. _pip: https://pip.pypa.io/en/latest/
.. _conda: https://docs.conda.io/en/latest/
.. _GitHub: https://github.com/astropy/photutils
.. _Xcode: https://developer.apple.com/xcode/
