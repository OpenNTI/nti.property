#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Support for URLs.
"""
import logging

__docformat__ = "restructuredtext en"

logger = logging.getLogger(__name__)

from urllib.parse import urlparse

from zope.contenttype.parse import parse as ct_parse

from zope.file import file as zfile

from zope.file.interfaces import IFile

from zope.schema.interfaces import InvalidURI
from zope.schema.interfaces import ConstraintNotSatisfied

from nti.property import dataurl


def _dict_setattr(instance, name, value):
    instance.__dict__[name] = value


def _dict_getattr(instance, name, default=_dict_setattr):
    if default is _dict_setattr:
        try:
            return instance.__dict__[name]
        except KeyError as ex:  # pragma: no cover
            raise AttributeError(name) from ex
    return instance.__dict__.get(name, default)


def _dict_delattr(instance, name):  # pragma: no cover
    instance.__dict__.pop(name, None)


class UrlProperty(object):
    """
    A data descriptor like :func:`property` for storing a URL value efficiently.

    This is an interesting situation because of ``data:`` URLs, which
    can be quite large. (See :mod:`nti.property.dataurl`) To store them efficiently,
    we transform them into a Blob-based :class:`zope.file.interfaces.IFile`. This means
    that we need up to two dictionary entries/attributes on the instance (one to store
    a URL string, one to store a IFile), although they can be the same; we will take
    care of type checking as needed.

    Commonly, to be useful, the file will need to be reachable by traversal on the
    instance holding the property. This object will ensure that the file is located
    (in the :mod:`zope.location` sense) as a child of the instance, and that it has a name;
    it is the responsibility of the instance to arrange for it to be traversable
    (through implementing ``__getitem__`` or ITraversable or an adapter).

    """

    max_file_size = None

    url_attr_name = '_url'
    file_attr_name = '_file'
    data_name = 'data'

    ignore_url_with_missing_host = False
    reject_url_with_missing_host = False

    _getattr = staticmethod(getattr)
    _setattr = staticmethod(setattr)
    _delattr = staticmethod(delattr)

    def __init__(self, data_name=None, url_attr_name=None,
                 file_attr_name=None, use_dict=False):
        """
        :keyword bool use_dict: If set to `True`, then the instance dictionary will be used
                explicitly for access to the url and file data. This is necessary if this property
                is being assigned to the same value as one of the attr names.
        """
        if url_attr_name:
            self.url_attr_name = url_attr_name

        if file_attr_name:
            self.file_attr_name = file_attr_name

        if data_name:
            self.data_name = data_name

        if use_dict:
            self._getattr = _dict_getattr
            self._setattr = _dict_setattr
            self._delattr = _dict_delattr

    def make_getitem(self):
        """
        As a convenience and to help with traversability, the results
        of this method can be assigned to __getitem__ (if there is no other instance
        of this property, or no other getitem).

        .. caution:: The traversal key must be equal to the ``data_name``, but
           the returned dictionary key is the ``file_attr_name``.
        """
        def __getitem__(s, key):
            if key == self.data_name:
                return self._getattr(s, self.file_attr_name, None)
            raise KeyError(key)
        return __getitem__

    def get_file(self, instance):
        """
        Return the :class:`zope.file.interfaces.IFile` for the instance
        if there is one, otherwise None.
        """
        the_file = self._getattr(instance, self.file_attr_name, None)
        # pylint:disable-next=no-value-for-parameter
        return (the_file if IFile.providedBy(the_file) else None)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        the_file = self.get_file(instance)
        if the_file is not None:
            fp = the_file.open()
            raw_bytes = fp.read()
            fp.close()
            return dataurl.encode(raw_bytes, the_file.mimeType)

        return self._getattr(instance, self.url_attr_name)

    def __set__(self, instance, value):
        if instance is None:  # pragma: no cover
            return

        if not value:
            self._setattr(instance, self.file_attr_name, None)
            self._setattr(instance, self.url_attr_name, value)
            return

        if value.startswith('data:'):
            raw_bytes, mime_type = dataurl.decode(value)
            if self.max_file_size and len(raw_bytes) > self.max_file_size:
                raise ConstraintNotSatisfied("The uploaded file is too large.")
            major, minor, parms = ct_parse(mime_type)
            the_file = zfile.File(mimeType=major + '/' + minor,
                                  parameters=parms)
            fp = the_file.open('w')
            fp.write(raw_bytes)
            fp.close()
            the_file.__parent__ = instance
            the_file.__name__ = self.data_name

            # By keeping url in __dict__, toExternalDictionary
            # still does the right thing
            self._setattr(instance, self.url_attr_name, None)
            self._setattr(instance, self.file_attr_name, the_file)
        else:
            # Be sure it at least parses
            parsed = urlparse(value)
            if not parsed.netloc:
                if self.reject_url_with_missing_host:
                    raise InvalidURI(value)
                if self.ignore_url_with_missing_host:
                    return

            self._setattr(instance, self.file_attr_name, None)
            self._setattr(instance, self.url_attr_name, value)

    def __delete__(self, instance):
        if instance is None:
            return
        for name in self.url_attr_name, self.file_attr_name:
            try:
                self._delattr(instance, name)
            except AttributeError:  # pragma: no cover
                pass
