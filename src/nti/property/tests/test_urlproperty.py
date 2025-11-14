#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that
from hamcrest import has_properties
from hamcrest import is_in

from zope.schema.interfaces import InvalidURI
from zope.schema.interfaces import ConstraintNotSatisfied

try:
    from nti.property.urlproperty import UrlProperty
except ModuleNotFoundError: # pragma: no cover
    UrlProperty = None


GIF_DATAURL = (
    'data:image/gif;base64,'
    'R0lGODlhCwALAIAAAAAA3pn/ZiH5BAEAAAEALAAAAAALAAsAAAIUhA+hkcuO4lmNVindo7qyrIXiGBYAOw=='
)

# pylint:disable=unnecessary-dunder-call

class TestURLProperty(unittest.TestCase):

    def setUp(self):
        super().setUp()
        if UrlProperty is None: # pragma: no cover
            self.skipTest('zope.file not installed')

    def test_getitem(self):
        prop = UrlProperty()
        getter = prop.make_getitem()
        with self.assertRaises(KeyError):
            getter(object(), 'foobar')
        assert_that(getter(object(), prop.data_name), is_(none()))

    def test_delete(self):
        prop = UrlProperty()
        assert_that(prop.__delete__(None), is_(none()))

        class O(object):
            pass

        o = O()
        setattr(o, prop.url_attr_name, 1)
        setattr(o, prop.file_attr_name, 2)

        prop.__delete__(o)
        assert_that(o.__dict__, is_({}))

    def test_reject_url_with_missing_host(self):
        prop = UrlProperty()
        prop.reject_url_with_missing_host = True

        class O(object):
            pass
        with self.assertRaises(InvalidURI):
            prop.__set__(O(), '/path/to/thing')

        prop.reject_url_with_missing_host = False

        o = O()
        o._url = None # pylint:disable=attribute-defined-outside-init
        prop.ignore_url_with_missing_host = True
        prop.__set__(o, '/path/to/thing')

        assert_that(prop.__get__(o, O), is_(none()))

        prop.ignore_url_with_missing_host = False
        prop.__set__(o, '/path/to/thing')

        assert_that(prop.__get__(o, O), is_('/path/to/thing'))

    def test_custom_attr_names(self):
        prop = UrlProperty(data_name='DATA', url_attr_name="URL", file_attr_name='FILE')
        assert_that(prop, has_properties(data_name='DATA',
                                         url_attr_name='URL',
                                         file_attr_name='FILE'))

    def test_use_dict_cover(self):

        class O(object):
            prop = UrlProperty(use_dict=True)

            @property
            def data(self):
                raise AttributeError('data') # pragma: no cover

            _file = _url = data

            __getitem__ = prop.make_getitem()

            def __contains__(self, key):
                return o[key]

        o = O()
        o.__dict__['_file'] = 'data_value'
        assert_that('data', is_in(o))# has_entry('data', 'data_value'))
        assert_that(O.prop.get_file(o), none())
        with self.assertRaises(AttributeError):
            getattr(o, 'prop')

        # Settings adds fields
        o.prop = ''

        assert_that(o.__dict__['_file'], none())
        assert_that(o.__dict__['_url'], is_(''))
        assert_that(O.prop.get_file(o), none())

        # Starts out as the data url
        assert_that(o.prop, is_(''))

        o.prop = GIF_DATAURL

        assert_that(o.prop, is_(GIF_DATAURL))

        O.prop.max_file_size = 1
        with self.assertRaises(ConstraintNotSatisfied):
            o.prop = GIF_DATAURL

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
