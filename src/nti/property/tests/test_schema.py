#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that

from nti.property.schema import DataURI

from nti.property.tests import PropertyLayerTest


GIF_DATAURL = 'data:image/gif;base64,R0lGODlhCwALAIAAAAAA3pn/ZiH5BAEAAAEALAAAAAALAAsAAAIUhA+hkcuO4lmNVindo7qyrIXiGBYAOw=='


class TestSchema(PropertyLayerTest):

    def test_data_url_class(self):
        value = DataURI.is_valid_data_uri(GIF_DATAURL)
        assert_that(value, is_(True))
        data_url = DataURI(__name__='url').fromUnicode(GIF_DATAURL)
        assert_that(data_url, is_(GIF_DATAURL))
