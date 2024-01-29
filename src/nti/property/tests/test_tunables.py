# -*- coding: utf-8 -*-
"""
Tests for tunables.py

"""

import unittest
import doctest


def test_suite():
    # zope-testrunner specific test loading.
    from .. import tunables
    return unittest.TestSuite((
        doctest.DocTestSuite(tunables)
    ))
