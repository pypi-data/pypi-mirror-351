Change & Version Information
============================

1.0.0
-----

Initial release of `neuxml.` This is a hard fork of `eulxml <https://github.com/emory-libraries/eulxml>`_
version 1.1.3, which drops Django forms integration and support for older versions of Python.

* Rename `eulxml` to `neuxml` throughout
* Remove `forms` submodule and drop Django requirements
* Add GitHub Actions workflow for PyPI publication
* Update for Python 3.12 compatibility
* Store a default XML catalog and schemas in codebase and released package
* Migrate build environment to Hatchling with `pypackage.toml`
* Migrate test environment from Nose to Pytest

For a record of the pre-existing functionality, refer to the `eulxml changelog <https://github.com/emory-libraries/eulxml/blob/master/CHANGELOG.rst>`_.
