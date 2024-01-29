#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import same_instance
from hamcrest import has_property

from nti.property.schema import DataURI

from zope.schema.interfaces import InvalidURI

GIF_DATAURL = (
    'data:image/gif;base64,'
    'R0lGODlhCwALAIAAAAAA3pn/ZiH5BAEAAAEALAAAAAALAAsAAAIUhA+hkcuO4lmNVindo7qyrIXiGBYAOw=='
)


class TestSchema(unittest.TestCase):

    def test_data_url_class(self):
        value = DataURI.is_valid_data_uri(GIF_DATAURL)
        assert_that(value, is_(True))

        field = DataURI(__name__='url')
        data_url = field.fromUnicode(GIF_DATAURL)
        assert_that(data_url, is_(GIF_DATAURL))
        assert_that(field.fromUnicode(data_url), is_(same_instance(data_url)))

        bad_data = 'data2:notvalid'
        with self.assertRaises(InvalidURI) as exc:
            field.fromUnicode(bad_data)

        ex = exc.exception
        assert_that(ex, has_property('value', bad_data))
        assert_that(ex, has_property('field', field))
