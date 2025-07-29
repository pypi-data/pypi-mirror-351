# -*- coding: utf-8 -*-
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
# Copyright (c) 2019 Daniel Hornung
# Copyright (C) 2024 Indiscale GmbH <info@indiscale.com>
# Copyright (C) 2024 Joscha Schmiedt <joscha@schmiedt.dev>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ** end header
#
"""Connection to a LinkAhead server."""
from __future__ import annotations

import logging
import ssl
import sys
import warnings
from builtins import str  # pylint: disable=redefined-builtin
from errno import EPIPE as BrokenPipe
from socket import error as SocketError
from urllib.parse import ParseResult, quote, urlparse

from requests import Session as HTTPSession
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as HTTPConnectionError
from urllib3.poolmanager import PoolManager

from ..configuration import get_config, config_to_yaml
from ..exceptions import (ConfigurationError, HTTPClientError,
                          HTTPForbiddenError, HTTPResourceNotFoundError,
                          HTTPServerError, HTTPURITooLongError,
                          LinkAheadConnectionError, LinkAheadException,
                          LoginFailedError)

try:
    from ..version import version               # pylint: disable=import-error
except ModuleNotFoundError:
    version = "uninstalled"

from .encode import MultipartYielder, ReadableMultiparts
from .interface import CaosDBHTTPResponse, CaosDBServerConnection
from .utils import make_uri_path, urlencode

from typing import TYPE_CHECKING
from .authentication.interface import CredentialsAuthenticator
if TYPE_CHECKING:
    from typing import Optional, Any, Iterator, Union
    from requests.models import Response
    from ssl import _SSLMethod              # pylint: disable=no-name-in-module
    from .authentication.interface import AbstractAuthenticator


_LOGGER = logging.getLogger(__name__)


class _WrappedHTTPResponse(CaosDBHTTPResponse):

    def __init__(self, response: Response):
        self.response: Response = response
        self._generator: Optional[Iterator[Any]] = None
        self._buffer: Optional[bytes] = b''
        self._stream_consumed: bool = False

    @property
    def reason(self):
        return self.response.reason

    @property
    def status(self):
        return self.response.status_code

    def read(self, size: Optional[int] = None):
        # FIXME This function behaves unexpectedly if `size` is larger than in the first run.

        if self._stream_consumed is True:
            raise BufferError("Stream is consumed")

        if self._buffer is None:
            # the buffer has been drained in the previous call.
            self._stream_consumed = True
            return b''

        if self._generator is None and (size is None or size == 0):
            # return full content at once
            self._stream_consumed = True
            return self.response.content

        if size is None or size == 0:
            raise BufferError(
                "`size` parameter can not be None or zero once reading has started with a non-zero "
                "value.")

        if len(self._buffer) >= size:
            # still enough bytes in the buffer
            result = self._buffer[:size]
            self._buffer = self._buffer[size:]
            return result

        if self._generator is None:
            # first call to this method
            if size is None or size == 0:
                size = 512
            self._generator = self.response.iter_content(size)

        try:
            # read new data into the buffer
            chunk = self._buffer + next(self._generator)
            result = chunk[:size]  # FIXME what if `size` is larger than at `iter_content(size)`?
            if len(result) == 0:
                self._stream_consumed = True
            self._buffer = chunk[size:]
            return result
        except StopIteration:
            # drain buffer
            last_result = self._buffer
            self._buffer = None
            return last_result

    def getheader(self, name: str, default=None):
        return self.response.headers[name] if name in self.response.headers else default

    def getheaders(self):
        return self.response.headers.items()

    def close(self):
        self.response.close()


class _SSLAdapter(HTTPAdapter):
    """Transport adapter that allows us to use different SSL versions."""

    def __init__(self, ssl_version: _SSLMethod):
        self.ssl_version = ssl_version
        super().__init__()

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_version=self.ssl_version)


