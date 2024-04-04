# -*- coding: utf-8 -*-
"""
Tests for tunables.py

"""
import unittest
import doctest

def _doctest():
    from zope.testing import cleanup
    from .. import tunables
    return doctest.DocTestSuite(tunables,
                                tearDown=lambda _test: cleanup.cleanUp())

def load_tests(_loader, standard_tests, _pattern):
    # unittest module
    standard_tests.addTests(_doctest())
    return standard_tests

if __name__ == '__main__':
    unittest.main()
