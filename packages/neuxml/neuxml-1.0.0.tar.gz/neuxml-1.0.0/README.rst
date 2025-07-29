======
neuxml
======

.. image:: https://img.shields.io/pypi/v/neuxml.svg
  :target: https://pypi.python.org/pypi/neuxml
  :alt: PyPI

.. image:: https://img.shields.io/github/license/Princeton-CDH/neuxml.svg
  :alt: License

.. image:: https://img.shields.io/pypi/pyversions/neuxml
  :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/dm/neuxml.svg
  :alt: PyPI downloads

`neuxml` is a Python library that provides utilities and classes for
object-oriented access to XML. `neuxml` makes it possible to define reusable
python classes to access, update, and create XML content as standard Python types.

**neuxml.xmlmap** makes it possible to map XML content to Python objects in a
pythonic and object-oriented way, which is easier to use than typical DOM access.
With the `neuxml.xmlmap.XmlObject` class, XML can be read, modified, and even
created from scratch in some cases, as long as the configured XPath can
be used to construct new nodes.

Object-oriented access depends on **neuxml.xpath**, which provides functions and
classes for parsing XPath expressions using `PLY <http://www.dabeaz.com/ply/>`_.

Installation
============

We recommend using pip to install the officially released versions from PyPI:

.. code-block:: shell

  pip install neuxml

It is also possible to install directly from GitHub. Use a branch or tag name,
e.g. `@develop` or `@1.0` to install a specific tagged version or branch.

.. code-block:: shell

  pip install git+https://github.com/Princeton-CDH/neuxml.git@develop#egg=neuxml


License
=======

**neuxml** is distributed under the Apache 2.0 License.


Development History
===================

`neuxml` is a hard fork of `eulxml <https://github.com/emory-libraries/eulxml>`_,
which was originally developed by Emory University Libraries from 2011-2016.
`neuxml` has been updated for compatibility with current versions of Python
and drops the support for Django form integration. The full development history
for the `eulxml` package is available at the original repository:  https://github.com/emory-libraries/eulxml


Technical documentation
=======================

For instructions on developer setup, unit testing, XML catalog file management,
and migrating from `eulxml`, refer to ``DEVNOTES.rst``.

Migration from ``eulxml``
=========================

If migrating from a previous ``eulxml`` installation, see ``MIGRATION.rst``.
