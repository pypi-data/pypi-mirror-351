ZGW Consumers' OAS tooling
==========================

:Version: 1.1.0
:Source: https://github.com/maykinmedia/zgw-consumers-oas
:Keywords: OpenAPI, Django, zgw-consumers

|build-status| |coverage| |linting|

|python-versions| |django-versions| |pypi-version|

Tooling to deal with OpenAPI specifications, extracted from zgw-consumers.

.. contents::

.. section-numbering::

ZGW Consumers used to have a hard requirement on OpenAPI 3.0 specifications for its
services. On the way to 1.0, this requirement became obsolete, and it has no need
anymore for this kind of tooling.

However, we understand that upgrading to zgw-consumers 1.0 is quite a big breaking
change if you rely on this tooling, so it was decided to provide it in a standalone
package to ease the transition.

This package is considered "feature complete" and will only receive bugfixes. No new
features will be added.


Installation
============

Requirements
------------

* Python 3.10 or newer
* Django 3.2 or newer


Install
-------

1. Install from PyPI

.. code-block:: bash

    pip install zgw-consumers-oas

Usage
=====

#. Update the relevant ``zgw_consumers.test.*`` imports to ``zgw_consumers_oas.*``

#. You can continue using the ``ZGW_CONSUMERS_*`` settings to discover OpenAPI schema
   files.



.. |build-status| image:: https://github.com/maykinmedia/zgw-consumers-oas/workflows/Run%20CI/badge.svg
    :target: https://github.com/maykinmedia/zgw-consumers-oas/actions?query=workflow%3A%22Run+CI%22
    :alt: Run CI

.. |linting| image:: https://github.com/maykinmedia/zgw-consumers-oas/workflows/Code%20quality%20checks/badge.svg
    :target: https://github.com/maykinmedia/zgw-consumers-oas/actions?query=workflow%3A%22Code+quality+checks%22
    :alt: Code linting

.. |coverage| image:: https://codecov.io/gh/maykinmedia/zgw-consumers-oas/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/zgw-consumers-oas
    :alt: Coverage status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/zgw_consumers_oas.svg

.. |django-versions| image:: https://img.shields.io/pypi/djversions/zgw_consumers_oas.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/zgw_consumers_oas.svg
    :target: https://pypi.org/project/zgw_consumers_oas/
