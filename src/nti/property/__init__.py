#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from nti.property.property import readproperty

from nti.property.property import alias
from nti.property.property import read_alias

from nti.property.property import dict_alias
from nti.property.property import dict_read_alias

from nti.property.property import annotation_alias

from nti.property.property import Lazy
from nti.property.property import LazyOnClass
from nti.property.property import CachedProperty

from nti.property.urlproperty import UrlProperty
