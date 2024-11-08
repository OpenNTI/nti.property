#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various property-like decorators and descriptors.
"""

__docformat__ = "restructuredtext en"

import operator

from zope.annotation.interfaces import IAnnotations


def alias(prop_name, doc=None):
    """
    Returns a property that is a read/write alias for another attribute
    of the object.

    Descriptor, use like ``my_prop = alias(\"other_prop\")``

    See :func:`dict_alias`.
    """
    if doc is None:
        doc = 'Alias for :attr:`' + prop_name + '`'
    prop_name = str(prop_name)  # native string
    return property(lambda self: getattr(self, prop_name),
                    lambda self, nv: setattr(self, prop_name, nv),
                    doc=doc)


def read_alias(prop_name, doc=None):
    """
    Returns a property that is a read-only alias for another attribute
    of the object.

    Descriptor, use like ``my_prop = read_alias(\"other_prop\")``

    See :func:`dict_read_alias`.
    """
    if doc is None:
        doc = 'Read-only alias for :attr:`' + prop_name + '`'
    return property(lambda self: getattr(self, prop_name),
                    doc=doc)


def dict_alias(key_name, doc=None):
    """
    Returns a property that is a read/write alias for a value in the
    instance's dictionary.

    See :func:`alias` for a more general version; this is a speed or
    access optimization. Be careful using it with `persistent.Persistent`
    objects (which may not have a populated dict).
    """
    if doc is None:
        doc = 'Alias for :attr:`' + key_name + '`'
    key_name = str(key_name)  # native string
    return property(lambda self: self.__dict__[key_name],
                    lambda self, nv: operator.setitem(
                        self.__dict__, key_name, nv),
                    doc=doc)


def dict_read_alias(key_name, doc=None):
    """
    Returns a property that is a read-only alias for a value in the
    instances dictionary.

    See :func:`read_alias` for a more general version; this is a speed or
    access optimization.
    """
    if doc is None:
        doc = 'Read-only alias for :attr:`' + key_name + '`'
    return property(lambda self: self.__dict__[key_name],
                    doc=doc)

class LazyOnClass(object):
    """
    Like :class:`zope.cachedescriptors.property.Lazy`, but
    when it caches, it caches on the class itself, not the instance,
    thus sharing the value. Thus, the value should be immutable and
    independent of any other state.
    """

    def __init__(self, func):
        self._func = func
        self.klass_cache_name = '_v__LazyOnClass_' + self._func.__name__

    def __get__(self, inst, klass):
        if inst is None:
            return self

        # In order to let this be resetable, to keep access
        # to this object and the original function, we
        # use a different name
        klass_cache_name = self.klass_cache_name
        val = getattr(klass, klass_cache_name, self)
        if val is self:
            val = self._func(inst)
            setattr(klass, klass_cache_name, val)
        return val


def annotation_alias(annotation_name,
                     annotation_property=None,
                     default=None,
                     delete=False, delete_quiet=True, doc=None):
    """
    Returns a property that is a read/write alias for
    a value stored as a :class:`zope.annotation.interface.IAnnotations`.

    The object itself may be adaptable to an IAnnotations, or a property
    of the object may be what is adaptable to the annotation. The later is intended
    for use in adapters when the ``context`` object is what should be adapted.

    :keyword bool delete: If ``True`` (not the default), then the property can be used
            to delete the annotation.
    :keyword bool delete_quiet: If ``True`` and *delete* is also True, then the property
            will ignore key errors when deleting the annotation value.
    :keyword str annotation_property: If set to a string, it is this property
            of the object that will be adapted to IAnnotations. Most often this will
            be ``context`` when used inside an adapter.
    """
    # pylint:disable=too-many-positional-arguments
    if doc is None:
        doc = 'Alias for annotation ' + annotation_name


    if annotation_property:
        def factory(self):
            return IAnnotations(getattr(self, annotation_property))
    else:
        factory = IAnnotations

    def fget(self):
        # pylint:disable-next=too-many-function-args
        return factory(self).get(annotation_name, default)

    def fset(self, nv):
        factory(self)[annotation_name] = nv


    if delete:
        def fdel(self):
            try:
                del factory(self)[annotation_name]
            except KeyError:
                if not delete_quiet:
                    raise
    else:
        fdel = None

    return property(fget, fset, fdel, doc=doc)
