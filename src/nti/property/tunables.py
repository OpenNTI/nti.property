# -*- coding: utf-8 -*-
"""
Property objects providing tunable settings.

The common use of these is to define them as class variables
(constants), and access them as instance variables. Just once,
the value of an environment variable is read, and that becomes the
value of the property when accessed as an instance variable.

For example:

.. doctest::

   >>> import os
   >>> from nti.property.tunables import Tunable
   >>> os.environ['NTI_PROP_TEST'] = '42'
   >>> class T:
   ...     PROP = Tunable(default='from class', env_name='NTI_PROP_TEST')
   >>> T().PROP
   42
   >>> os.environ['NTI_PROP_TEST'] = '43'
   >>> T().PROP
   42

The way in which environment variables are converted to Python objects is customizable.
The best way to do this is to use named implementations of :class:`IEnvironGetter`.
A ZCML directive provided by this package will register these with the component
system; this is automatically done when including this package.

.. doctest::


    >>> from nti.property.tunables import IEnvironGetter
    >>> from zope import component
    >>> from zope.configuration import xmlconfig
    >>> _ = xmlconfig.string('''\
    <configure xmlns="http://namespaces.zope.org/zope" \
               xmlns:nntp="http://nextthought.com/ntp/property"> \
         <include package="nti.property" /> \
         <nntp:registerTunables /> \
    </configure> \
    ''')
    >>> component.getUtility(IEnvironGetter, name='byte-size') # doctest: +ELLIPSIS
    <function get_byte_size_from_environ at ...>
    >>> component.getUtility(IEnvironGetter, name='dotted-name') # doctest: +ELLIPSIS
    <EnvironGetter 'dotted-name'=<ZConfig.datatypes.DottedNameConversion object at ...>>


There is :obj:`a registry <ENVIRON_GETTERS>` of fallback names that is used
if the component system is not initialized. The same names are registered
in both places.

.. versionadded:: NEXT

"""
import os
import sys
import logging

from zope import component
from zope.component import named
from zope.component.zcml import utility as registerUtility
from zope.interface import Interface
from zope.interface import provider

from ZConfig.datatypes import asBoolean
from ZConfig.datatypes import integer
from ZConfig.datatypes import RangeCheckedConversion
from ZConfig.datatypes import stock_datatypes

_logger = logging.getLogger(__name__)

positive_integer = RangeCheckedConversion(integer, min=1)
positive_float = RangeCheckedConversion(float, min=1)

non_negative_float = RangeCheckedConversion(float, min=0)
non_negative_integer = RangeCheckedConversion(integer, min=0)


def _setting_from_environ(converter, environ_name, default, logger):
    logger = logger or _logger
    result = default
    env_val = os.environ.get(environ_name, default) if environ_name else default
    if env_val is not default:
        try:
            result = converter(env_val)
        except (ValueError, TypeError):
            logger.exception("Failed to parse environment value %r for key %r",
                             env_val, environ_name)
            result = default

    logger.info(
        'Using value %s from environ %r=%r (default=%r)',
        result, environ_name, env_val, default)
    return result


class IEnvironGetter(Interface): # pylint:disable=inherit-non-class
    """
    A getter function for use with :class:`Tunable`.
    """
    # pylint:disable=no-self-argument
    def __call__(environ_name, default, logger=None):
        """
        Read and return an appropriately converted Python
        object from an environment variable named *environ_name*.

        If this cannot be done (the environment variable is missing
        or malformed), return the *default* value.

        Information will be logged using the :class:`logging.Logger` *logger*.
        If not provided, a default logger will be used.
        """

class _EnvironGetterRegistry(dict):
    def __init__(self):
        self.__orig = {}
        self.__closed = False

    def __setitem__(self, name, value):
        if not self.__closed:
            self.__orig[name] = value
        super().__setitem__(name, value)

    def close(self):
        self.__closed = True

    def reset(self):
        self.clear()
        self.update(self.__orig)

    def __repr__(self):
        return "<EnvironGetters %s>" % (list(self),)

#: The mapping from string names to getter functions used
#: when there are no components registered.
ENVIRON_GETTERS = _EnvironGetterRegistry()


def _getter(name):
    def wrap(func):
        func = named(name)(func)
        func = provider(IEnvironGetter)(func)
        assert name not in ENVIRON_GETTERS
        ENVIRON_GETTERS[name] = func
        return func
    return wrap

