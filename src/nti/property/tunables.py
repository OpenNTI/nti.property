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

If you don't supply an environment variable name, one is derived from
the name of the class (including module) and property.

.. doctest::

   >>> __name__ = 'nti.property.tunables'
   >>> class ACls:
   ...     PROP = Tunable(42)
   >>> ACls.PROP.env_name
   'NTI_PROPERTY_TUNABLES_ACLS_PROP'


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
in both places. Known getters are:

basic-key
     :class:`ZConfig.datatypes.BasicKeyConversion`
boolean
     :func:`get_boolean_from_environ`
byte-size
     :func:`get_byte_size_from_environ`
dotted-name
     :class:`ZConfig.datatypes.DottedNameConversion`
dotted-suffix
     :class:`ZConfig.datatypes.DottedNameSuffixConversion`
duration
     :func:`get_duration_from_environ`
existing-directory
     :func:`ZConfig.datatypes.existing_directory`
existing-dirpath
     :func:`ZConfig.datatypes.existing_dirpath`
existing-file
     :func:`ZConfig.datatypes.existing_file`
existing-path
     :func:`ZConfig.datatypes.existing_path`
float
     :func:`ZConfig.datatypes.float_conversion`
float+
     :func:`get_positive_float_from_environ`
float0
     :func:`get_non_negative_float_from_environ`
identifier
     :class:`ZConfig.datatypes.IdentifierConversion`
inet-address
     :class:`ZConfig.datatypes.InetAddress`
inet-binding-address
     :class:`ZConfig.datatypes.InetAddress`
inet-connection-address
     :class:`ZConfig.datatypes.InetAddress`
integer
     :func:`ZConfig.datatypes.integer`
integer+
     :func:`get_positive_integer_from_environ`
integer0
     :func:`get_non_negative_integer_from_environ`
ipaddr-or-hostname
     :class:`ZConfig.datatypes.IpaddrOrHostname`
locale
     :class:`ZConfig.datatypes.MemoizedConversion`
null
     :func:`ZConfig.datatypes.null_conversion`
port-number
     :meth:`ZConfig.datatypes.RangeCheckedConversion.__call__`
socket-address
     :class:`builtins.type`
socket-binding-address
     :class:`builtins.type`
socket-connection-address
     :class:`builtins.type`
string
     :func:`get_string_from_environ`
string-list
     :func:`ZConfig.datatypes.string_list`
time-interval
     :class:`ZConfig.datatypes.SuffixMultiplier`
timedelta
     :func:`ZConfig.datatypes.timedelta`

.. testcleanup::

    from zope.testing import cleanup
    cleanup.cleanUp()

.. versionadded:: 2.0.0

"""
import os
import sys
import logging

from zope import component
from zope.component import named
from zope.interface import Interface
from zope.interface import provider

from ZConfig.datatypes import asBoolean
from ZConfig.datatypes import integer
from ZConfig.datatypes import RangeCheckedConversion
from ZConfig.datatypes import stock_datatypes

_logger = default_logger = logging.getLogger(__name__)

positive_integer = RangeCheckedConversion(integer, min=1)
positive_float = RangeCheckedConversion(float, min=1)

non_negative_float = RangeCheckedConversion(float, min=0)
non_negative_integer = RangeCheckedConversion(integer, min=0)

# because we use target in the log string through locals()
# pylint:disable-next=unused-argument
def _setting_from_environ(converter, environ_name, default, logger, target):
    logger = logger or _logger
    result = default
    env_val = None
    if environ_name in os.environ:
        env_val = os.environ[environ_name]
        try:
            result = converter(env_val)
        except (ValueError, TypeError):
            logger.exception(
                "Failed to parse environment value %r for key %r; will use default",
                env_val, environ_name)

    logger.info(
        'Using value %(result)s from $%(environ_name)s=%(env_val)r; '
        'default=%(default)r; target=%(target)s',
        locals())

    return result


class IEnvironGetter(Interface): # pylint:disable=inherit-non-class
    """
    A getter function for use with :class:`Tunable`.
    """
    # pylint:disable=no-self-argument
    def __call__(environ_name, default, logger=None, target=None):
        """
        Read and return an appropriately converted Python
        object from an environment variable named *environ_name*.

        If this cannot be done (the environment variable is missing
        or malformed), return the *default* value.

        Information will be logged using the :class:`logging.Logger` *logger*.
        If not provided, a default logger will be used.

        The *target* is an optional string giving context information
        about how the value is used. It is only for logging.
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

    def reset(self): # pragma: no cover
        self.clear()
        self.update(self.__orig)

    def __repr__(self):
        return "<EnvironGetters %s>" % (list(self),)

    __str__ = __repr__

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
except ImportError: # pragma: no cover
    pass
else:
    cleanup.addCleanUp(ENVIRON_GETTERS.reset)


@_getter('string')
def get_string_from_environ(environ_name, default, logger=None, target=None):
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
    return _setting_from_environ(lambda k: k, environ_name, default, logger, target)


@_getter('integer+')
def get_positive_integer_from_environ(environ_name, default, logger=None, target=None):
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
    return _setting_from_environ(positive_integer, environ_name, default, logger, target)

@_getter('float+')
def get_positive_float_from_environ(environ_name, default, logger=None, target=None):
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
    return _setting_from_environ(positive_float, environ_name, default, logger, target)


