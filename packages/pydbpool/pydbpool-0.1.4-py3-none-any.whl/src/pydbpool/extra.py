# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : extra.py
@Project  : 
@Time     : 2025/3/18 10:52
@Author   : dylan
@Contact Email: cgq2012516@163.com
"""

from __future__ import annotations

import collections.abc as collections_abc
import re
from typing import (
    Any,
    cast,
    Dict,
    Iterable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    overload,
    Sequence,
    Tuple,
    Union,
)
from typing_extensions import TypeGuard as TypeGuard  # 3.10

from urllib.parse import (
    parse_qsl,
    quote,
    unquote,
)

from .errors import ArgumentError


class URL(NamedTuple):
    """
    Represent the components of a URL used to connect to a database.

    URLs are typically constructed from a fully formatted URL string, where the
    :func:`.make_url` function is used internally by the
    :func:`_sa.create_engine` function in order to parse the URL string into
    its individual components, which are then used to construct a new
    :class:`.URL` object. When parsing from a formatted URL string, the parsing
    format generally follows
    `RFC-1738 <https://www.ietf.org/rfc/rfc1738.txt>`_, with some exceptions.

    A :class:`_engine.URL` object may also be produced directly, either by
    using the :func:`.make_url` function with a fully formed URL string, or
    by using the :meth:`_engine.URL.create` constructor in order
    to construct a :class:`_engine.URL` programmatically given individual
    fields. The resulting :class:`.URL` object may be passed directly to
    :func:`_sa.create_engine` in place of a string argument, which will bypass
    the usage of :func:`.make_url` within the engine's creation process.

    .. versionchanged:: 1.4

        The :class:`_engine.URL` object is now an immutable object.  To
        create a URL, use the :func:`_engine.make_url` or
        :meth:`_engine.URL.create` function / method.  To modify
        a :class:`_engine.URL`, use methods like
        :meth:`_engine.URL.set` and
        :meth:`_engine.URL.update_query_dict` to return a new
        :class:`_engine.URL` object with modifications.   See notes for this
        change at :ref:`change_5526`.

    .. seealso::

        :ref:`database_urls`

    :class:`_engine.URL` contains the following attributes:

    * :attr: database backend and driver name, such as
      ``postgresql+psycopg2``
    * :attr: username string
    * :attr: password string
    * :attr: string hostname
    * :attr: integer port number
    * :attr: string database name
      string.  contains strings for keys and either strings or tuples of
      strings for values.


    """

    drivername: str
    """database backend and driver name, such as
    ``postgresql+psycopg2``

    """

    username: Optional[str]
    "username string"

    password: Optional[str]
    """password, which is normally a string but may also be any
    object that has a ``__str__()`` method."""

    host: Optional[str]
    """hostname or IP number.  May also be a data source name for some
    drivers."""

    port: Optional[int]
    """integer port number"""

    database: Optional[str]
    """database name"""

    @classmethod
    def create(
            cls,
            drivername: str,
            username: Optional[str] = None,
            password: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[int] = None,
            database: Optional[str] = None,
    ) -> URL:
        """Create a new :class:`_engine.URL` object.

        .. seealso::

            :ref:`database_urls`

        :param drivername: the name of the database backend. This name will
          correspond to a module in sqlalchemy/databases or a third party
          plug-in.
        :param username: The user name.
        :param password: database password.  Is typically a string, but may
          also be an object that can be stringified with ``str()``.

          .. note:: The password string should **not** be URL encoded when
             passed as an argument to :meth:`_engine.URL.create`; the string
             should contain the password characters exactly as they would be
             typed.

          .. note::  A password-producing object will be stringified only
             **once** per :class:`_engine.Engine` object.  For dynamic password
             generation per connect, see :ref:`engines_dynamic_tokens`.

        :param host: The name of the host.
        :param port: The port number.
        :param database: The database name.
        :param query: A dictionary of string keys to string values to be passed
          to the dialect and/or the DBAPI upon connect.   To specify non-string
          parameters to a Python DBAPI directly, use the
          :paramref:`_sa.create_engine.connect_args` parameter to
          :func:`_sa.create_engine`.   See also
          :attr:`_engine.URL.normalized_query` for a dictionary that is
          consistently string->list of string.
        :return: new :class:`_engine.URL` object.

        .. versionadded:: 1.4

            The :class:`_engine.URL` object is now an **immutable named
            tuple**.  In addition, the ``query`` dictionary is also immutable.
            To create a URL, use the :func:`_engine.url.make_url` or
            :meth:`_engine.URL.create` function/ method.  To modify a
            :class:`_engine.URL`, use the :meth:`_engine.URL.set` and
            :meth:`_engine.URL.update_query` methods.

        """

        return cls(
            cls._assert_str(drivername, "drivername"),
            cls._assert_none_str(username, "username"),
            password,
            cls._assert_none_str(host, "host"),
            cls._assert_port(port),
            cls._assert_none_str(database, "database"),
        )

    @classmethod
    def _assert_port(cls, port: Optional[int]) -> Optional[int]:
        if port is None:
            return None
        try:
            return int(port)
        except TypeError:
            raise TypeError("Port argument must be an integer or None")

    @classmethod
    def _assert_str(cls, v: str, paramname: str) -> str:
        if not isinstance(v, str):
            raise TypeError("%s must be a string" % paramname)
        return v

    @classmethod
    def _assert_none_str(
            cls, v: Optional[str], paramname: str
    ) -> Optional[str]:
        if v is None:
            return v

        return cls._assert_str(v, paramname)

    @classmethod
    def _str_dict(
            cls,
            dict_: Optional[
                Union[
                    Sequence[Tuple[str, Union[Sequence[str], str]]],
                    Mapping[str, Union[Sequence[str], str]],
                ]
            ],
    ) -> Dict[str, Union[Tuple[str, ...], str]]:
        if dict_ is None:
            return {}

        @overload
        def _assert_value(
                val: str,
        ) -> str:
            ...

        @overload
        def _assert_value(
                val: Sequence[str],
        ) -> Union[str, Tuple[str, ...]]:
            ...

        def _assert_value(
                val: Union[str, Sequence[str]],
        ) -> Union[str, Tuple[str, ...]]:
            if isinstance(val, str):
                return val
            elif isinstance(val, collections_abc.Sequence):
                return tuple(_assert_value(elem) for elem in val)
            else:
                raise TypeError(
                    "Query dictionary values must be strings or "
                    "sequences of strings"
                )

        def _assert_str(v: str) -> str:
            if not isinstance(v, str):
                raise TypeError("Query dictionary keys must be strings")
            return v

        dict_items: Iterable[Tuple[str, Union[Sequence[str], str]]]
        if isinstance(dict_, collections_abc.Sequence):
            dict_items = dict_
        else:
            dict_items = dict_.items()

        return dict(
            {
                _assert_str(key): _assert_value(
                    value,
                )
                for key, value in dict_items
            }
        )

    def set(
            self,
            drivername: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            host: Optional[str] = None,
            port: Optional[int] = None,
            database: Optional[str] = None,
            query: Optional[Mapping[str, Union[Sequence[str], str]]] = None,
    ) -> URL:
        """return a new :class:`_engine.URL` object with modifications.

        Values are used if they are non-None.  To set a value to ``None``
        explicitly, use the :meth:`_engine.URL._replace` method adapted
        from ``namedtuple``.

        :param database:
        :param drivername: new drivername
        :param username: new username
        :param password: new password
        :param host: new hostname
        :param port: new port
        :param query: new query parameters, passed a dict of string keys
         referring to string or sequence of string values.  Fully
         replaces the previous list of arguments.

        :return: new :class:`_engine.URL` object.

        .. versionadded:: 1.4

        .. seealso::

            :meth:`_engine.URL.update_query_dict`

        """

        kw: Dict[str, Any] = {}
        if drivername is not None:
            kw["drivername"] = drivername
        if username is not None:
            kw["username"] = username
        if password is not None:
            kw["password"] = password
        if host is not None:
            kw["host"] = host
        if port is not None:
            kw["port"] = port
        if database is not None:
            kw["database"] = database

        return self._assert_replace(**kw)

    def _assert_replace(self, **kw: Any) -> URL:
        """argument checks before calling _replace()"""

        if "drivername" in kw:
            self._assert_str(kw["drivername"], "drivername")
        for name in "username", "host", "database":
            if name in kw:
                self._assert_none_str(kw[name], name)
        if "port" in kw:
            self._assert_port(kw["port"])

        return self._replace(**kw)

    def render_as_string(self, hide_password: bool = True) -> str:
        """Render this :class:`_engine.URL` object as a string.

        This method is used when the ``__str__()`` or ``__repr__()``
        methods are used.   The method directly includes additional options.

        :param hide_password: Defaults to True.   The password is not shown
         in the string unless this is set to False.

        """
        s = self.drivername + "://"
        if self.username is not None:
            s += quote(self.username, safe=" +")
            if self.password is not None:
                s += ":" + (
                    "***"
                    if hide_password
                    else quote(str(self.password), safe=" +")
                )
            s += "@"
        if self.host is not None:
            if ":" in self.host:
                s += f"[{self.host}]"
            else:
                s += self.host
        if self.port is not None:
            s += ":" + str(self.port)
        if self.database is not None:
            s += "/" + self.database
        return s

    def __repr__(self) -> str:
        return self.render_as_string()

    def __copy__(self) -> URL:
        return self.__class__.create(
            self.drivername,
            self.username,
            self.password,
            self.host,
            self.port,
            self.database,
        )

    def __deepcopy__(self, memo: Any) -> URL:
        return self.__copy__()

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: Any) -> bool:
        return (
                isinstance(other, URL)
                and self.drivername == other.drivername
                and self.username == other.username
                and self.password == other.password
                and self.host == other.host
                and self.database == other.database
                and self.port == other.port
        )

    def __ne__(self, other: Any) -> bool:
        return not self == other


def make_url(name_or_url: Union[str, URL]) -> URL:
    """
    Given a string, produce a new URL instance. that like sqlalchemy supported
    eg.
    """

    if isinstance(name_or_url, str):
        return _parse_url(name_or_url)
    elif not isinstance(name_or_url, URL) and not hasattr(
            name_or_url, "_sqla_is_testing_if_this_is_a_mock_object"
    ):
        raise ArgumentError(
            f"Expected string or URL object, got {name_or_url!r}"
        )
    else:
        return name_or_url


def _parse_url(name: str) -> URL:
    pattern = re.compile(
        r"""
            (?P<name>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>[^@]*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/\?]+)\] |
                    (?P<ipv4host>[^/:\?]+)
                )?
                (?::(?P<port>[^/\?]*))?
            )?
            (?:/(?P<database>[^\?]*))?
            (?:\?(?P<query>.*))?
            """,
        re.X,
    )

    m = pattern.match(name)
    if m is not None:
        components = m.groupdict()
        query: Optional[Dict[str, Union[str, List[str]]]]
        if components["query"] is not None:
            query = {}

            for key, value in parse_qsl(components["query"]):
                if key in query:
                    query[key] = to_list(query[key])
                    cast("List[str]", query[key]).append(value)
                else:
                    query[key] = value
        else:
            query = None
        components["query"] = query

        if components["username"] is not None:
            components["username"] = unquote(components["username"])

        if components["password"] is not None:
            components["password"] = unquote(components["password"])

        ipv4host = components.pop("ipv4host")
        ipv6host = components.pop("ipv6host")
        components["host"] = ipv4host or ipv6host
        name = components.pop("name")

        if components["port"]:
            components["port"] = int(components["port"])

        return URL.create(name, **components)  # type: ignore

    else:
        raise ArgumentError(
            "Could not parse SQLAlchemy URL from string '%s'" % name
        )


def to_list(x: Any, default: Optional[List[Any]] = None) -> List[Any]:
    if x is None:
        return default  # type: ignore
    if not is_non_string_iterable(x):
        return [x]
    elif isinstance(x, list):
        return x
    else:
        return list(x)


def is_non_string_iterable(obj: Any) -> TypeGuard[Iterable[Any]]:
    return isinstance(obj, collections_abc.Iterable) and not isinstance(
        obj, (str, bytes)
    )