try:
    from zope.testing import cleanup
except ImportError:
    pass
else:
    cleanup.addCleanUp(ENVIRON_GETTERS.reset)


@_getter('string')
def get_string_from_environ(environ_name, default, logger=None):
    """
    A getter function that returns the environment value unchanged.
    In particular, this does no string stripping on trimming, so whitespace
    is preserved.

    >>> import os
    >>> from nti.property.tunables import get_string_from_environ
    >>> _ = os.environ.pop('RS_TEST_VAL', None)
    >>> get_string_from_environ('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = ' <a string> '
    >>> get_string_from_environ('RS_TEST_VAL', None)
    ' <a string> '
    """
    return _setting_from_environ(lambda k: k, environ_name, default, logger)


@_getter('integer+')
def get_positive_integer_from_environ(environ_name, default, logger=None):
    """
    A getter function that returns a positive integer from the environment
    (positive integers are those greater than or equal to 1).
    Other values are ignored.

    >>> import os
    >>> from nti.property.tunables import get_positive_integer_from_environ as fut
    >>> _ = os.environ.pop('RS_TEST_VAL', None)
    >>> fut('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = '1982'
    >>> fut('RS_TEST_VAL', 42)
    1982
    >>> os.environ['RS_TEST_VAL'] = '1'
    >>> fut('RS_TEST_VAL', 42)
    1
    >>> os.environ['RS_TEST_VAL'] = '0'
    >>> fut('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = '-1492'
    >>> fut('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = '<a string>'
    >>> fut('RS_TEST_VAL', 42)
    42
    """
    return _setting_from_environ(positive_integer, environ_name, default, logger)

@_getter('float+')
def get_positive_float_from_environ(environ_name, default, logger=None):
    """
    A getter function that returns a positive decimal from the environment
    (positive decimals are those greater than or equal to 1).
    Other values are ignored.

    >>> import os
    >>> from nti.property.tunables import get_positive_float_from_environ as fut
    >>> _ = os.environ.pop('RS_TEST_VAL', None)
    >>> fut('RS_TEST_VAL', 42.0)
    42.0
    >>> os.environ['RS_TEST_VAL'] = '1982.0'
    >>> fut('RS_TEST_VAL', 42)
    1982.0
    >>> os.environ['RS_TEST_VAL'] = '1'
    >>> fut('RS_TEST_VAL', 42)
    1.0
    >>> os.environ['RS_TEST_VAL'] = '0.0'
    >>> fut('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = '-1492'
    >>> fut('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = '<a string>'
    >>> fut('RS_TEST_VAL', 42)
    42
    """
    return _setting_from_environ(positive_float, environ_name, default, logger)


@_getter('integer0')
def get_non_negative_integer_from_environ(environ_name, default, logger=None):
    """
    A getter function that returns a non-negative integer from the environment
    (non-negative integers are those greater than or equal to 0).
    Other values are ignored.

    >>> import os
    >>> from nti.property.tunables import get_non_negative_integer_from_environ as fut
    >>> _ = os.environ.pop('RS_TEST_VAL', None)
    >>> fut('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = '1982'
    >>> fut('RS_TEST_VAL', 42)
    1982
    >>> os.environ['RS_TEST_VAL'] = '1'
    >>> fut('RS_TEST_VAL', 42)
    1
    >>> os.environ['RS_TEST_VAL'] = '0'
    >>> fut('RS_TEST_VAL', 42)
    0
    >>> os.environ['RS_TEST_VAL'] = '-1492'
    >>> fut('RS_TEST_VAL', 42)
    42
    >>> os.environ['RS_TEST_VAL'] = '<a string>'
    >>> fut('RS_TEST_VAL', 42)
    42
    """
    return _setting_from_environ(non_negative_integer, environ_name, default, logger)


@_getter('float0')
def get_non_negative_float_from_environ(environ_name, default, logger=None):
    """
    >>> import os
    >>> from nti.property.tunables import get_non_negative_float_from_environ
    >>> os.environ['RS_TEST_VAL'] = '2.3'
    >>> get_non_negative_float_from_environ('RS_TEST_VAL', None)
    2.3
    >>> os.environ['RS_TEST_VAL'] = '-2.3'
    >>> get_non_negative_float_from_environ('RS_TEST_VAL', 1.0)
    1.0
    """
    return _setting_from_environ(non_negative_float, environ_name, default, logger)