@_getter('integer0')
def get_non_negative_integer_from_environ(environ_name, default, logger=None, target=None):
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
    return _setting_from_environ(non_negative_integer, environ_name, default, logger, target)


@_getter('float0')
def get_non_negative_float_from_environ(environ_name, default, logger=None, target=None):
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
    return _setting_from_environ(non_negative_float, environ_name, default, logger, target)


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
def get_boolean_from_environ(environ_name, default, logger=None, target=None):
    """
    >>> from nti.property.tunables import get_boolean_from_environ
    >>> import os
    >>> os.environ['RS_TEST_VAL'] = 'on'
    >>> get_boolean_from_environ('RS_TEST_VAL', None)
    True


    .. seealso:: `parse_boolean`
       For accepted values.
    """
    return _setting_from_environ(parse_boolean, environ_name, default, logger, target)


@_getter('duration')
def get_duration_from_environ(environ_name, default, logger=None, target=None):
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

    return _setting_from_environ(convert, environ_name, default, logger, target)


@_getter('byte-size')
def get_byte_size_from_environ(environ_name, default, logger=None, target=None):
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
    return _setting_from_environ(stock_datatypes['byte-size'], environ_name,
                                 default, logger, target)

# TODO: Add a getter for reading a JSON object.
# TODO: Add a public way to reset a Tunable.
# TODO: Keep a weak reference to all Tunables, and reset them during
# test cleanup.

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

    You can supply a logger, or one will be found for you
    by looking for a 'logger' in the calling frames:

    >>> from nti.property.tunables import default_logger
    >>> logger = None
    >>> Tunable(0, 'RS_TEST_VAL').logger is default_logger
    True
    >>> logger = "from parent frame"
    >>> Tunable(0, 'RS_TEST_VAL').logger
    'from parent frame'
    >>> Tunable(0, 'RS_TEST_VAL', logger=42).logger
    42
    >>> class WithTunable:
    ...   TUNABLE = Tunable(0, 'RS_TEST_VAL')
    >>> WithTunable.TUNABLE.logger
    'from parent frame'

    If the closest logger that we find isn't a
    real logger, but we find one farther away that _is_ a
    real logger, we'll use that one:

    >>> import logging
    >>> real_logger = logging.getLogger('real.logger')
    >>> def make_class():
    ...    logger = real_logger
    ...    def do_it():
    ...        logger = 'not a real logger'
    ...        class WithTunable:
    ...           TUNABLE = Tunable(0, 'RS_TEST_VAL')
    ...        return WithTunable
    ...    return do_it()
    >>> WithTunable = make_class()
    >>> WithTunable.TUNABLE.logger is real_logger
    True
    """

    _NOT_SET = object()
    _target_name = ''

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
           in a calling frame that looks-like a logger.

        .. versionchanged:: 2.0.2
           Now searches harder up the call chain to find a logger,
           and accepts the first one that looks-like a logger. If no
           real logger can be found, then the first 'logger' variable we see
           is used.
        """
        self.default = default
        self.env_name = env_name
        self.getter = getter
        if not callable(getter):
            getter = component.queryUtility(IEnvironGetter, name=getter,
                                            default=ENVIRON_GETTERS.get(getter))
        self.getter = getter
        self.logger = logger or self._find_logger() or _logger
        self._value = self._NOT_SET

    @staticmethod
    def _find_logger():
        logger = None
        closest_candidate = None
        try:
            frame = sys._getframe(1) # pylint:disable=protected-access
        except (AttributeError, ValueError): # pragma: no cover
            # Attribute: Not implemented; Value: wrong depth
            frame = None

        while frame is not None:
            candidate = frame.f_locals.get('logger')
            closest_candidate = closest_candidate or candidate
            if hasattr(candidate, 'log'):
                logger = candidate
                break
            frame = frame.f_back
        return logger or closest_candidate


    def __set_name__(self, cls, name):
        self._target_name = cls.__name__ + '.' + name
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
            self._value = self.getter(self.env_name, self.default,
                                      self.logger, self._target_name)

        return self._value


def _register():

    class Getter:
        def __init__(self, name, converter):
            self.__name__ = name
            self.converter = converter

        def __call__(self, environ_name, default, logger, target=None):
            return _setting_from_environ(self.converter, environ_name, default, logger, target)

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
    # This is our ZCML handler, so if we're here, we're being called from
    # zope.configuration; zope.component.zcml requires zope.configuration
    from zope.component.zcml import utility as registerUtility
    for k, v in ENVIRON_GETTERS.items():
        registerUtility(
            _context,
            provides=IEnvironGetter,
            component=v,
            name=k
        )

# This snippet generates the documentation:


def _generate_docs(): # pragma: no cover
    func_type = type(lambda: None)
    class O:
        def m(self):
            """Nothing."""
    meth_type = type(O().m)

    def ref(item):
        if hasattr(item, 'converter'):
            item = item.converter
        if isinstance(item, func_type):
            if item.__module__ == 'nti.property.tunables':
                return ':func:`%s`' % (item.__name__,)
            return ':func:`%s.%s`' % (item.__module__, item.__name__)

        if isinstance(item, meth_type):
            kind = type(item.__self__)
            return ':meth:`%s.%s.%s`' % (
                kind.__module__,
                kind.__name__,
                item.__name__
            )
        return ':class:`%s.%s`' % (
            type(item).__module__,
            type(item).__name__
        )
    for k, v in sorted(ENVIRON_GETTERS.items()):
        print(k)
        print('    ', ref(v))