class _DefaultCaosDBServerConnection(CaosDBServerConnection):
    """_DefaultCaosDBServerConnection.

    Methods
    -------
    configure
    request
    """

    def __init__(self):
        self._useragent = ("linkahead-pylib/{version} - {implementation}".format(
            version=version, implementation=type(self).__name__))
        self._base_path = None
        self._session = None
        self._timeout = None

    def request(self,
                method: str, path: str,
                headers: Optional[dict[str, str]] = None,
                body: Union[str, bytes, None] = None,
                **kwargs) -> _WrappedHTTPResponse:
        """request.

        Send a HTTP request to the server.

        Parameters
        ----------
        method : str
            The HTTP request method.
        path : str
            An URI path segment (without the 'scheme://host:port/' parts),
            including query and frament segments.
        headers : dict of str -> str, optional
            HTTP request headers. (Default: None)
        body : str or bytes or readable, optional
            The body of the HTTP request. Bytes should be a utf-8 encoded
            string.

        Returns
        -------
        response : _WrappedHTTPResponse
        """

        if headers is None:
            headers = {}
        headers["User-Agent"] = self._useragent

        if path.endswith("/."):
            path = path[:-1] + "%2E"

        if isinstance(body, MultipartYielder):
            body = ReadableMultiparts(body)

        try:
            response = self._session.request(
                method=method,
                url=self._base_path + path,
                headers=headers,
                data=body,
                timeout=self._timeout,
                stream=True)

            return _WrappedHTTPResponse(response)
        except HTTPConnectionError as conn_err:
            raise LinkAheadConnectionError(
                "Connection failed. Network or server down? " + str(conn_err)
            )

    def configure(self, **config) -> None:
        """configure.

        Configure the http connection.

        Parameters
        ----------
        cacert : str
            Path to the CA certificate which will be used to identify the
            server.
        url : str
            The url of the LinkAhead Server, e.g.
            `https://example.com:443/rootpath`, including a possible root path.
        **config :
            Any further keyword arguments are being ignored.

        Raises
        ------
        LinkAheadConnectionError
            If no url has been specified, or if the CA certificate cannot be
            loaded.
        """

        if "url" not in config:
            raise LinkAheadConnectionError(
                "No connection url specified. Please "
                "do so via linkahead.configure_connection(...) or in a config "
                "file.")
        url_string: str = config["url"]
        if (not url_string.lower().startswith("https://")
                and not url_string.lower().startswith("http://")):
            raise LinkAheadConnectionError("The connection url is expected "
                                           "to be a http or https url and "
                                           "must include the url scheme "
                                           "(i.e. start with https:// or "
                                           "http://).")

        url: ParseResult = urlparse(url=url_string)
        path = url.path.strip("/")
        if len(path) > 0:
            path = path + "/"
        self._base_path = url.scheme + "://" + url.netloc + "/" + path

        self._session = HTTPSession()

        if url.scheme == "https":
            self._setup_ssl(config)

        # TODO(tf) remove in next release
        socket_proxy = config["socket_proxy"] if "socket_proxy" in config else None
        if socket_proxy is not None:
            self._session.proxies = {
                "https": "socks5://" + socket_proxy,
                "http": "socks5://" + socket_proxy,
            }

        if "https_proxy" in config:
            if self._session.proxies is None:
                self._session.proxies = {}
            self._session.proxies["https"] = config["https_proxy"]

        if "http_proxy" in config:
            if self._session.proxies is None:
                self._session.proxies = {}
            self._session.proxies["http"] = config["http_proxy"]

        if "timeout" in config:
            self._timeout = config["timeout"]

    def _setup_ssl(self, config: dict[str, Any]):
        if "ssl_version" in config and config["cacert"] is not None:
            ssl_version = getattr(ssl, config["ssl_version"])
        else:
            ssl_version = ssl.PROTOCOL_TLS

        self._session.mount(self._base_path, _SSLAdapter(ssl_version))

        verify = True
        if "cacert" in config:
            verify = config["cacert"]
        if "ssl_insecure" in config and config["ssl_insecure"]:
            _LOGGER.warning("*** Warning! ***\n"
                            "Insecure SSL mode, certificate will not be checked! "
                            "Please consider removing the `ssl_insecure` configuration option.\n"
                            "****************")
            warnings.filterwarnings(action="ignore", module="urllib3",
                                    message="Unverified HTTPS request is being made")
            verify = False
        if verify is not None:
            self._session.verify = verify


def _make_conf(*conf):
    """_make_conf.

    Merge several config dicts into one. The precedence goes to latter dicts in
    the function call.

    Parameters
    ----------
    *conf : dict
        One ore more dicts with lower case option names (i.e. keys).

    Returns
    -------
    dict
        A merged config dict.
    """
    result = {}

    for conf_dict in conf:
        result.update(conf_dict)

    return result


_DEFAULT_CONF = {
    "password_method": "input",
    "implementation": _DefaultCaosDBServerConnection,
    "timeout": 210,
}


