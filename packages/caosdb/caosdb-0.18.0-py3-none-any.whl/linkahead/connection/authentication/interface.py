# -*- coding: utf-8 -*-
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2018 Research Group Biomedical Physics,
# Max-Planck-Institute for Dynamics and Self-Organization Göttingen
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

"""This module provides the interfaces for authenticating requests to the
LinkAhead server.

Implementing modules must provide a `get_authentication_provider()` method.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import logging
from ..utils import urlencode
from ..interface import CaosDBServerConnection
from ..utils import parse_auth_token, auth_token_to_cookie
from ...exceptions import LoginFailedError
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from ..interface import CaosDBHTTPResponse
    QueryDict = dict[str, Optional[str]]


_LOGGER = logging.getLogger(__name__)


class AbstractAuthenticator(ABC):
    """AbstractAuthenticator.

    Interface for different authentication mechanisms. e.g. username/password
    authentication or SSH key authentication.

    Attributes
    ----------
    logger : Logger
        A logger which should be used for all logging which has to do with
        authentication.
    auth_token : str
        A string representation of a LinkAhead Auth Token.

    Methods
    -------
    login (abstract)
    logout (abstract)
    configure (abstract)
    on_request
    on_response

    """

    def __init__(self):
        self.auth_token = None
        self.logger = _LOGGER

    @abstractmethod
    def login(self):
        """login.

        To be implemented by the child classes.

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def logout(self):
        """logout.

        To be implemented by the child classes.

        Returns
        -------
        None
        """
        pass

    @abstractmethod
    def configure(self, **config):
        """configure.

        Configure this authenticator.

        Parameters
        ----------
        **config
            Keyword arguments for the configuration.

        Returns
        -------
        None
        """
        pass

    def on_response(self, response: CaosDBHTTPResponse):
        """on_response.

        A call-back with is to be called by the connection after each
        response. This method reads the latest auth cookie from the response.

        Parameters
        ----------
        response : CaosDBHTTPResponse
            The response of the server

        Returns
        -------
        """
        new_token = parse_auth_token(response.getheader("Set-Cookie"))
        if new_token is not None:
            self.auth_token = new_token

    def on_request(self, method: str, path: str, headers: QueryDict, **kwargs):
        # pylint: disable=unused-argument
        """on_request.

        A call-back which is to be called by the connection before each
        request. This method set the auth cookie for that request.

        Parameters
        ----------
        method : str
            The request method.
        path : str
            The request path.
        headers : dict
            A dictionary with headers which are to be set.
        **kwargs
            Ignored

        Returns
        -------
        """
        if self.auth_token is None:
            self.login()
        if self.auth_token is not None:
            headers['Cookie'] = auth_token_to_cookie(self.auth_token)


class CredentialsAuthenticator(AbstractAuthenticator):
    """CredentialsAuthenticator.

    Subclass of AbstractAuthenticator which provides authentication via
    credentials (username/password). This class always needs a
    credentials_provider which provides valid credentials_provider before each
    login.

    Parameters
    ----------
    credentials_provider : CredentialsProvider
        The source for the username and the password.

    Methods
    -------
    login
    logout
    configure
    """

    def __init__(self, credentials_provider):
        super(CredentialsAuthenticator, self).__init__()
        self._credentials_provider = credentials_provider
        self._connection = None
        self.auth_token = None

    def login(self):
        self._login()

    def logout(self):
        self._logout()

    def _logout(self):
        self.logger.debug("[LOGOUT]")
        if self.auth_token is not None:
            self._connection.request(method="GET", path="logout")
        self.auth_token = None

    def _login(self):
        username = self._credentials_provider.username
        password = self._credentials_provider.password
        self.logger.debug("[LOGIN] %s", username)

        # we need a username for this:
        if username is None:
            raise LoginFailedError("No username was given.")
        if password is None:
            raise LoginFailedError("No password was given")

        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urlencode({"username": username, "password": password})
        response = self._connection.request(method="POST",
                                            path="login",
                                            headers=headers, body=body)

        response.read()  # clear socket
        if response.status != 200:
            raise LoginFailedError("LOGIN WAS NOT SUCCESSFUL")
        self.on_response(response)
        return response

    def configure(self, **config):
        self._credentials_provider.configure(**config)
        if "connection" in config:
            self._connection = config["connection"]
            if not isinstance(self._connection, CaosDBServerConnection):
                raise Exception("""Bad configuration of the LinkAhead connection.
                                The `connection` must be an instance of
                                `LinkAheadConnection`.""")


class CredentialsProvider(ABC):
    """CredentialsProvider.

    An abstract class for username/password authentication.

    Attributes
    ----------
    password (abstract)
    username (abstract)
    logger : Logger
        A logger which should be used for all logging which has to do with the
        provision of credentials. This is usually just the "authentication"
        logger.

    Methods
    -------
    configure (abstract)
    """

    def __init__(self):
        self.logger = _LOGGER

    @abstractmethod
    def configure(self, **config):
        """configure.

        Configure the credentials provider with a dict.

        Parameters
        ----------
        **config
            Keyword arguments. The relevant arguments depend on the
            implementing subclass of this class.
        Returns
        -------
        None
        """

    @property
    @abstractmethod
    def password(self):
        """password."""

    @property
    @abstractmethod
    def username(self):
        """username."""
