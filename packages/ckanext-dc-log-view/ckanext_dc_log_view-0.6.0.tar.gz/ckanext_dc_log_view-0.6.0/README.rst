ckanext-dc_log_view
===================

|PyPI Version| |Build Status| |Coverage Status|


A CKAN log viewer for DC files.

Installation
------------

::

    pip install ckanext-dc_log_view



Add this extension to the plugins and defaul_views in ckan.ini:

::

    ckan.plugins = [...] dc_log_view
    ckan.views.default_views = [...] dc_log_view


Testing
-------
If CKAN/DCOR is installed and setup for testing, this extension can
be tested with pytest:

::

    pytest ckanext

Testing is implemented via GitHub Actions. You may also set up a local
docker container with CKAN and MinIO. Take a look at the GitHub Actions
workflow for more information.


.. |PyPI Version| image:: https://img.shields.io/pypi/v/ckanext.dc_log_view.svg
   :target: https://pypi.python.org/pypi/ckanext.dc_log_view
.. |Build Status| image:: https://img.shields.io/github/actions/workflow/status/DCOR-dev/ckanext-dc_log_view/check.yml
   :target: https://github.com/DCOR-dev/ckanext-dc_log_view/actions?query=workflow%3AChecks
.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/DCOR-dev/ckanext-dc_log_view
   :target: https://codecov.io/gh/DCOR-dev/ckanext-dc_log_view