def _get_authenticator(**config) -> AbstractAuthenticator:
    """_get_authenticator.

    Import and configure the password_method.

    Parameters
    ----------
    password_method : str
        The simple name of a submodule of linkahead.connection.authentication.
        Currently, there are four valid values for this parameter: 'plain',
        'pass', 'keyring' and 'auth_token'.
    **config :
        Any other keyword arguments are passed the configure method of the
        password_method.

    Returns
    -------
    AbstractAuthenticator
        An object which implements the password_method and which already
        configured.

    Raises
    ------
    ConfigurationError
        If the password_method string cannot be resolved to a LinkaheadAuthenticator
        class.
    """
    auth_module = ("linkahead.connection.authentication." +
                   config["password_method"])
    _LOGGER.debug("import auth_module %s", auth_module)
    try:
        __import__(auth_module)

        auth_provider = sys.modules[auth_module].get_authentication_provider()
        auth_provider.configure(**config)

        return auth_provider

    except ImportError:
        raise ConfigurationError("Password method \"{}\" not implemented. "
                                 "Try `plain`, `pass`, `keyring`, or "
                                 "`auth_token`."
                                 .format(config["password_method"]))


def configure_connection(**kwargs):
    """Configures the LinkAhead connection and returns the Connection object.

    The effective configuration is governed by the default values (see
    'Parameters'), the global configuration (see `linkahead.get_config()`) and the
    parameters which are passed to this function, with ascending priority.

    The parameters which are listed here, are possibly not sufficient for a
    working configuration of the connection. Check the `configure` method of
    the implementation class and the password_method for more details.

    Parameters
    ----------
    url : str
        The url of the LinkAhead Server. HTTP and HTTPS urls are allowed. However,
        it is **highly** recommend to avoid HTTP because passwords and
        authentication token are send over the network in plain text.

    username : str
        Username for login; e.g. 'admin'.

    password : str
        Password for login if 'plain' is used as password_method.

    password_method : str
        The name of a submodule of linkahead.connection.authentication which
        implements the AbstractAuthenticator interface. (Default: 'plain')
        Possible values are, for example:
        - "plain"    Need username and password arguments.
        - "input"    Asks for the password.
        - "pass"     Uses the `pass` password manager.
        - "keyring"  Uses the `keyring` library.
        - "auth_token" Uses only a given auth_token.

    timeout : int, tuple, or None
        A connection timeout in seconds. (Default: 210)
        If a tuple is given, they are used as connect and read timeouts
        respectively, timeout None disables the timeout.

    ssl_insecure : bool
        Whether SSL certificate warnings should be ignored. Only use this for
        development purposes! (Default: False)

    auth_token : str (optional)
        An authentication token which has been issued by the LinkAhead Server.
        Implies `password_method="auth_token"` if set.  An example token string would be
        ``["O","OneTimeAuthenticationToken","anonymous",["administration"],[],1592995200000,
          604800000,"3ZZ4WKRB-5I7DG2Q6-ZZE6T64P-VQ","197d0d081615...1ee9",1,30000]``.

    https_proxy : str, optional
        Define a proxy for the https connections, e.g. `http://localhost:8888`,
        `socks5://localhost:8888`, or `socks4://localhost:8888`. These are
        either (non-TLS) HTTP proxies, SOCKS4 proxies, or SOCKS5 proxies. HTTPS
        proxies are not supported. However, the connection will be secured
        using TLS in the tunneled connection nonetheless. Only the connection
        to the proxy is insecure which is why it is not recommended to use HTTP
        proxies when authentication against the proxy is necessary. If
        unspecified, the https_proxy option of the pylinkahead.ini or the HTTPS_PROXY
        environment variable are being used. Use `None` to override these
        options with a no-proxy setting.

    http_proxy : str, optional
        Define a proxy for the http connections, e.g. `http://localhost:8888`.
        If unspecified, the http_proxy option of the pylinkahead.ini or the
        HTTP_PROXY environment variable are being used. Use `None` to override
        these options with a no-proxy setting.

    implementation : CaosDBServerConnection
        The class which implements the connection. (Default:
        _DefaultCaosDBServerConnection)

    Returns
    -------
    _Connection
        The singleton instance of the _Connection class.
    """
    global_conf = {}
    conf = get_config()
    # Convert config to dict, with preserving types
    int_opts = []
    bool_opts = ["ssl_insecure"]
    other_opts = ["timeout"]

    if conf.has_section("Connection"):
        global_conf = dict(conf.items("Connection"))

        # Integer options
        for opt in int_opts:
            if opt in global_conf:
                global_conf[opt] = conf.getint("Connection", opt)

        # Boolean options
        for opt in bool_opts:
            if opt in global_conf:
                global_conf[opt] = conf.getboolean("Connection", opt)

        # Other options, defer parsing to configuration.config_to_yaml:
        connection_config = config_to_yaml(conf)["Connection"]
        for opt in other_opts:
            if opt in global_conf:
                global_conf[opt] = connection_config[opt]

    local_conf = _make_conf(_DEFAULT_CONF, global_conf, kwargs)

    connection = _Connection.get_instance()

    if "socket_proxy" in local_conf:
        warnings.warn("Deprecated configuration option: socket_proxy. Use "
                      "the new https_proxy option instead",
                      DeprecationWarning, stacklevel=1)
    connection.configure(**local_conf)

    return connection