def parse_boolean(val):
    """
    >>> from nti.property.tunables import parse_boolean
    >>> parse_boolean('0')
    False
    >>> parse_boolean('1')
    True
    >>> parse_boolean('yes')
    True
    >>> parse_boolean('no')
    False
    >>> parse_boolean('on')
    True
    >>> parse_boolean('off')
    False

    .. seealso:: :func:`ZConfig.datatypes.asBoolean`
    """
    if val == '0':
        return False
    if val == '1':
        return True
    return asBoolean(val)


@_getter('boolean')
def get_boolean_from_environ(environ_name, default, logger=None):
    """
    >>> from nti.property.tunables import get_boolean_from_environ
    >>> import os
    >>> os.environ['RS_TEST_VAL'] = 'on'
    >>> get_boolean_from_environ('RS_TEST_VAL', None)
    True


    .. seealso:: `parse_boolean`
       For accepted values.
    """
    return _setting_from_environ(parse_boolean, environ_name, default, logger)


@_getter('duration')
def get_duration_from_environ(environ_name, default, logger=None):
    """
    Return a floating-point number of seconds from the environment *environ_name*,
    or *default*.

    Examples: ``1.24s``, ``3m``, ``1m 3.6s``::

        >>> import os
        >>> from nti.property.tunables import get_duration_from_environ
        >>> os.environ['RS_TEST_VAL'] = '2.3'
        >>> get_duration_from_environ('RS_TEST_VAL', None)
        2.3
        >>> os.environ['RS_TEST_VAL'] = '5.4s'
        >>> get_duration_from_environ('RS_TEST_VAL', None)
        5.4
        >>> os.environ['RS_TEST_VAL'] = '1m 3.2s'
        >>> get_duration_from_environ('RS_TEST_VAL', None)
        63.2
        >>> os.environ['RS_TEST_VAL'] = 'Invalid' # No time specifier
        >>> get_duration_from_environ('RS_TEST_VAL', 42)
        42
        >>> os.environ['RS_TEST_VAL'] = 'Invalids' # The 's' time specifier
        >>> get_duration_from_environ('RS_TEST_VAL', 42)
        42
    """

    def convert(val):
        # The default time-interval accepts only integers; that's not fine
        # grained enough for these durations.
        if any(c in val for c in ' wdhms'):
            delta = stock_datatypes['timedelta'](val)
            return delta.total_seconds()
        return float(val)

    return _setting_from_environ(convert, environ_name, default, logger)


@_getter('byte-size')
def get_byte_size_from_environ(environ_name, default, logger=None):
    """
    Return a byte quantity from the environment variable *environ_name*,
    or *default*.

    Values can be specified in bytes without a suffix, or with a KB,
    MB, or GB suffix (case and spacing insensitive).

    No constraints are applied to the value by this function.

    >>> import os
    >>> from nti.property.tunables import get_byte_size_from_environ
    >>> os.environ['RS_TEST_VAL'] = '1024'
    >>> get_byte_size_from_environ('RS_TEST_VAL', None)
    1024
    >>> os.environ['RS_TEST_VAL'] = '1 kB'
    >>> get_byte_size_from_environ('RS_TEST_VAL', None)
    1024
    """
    return _setting_from_environ(stock_datatypes['byte-size'], environ_name, default, logger)


