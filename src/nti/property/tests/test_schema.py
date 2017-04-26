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

from nti.property.schema import DataURI

from nti.property.tests import PropertyLayerTest

from zope.schema.interfaces import InvalidURI

GIF_DATAURL = 'data:image/gif;base64,R0lGODlhCwALAIAAAAAA3pn/ZiH5BAEAAAEALAAAAAALAAsAAAIUhA+hkcuO4lmNVindo7qyrIXiGBYAOw=='


class TestSchema(PropertyLayerTest):

    def test_data_url_class(self):
        value = DataURI.is_valid_data_uri(GIF_DATAURL)
        assert_that(value, is_(True))

        field = DataURI(__name__='url')
        data_url = field.fromUnicode(GIF_DATAURL)
        assert_that(data_url, is_(GIF_DATAURL))
        assert_that(field.fromUnicode(data_url), is_(same_instance(data_url)))


        with self.assertRaises(InvalidURI):
            field.fromUnicode(u'data2:notvalid')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