def get_connection():
    """Return the connection.

    If the connection was not configured yet `configure_connection` will
    be called inside this function without arguments.
    """
    connection = _Connection.get_instance()

    if connection.is_configured:
        return connection

    return configure_connection()


def _handle_response_status(http_response):

    status = http_response.status

    if status == 200:
        return

    # emtpy response buffer
    body = http_response.read()

    if status == 404:
        raise HTTPResourceNotFoundError("This resource has not been found.")
    elif status > 499:
        raise HTTPServerError(body=body)

    reason = http_response.reason
    standard_message = ("Request failed. The response returned with status "
                        "{} - {}.".format(status, reason))
    if status == 401:
        raise LoginFailedError(standard_message)
    elif status == 403:
        raise HTTPForbiddenError(standard_message)
    elif status in (413, 414, 431):
        # Content (413), URI (414) or complete HTTP headers (URI+headers) (431) too long
        raise HTTPURITooLongError(standard_message)
    elif 399 < status < 500:
        raise HTTPClientError(msg=standard_message, status=status, body=body)
    else:
        raise LinkAheadException(standard_message)


class _Connection(object):  # pylint: disable=useless-object-inheritance
    """This connection class provides the interface to the database connection
    allowing for retrieval, insertion, update, etc. of entities, files, users,
    roles and much more.

    It wrapps an instance of CaosDBServerConnection which actually does the
    work (how, depends on the instance).

    It is a singleton and should not be instanciated or modified by any client.
    Use the methods `get_connection` and `configure_connection` for this
    purpose.
    """

    __instance = None

    def __init__(self) -> None:
        self._delegate_connection: Optional[CaosDBServerConnection] = None
        self._authenticator: Optional[AbstractAuthenticator] = None
        self.is_configured = False

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls.__instance = _Connection()

        return cls.__instance

    def configure(self, **config) -> _Connection:
        self.is_configured = True

        if "implementation" not in config:
            raise ConfigurationError(
                "Missing CaosDBServerConnection implementation. You did not "
                "specify an `implementation` for the connection.")
        try:
            self._delegate_connection = config["implementation"]()

            if not isinstance(self._delegate_connection,
                              CaosDBServerConnection):
                raise TypeError("The `implementation` callable did not return "
                                "an instance of CaosDBServerConnection.")
        except TypeError as type_err:
            raise ConfigurationError(
                "Bad CaosDBServerConnection implementation. The "
                "implementation must be a callable object which returns an "
                "instance of `CaosDBServerConnection` (e.g. a constructor "
                "or a factory).\n{}".format(type_err.args[0]))
        self._delegate_connection.configure(**config)

        if "auth_token" in config:
            # deprecated, needed for older scripts
            config["password_method"] = "auth_token"
        if "password_method" not in config:
            raise ConfigurationError("Missing password_method. You did "
                                     "not specify a `password_method` for"
                                     "the connection.")
        self._authenticator = _get_authenticator(
            connection=self._delegate_connection, **config)

        return self

    def retrieve(self,
                 entity_uri_segments: Optional[list[str]] = None,
                 query_dict: Optional[dict[str, Optional[str]]] = None,
                 **kwargs) -> CaosDBHTTPResponse:
        path = make_uri_path(entity_uri_segments, query_dict)

        http_response = self._http_request(method="GET", path=path, **kwargs)

        return http_response

    def delete(self, entity_uri_segments: Optional[list[str]] = None,
               query_dict: Optional[dict[str, Optional[str]]] = None, **kwargs) -> (
                   CaosDBHTTPResponse):
        path = make_uri_path(entity_uri_segments, query_dict)

        http_response = self._http_request(
            method="DELETE", path=path, **kwargs)

        return http_response

    def update(self, entity_uri_segment: Optional[list[str]],
               query_dict: Optional[dict[str, Optional[str]]] = None, **kwargs) -> (
                   CaosDBHTTPResponse):
        path = make_uri_path(entity_uri_segment, query_dict)

        http_response = self._http_request(method="PUT", path=path, **kwargs)

        return http_response

    def activate_user(self, link: str) -> CaosDBHTTPResponse:
        if self._authenticator is not None:
            self._authenticator.logout()
        fullurl = urlparse(link)
        path = fullurl.path
        query = fullurl.query
        http_response = self._http_request(
            method="GET", path=path + "?" + query)

        return http_response

    def put_form_data(self, entity_uri_segment: str, params) -> CaosDBHTTPResponse:
        return self._form_data_request(
            method="PUT", path=entity_uri_segment, params=params)

    def post_form_data(self, entity_uri_segment: str, params: dict[str, Optional[str]]) -> (
            CaosDBHTTPResponse):
        return self._form_data_request(
            method="POST",
            path=entity_uri_segment,
            params=params)

    def _form_data_request(self, method: str, path: str, params: dict[str, Optional[str]]) -> (
            CaosDBHTTPResponse):
        body = urlencode(params)
        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        response = self._http_request(
            method=method,
            path=quote(path),
            body=body,
            headers=headers)

        return response

    def insert(self, entity_uri_segment:  Optional[list[str]],
               query_dict: Optional[dict[str, Optional[str]]] = None,
               body: Union[str, bytes, None] = None, **kwargs) -> CaosDBHTTPResponse:
        path = make_uri_path(entity_uri_segment, query_dict)

        http_response = self._http_request(
            method="POST", path=path, body=body, **kwargs)

        return http_response

    def download_file(self, path: str):
        """This function downloads a file via HTTP from the LinkAhead file
        system."""
        try:
            uri_segments = ["FileSystem"]
            uri_segments.extend(path.split("/"))

            return self.retrieve(entity_uri_segments=uri_segments)
        except HTTPResourceNotFoundError:
            raise HTTPResourceNotFoundError("This file does not exist.")

    def _login(self):
        self._authenticator.login()

    def _logout(self):
        self._authenticator.logout()

    def _http_request(self, method: str, path: str,
                      headers: Optional[dict["str", Any]] = None,
                      body: Union[str, bytes, None] = None, **kwargs):
        try:
            return self._retry_http_request(method=method, path=path,
                                            headers=headers, body=body,
                                            **kwargs)
        except SocketError as e:
            if e.errno != BrokenPipe:
                raise

            return self._retry_http_request(method=method, path=path,
                                            headers=headers, body=body,
                                            reconnect=False,
                                            **kwargs)
        except LoginFailedError:
            if kwargs.get("reconnect", True) is True:
                self._login()

                return self._retry_http_request(method=method, path=path,
                                                headers=headers, body=body,
                                                reconnect=False,
                                                **kwargs)
            raise

    def _retry_http_request(self,
                            method: str,
                            path: str,
                            headers: Optional[dict["str", Any]],
                            body: Union[str, bytes, None], **kwargs) -> CaosDBHTTPResponse:

        if hasattr(body, "encode") and body is not None:
            # python3
            body = body.encode("utf-8")

        if headers is None:
            headers = {}

        if self._authenticator is None:
            raise ValueError(
                "No authenticator set. Please call configure_connection() first.")

        self._authenticator.on_request(method=method, path=path,
                                       headers=headers)

        if self._delegate_connection is None:
            raise ValueError(
                "No connection set. Please call configure_connection() first.")

        _LOGGER.debug("request: %s %s %s", method, path, str(headers))
        http_response = self._delegate_connection.request(
            method=method,
            path=path,
            headers=headers,
            body=body)
        _LOGGER.debug("response: %s %s", str(http_response.status),
                      str(http_response.getheaders()))
        self._authenticator.on_response(http_response)
        _handle_response_status(http_response)

        return http_response

    def get_username(self) -> str:
        """
        Return the username of the current connection.

        Shortcut for: get_connection()._authenticator._credentials_provider.username
        """
        warnings.warn("Deprecated. Please use ``la.Info().user_info.name`` instead.",
                      DeprecationWarning)
        if self._authenticator is None:
            raise ValueError(
                "No authenticator set. Please call configure_connection() first.")
        assert isinstance(self._authenticator, CredentialsAuthenticator)
        if self._authenticator._credentials_provider is None:
            raise ValueError(
                "No credentials provider set. Please call configure_connection() first.")
        return self._authenticator._credentials_provider.username
