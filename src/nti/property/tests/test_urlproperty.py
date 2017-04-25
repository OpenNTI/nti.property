#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that

from zope.schema.interfaces import InvalidURI

from nti.property.urlproperty import UrlProperty

from nti.property.tests import PropertyLayerTest


class TestURLProperty(PropertyLayerTest):

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