class Tunable:
    """
    A non-data descriptor that either returns the *default*,
    or a value from the environment.

    The value from the environment is only checked the first time the
    object is used. When used as a class variable, this is the first
    time the variable is used on any instane of the class (that is,
    class variable tunables only check the environment once, not per-instance).

    The object has a string value useful in documentation.

    .. caution::
       Some version of Sphinx has stopped actually documenting these
       things for reasons I have yet to figure out, so you should
       list the default value in the docstring.

    Instances have a ``value`` property that is set when the instance is accessed:

    >>> from nti.property.tunables import Tunable
    >>> import os
    >>> _ = os.environ.pop('RS_TEST_VAL', None)
    >>> tunable = Tunable(42, 'RS_TEST_VAL')
    >>> tunable
    <Default: 42 Environment Variable: 'RS_TEST_VAL'>
    >>> tunable.value
    42
    >>> os.environ['RS_TEST_VAL'] = '12'
    >>> tunable.value
    42

    The usual usage is as a class variable:

    >>> class T:
    ...     PROP = Tunable(42, 'RS_TEST_VAL')
    >>> T().PROP
    12
    >>> T.PROP
    <Default: 42 Environment Variable: 'RS_TEST_VAL'>
    >>> T.PROP.value
    12

    Many named datatypes are available:

    >>> os.environ['RS_TEST_VAL'] = '1'
    >>> tunable = Tunable(0, 'RS_TEST_VAL', 'boolean')
    >>> tunable.value
    True
    >>> os.environ['RS_TEST_VAL'] = '192.168.1.1:80'
    >>> tunable = Tunable(0, 'RS_TEST_VAL', 'inet-address')
    >>> tunable.value
    ('192.168.1.1', 80)

    You can supply a logger, or one will be found for you:
    >>> logger = None
    >>> Tunable(0, 'RS_TEST_VAL').logger is _logger
    True
    >>> logger = 1
    >>> Tunable(0, 'RS_TEST_VAL').logger == 1
    True
    >>> Tunable(0, 'RS_TEST_VAL', logger=42).logger == 42
    True

    """

    _NOT_SET = object()

    def __init__(self, default, env_name=None,
                 getter=get_positive_integer_from_environ,
                 logger=None):
        """
        :param str env_name: When an instance is used as a class variable (the usual
           use), an environment variable name is generated from the name of the class,
           the name of the module it is in, and the name of the class variable (e.g.,
           ``THE_MODULE_ACLASS_AN_ATTR``). This is used to override that. You must set
           this if using in a context outside of a class variable.
        :param IEnvironGetter getter: One of the ``get_`` family of functions from this module,
           or something implementing the same interface. The default is to get an integer.
           If you provide a string instead of a callable object, a utility providing
           that interface and having that name will be searched for; as a fallback, the hard-coded
           list of utilities in this module will be used.

           All of the named datatypes supported by :mod:`ZConfig.datatypes` are available
           to use as names.
        :param logger: The logger used to record information about the
           value being used. If not given, tries to find the variable named "logger"
           in the calling frame.
        """
        self.default = default
        self.env_name = env_name
        self.getter = getter
        if not callable(getter):
            getter = component.queryUtility(IEnvironGetter, name=getter,
                                            default=ENVIRON_GETTERS.get(getter))
        self.getter = getter
        if not logger:
            try:
                logger = sys._getframe(1).f_locals['logger']
            except (ValueError, KeyError, AttributeError):
                logger = _logger
        self.logger = logger or _logger
        self._value = self._NOT_SET

    def __set_name__(self, cls, name):
        if self.env_name is not None: # pragma: no cover
            return
        self.env_name = ('%s_%s_%s' % (
            cls.__module__,
            cls.__name__,
            name
        )).upper().replace('.', '_')

    def __str__(self):
        return "<Default: %r Environment Variable: %r>" % (
            self.default,
            self.env_name,
        )

    __repr__ = __str__

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        return self.value

    @property
    def value(self):
        """
        Invoke this property if you want to get the value
        when accessing the variable through the class attribute instead
        of an instance.
        """
        if self._value is self._NOT_SET:
            self._value = self.getter(self.env_name, self.default, self.logger)

        return self._value


def _register():

    class Getter:
        def __init__(self, name, converter):
            self.__name__ = name
            self.converter = converter

        def __call__(self, environ_name, default, logger):
            return _setting_from_environ(self.converter, environ_name, default, logger)

        def __repr__(self):
            return '<EnvironGetter %r=%s>' % (
                self.__name__, self.converter
            )

    for name, converter in stock_datatypes.items():
        if name in ENVIRON_GETTERS:
            continue
        _getter(name)(Getter(name, converter))
    ENVIRON_GETTERS.close()

_register()


###
# ZCML
###

class _IRegisterTunables(Interface): # pylint:disable=inherit-non-class
    # Doc tests on interfaces seem not to get run; so the doctest here
    # is at module level.
    """
    ZCML directive to register all the known IEnvironGetter implementations
    by name for the use of :class:`Tunable`.
    """


def _register_tunables(_context):

    for k, v in ENVIRON_GETTERS.items():
        registerUtility(
            _context,
            provides=IEnvironGetter,
            component=v,
            name=k
        )
