#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904
import unittest

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_property

from nti.property.dataurl import encode
from nti.property.dataurl import decode
from nti.property.dataurl import DataURL


GIF_DATAURL = (
    'data:image/gif;base64,'
    'R0lGODlhCwALAIAAAAAA3pn/ZiH5BAEAAAEALAAAAAALAAsAAAIUhA+hkcuO4lmNVindo7qyrIXiGBYAOw=='
)
GIF_DATA = (
    b'GIF89a\x0b\x00\x0b\x00\x80\x00\x00\x00\x00\xde\x99\xfff!'
    b'\xf9\x04\x01\x00\x00\x01\x00,\x00\x00\x00\x00\x0b\x00\x0b'
    b'\x00\x00\x02\x14\x84\x0f\xa1\x91\xcb\x8e\xe2Y\x8dV)\xdd'
    b'\xa3\xba\xb2\xac\x85\xe2\x18\x16\x00;'
)

class TestDataURL(unittest.TestCase):

    def test_data_url_class(self):
        url = DataURL(GIF_DATAURL)
        assert_that(url, has_property('mimeType', 'image/gif'))
        assert_that(url, has_property('data', is_not(none())))
        encoded = encode(url.data, 'image/gif')
        assert_that(encoded, is_(GIF_DATAURL))

    def test_decode_DataUrl(self):
        url = DataURL(GIF_DATAURL)
        assert_that(decode(url), is_((GIF_DATA, 'image/gif')))

    def test_funky_decode(self):
        bad_data = GIF_DATAURL.replace('base64', 'quoted')
        _, mime = decode(bad_data) # this decodes improperly
        assert_that(mime, is_('image/gif'))

        bad_data = bad_data.replace('image/gif;quoted', '')
        _, mime = decode(bad_data) # this decodes improperly
        assert_that(mime, is_('text/plain;charset=US-ASCII'))

    def test_encode_plain(self):
        data = b'abcd'
        url = encode(data, encoder=None)

        assert_that(url, is_('data:text/plain;charset=US-ASCII,abcd'))
