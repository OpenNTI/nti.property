=========
 Changes
=========


2.2.2 (2025-11-18)
==================

- Make ``zope.configuration`` an optional dependency. Previously, it
  was installed by default via way of ``zope.file``, which itself is
  now optional.


2.2.1 (2025-11-14)
==================

- Move ``zope.file``, and by extension ZODB, into the "zodb" extra.


2.2.0 (2025-09-19)
==================

- Add support for Python 3.14; this required no code changes, so
  earlier versions should work on 3.14 as well.
- Tweak the logging from ``Tunable``.


2.1.0.post0 (2024-11-08)
========================

- Nothing changed yet.


2.1.0 (2024-11-08)
==================

- Add support for Python 3.13.
- Use native namespace packages.


2.0.2 (2024-04-04)
==================

- Make ``Tunable`` search harder (farther up the call chain)
  to find a logger. This should make finding a logger in a
  class definition better.


2.0.1 (2024-02-16)
==================

- Updates to documentation and logging for tunables.


2.0.0 (2024-01-29)
==================

- Add support for Python 3.12.
- Drop runtime dependency on setuptools in favor of "native namespace
  packages".
- Drop support for legacy Python versions: 2.7, 3.6. 3.7, 3.8 and 3.9.
- Add new module ``nti.property.tunables`` for customizing parameters
  (usually represented as class variables) from the environment.


1.2.0 (2023-05-05)
==================

- Add support for Python 3.8, 3.9, 3.10 and 3.11.


1.1.0 (2018-09-13)
==================

- Add support for Python 3.7.

- Add support for zope.schema 4.7.


1.0.0 (2017-04-26)
==================

- First PyPI release.
- Add support for Python 3.6.
- Remove backward compatibility exports.
