#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from hamcrest import is_
from hamcrest import has_entry
from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import same_instance

from zope import interface

from zope.annotation import interfaces as an_interfaces

from nti.property.property import alias
from nti.property.property import read_alias
from nti.property.property import dict_alias
from nti.property.property import LazyOnClass
from nti.property.property import dict_read_alias
from nti.property.property import annotation_alias


class TestProperty(unittest.TestCase):

    def test_alias(self):

        class X(object):

            y = alias('x')

            def __init__(self):
                self.x = 1

        x = X()
        assert_that(x, has_property('x', 1))
        assert_that(x, has_property('y', 1))
        x.y = 2
        assert_that(x, has_property('y', 2))

    def test_dict_alias(self):
        class X(object):

            def __init__(self):
                self.x = 1

            y = dict_alias('x')

        assert_that(X(), has_property('y', 1))
        x = X()
        x.y = 2
        assert_that(x, has_property('y', 2))
        assert_that(x, has_property('x', 2))

    def test_read_alias(self):

        class O(object):
            x = 1
            y = read_alias('x')

        o = O()
        assert_that(o, has_property('y', o.x))
        with self.assertRaises(AttributeError):
            o.y = 1


    def test_dict_read_alias(self):
        class X(object):

            def __init__(self):
                self.x = 1

            y = dict_read_alias('x')

        assert_that(X(), has_property('y', 1))
        x = X()
        with self.assertRaises(AttributeError):
            x.y = 2

    def test_cached_property(self):
        from zope.cachedescriptors.property import CachedProperty
        # Usable directly
        class X(object):

            @CachedProperty
            def prop(self):
                return object()

        x = X()
        assert_that(x.prop, same_instance(x.prop))

        # Usable with names
        class Y(object):

            def __init__(self):
                self.dep = 1

            @CachedProperty('dep')
            def prop(self):
                return str(self.dep)

        y = Y()
        assert_that(y.prop, same_instance(y.prop))
        assert_that(y.prop, is_("1"))
        y.dep = 2
        assert_that(y.prop, is_("2"))
        assert_that(y.prop, same_instance(y.prop))

        # And, to help refactoring, usable with parens but no names
        class Z(object):

            @CachedProperty()
            def prop(self):
                return object()

        z = Z()
        assert_that(z.prop, same_instance(z.prop))

    def test_annotation_alias(self):

        @interface.implementer(an_interfaces.IAnnotations)
        class X(dict):
            the_alias = annotation_alias('the.key',
                                         delete=True,
                                         default=1)

        x = X()
        # Default value
        assert_that(x, has_property('the_alias', 1))

        # Set
        x.the_alias = 2
        assert_that(x, has_property('the_alias', 2))
        assert_that(x, has_entry('the.key', 2))

        # del
        del x.the_alias
        assert_that(x, has_property('the_alias', 1))

        # quiet re-del
        del x.the_alias
        assert_that(x, has_property('the_alias', 1))


        # Annotation based on a property, that can't be deleted
        # quietly
        @interface.implementer(an_interfaces.IAnnotations)
        class Z(dict):

            the_alias = annotation_alias('the.key',
                                         annotation_property="context",
                                         delete=True, delete_quiet=False,
                                         default=1)

            def __init__(self):
                self.context = X()

        z = Z()
        z.context['the.key'] = 42
        assert_that(z, has_property('the_alias', 42))
        del z.the_alias
        assert_that(z, has_property('the_alias', 1))

        with self.assertRaises(KeyError):
            del z.the_alias
        assert_that(z, has_property('the_alias', 1))

        # Annotation that can't be
        # deleted at all
        @interface.implementer(an_interfaces.IAnnotations)
        class ZZ(dict):
            the_alias = annotation_alias('the.key',
                                         delete=False,
                                         default=1)

            def __init__(self):
                self.context = X()

        z = ZZ() # pylint:disable=redefined-variable-type
        z['the.key'] = 42
        assert_that(z, has_property('the_alias', 42))
        with self.assertRaises(AttributeError):
            del z.the_alias
        assert_that(z, has_property('the_alias', 42))

    def test_lazy_on_class(self):

        class X(dict):

            @LazyOnClass
            def _foo(self):
                return "boo"

        assert_that(X._foo, is_(LazyOnClass))

        x = X()
        assert_that(x, has_property('_foo', is_("boo")))
        x2 = X()
        assert_that(x2, has_property('_foo', is_("boo")))
