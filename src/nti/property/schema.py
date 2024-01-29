#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Schema fields.

"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
__docformat__ = "restructuredtext en"


from zope import schema
from zope.schema.interfaces import InvalidURI

from nti.property import dataurl


class DataURI(schema.URI):
    """
    A URI field that ensures and requires its value to be
    a data URI. The field value is a :class:`.DataURL`.
    """

    DATA = 'data:'

    @classmethod
    def is_valid_data_uri(cls, value):
        return value and value.startswith(cls.DATA)

    def _validate(self, value):
        super()._validate(value)
        if not self.is_valid_data_uri(value):
            raise InvalidURI(value).with_field_and_value(self, value)

    def fromUnicode(self, value):
        if isinstance(value, dataurl.DataURL):
            return value

        super().fromUnicode(value)
        return dataurl.DataURL(value)
