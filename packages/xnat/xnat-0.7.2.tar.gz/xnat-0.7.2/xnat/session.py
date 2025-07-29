# Copyright 2011-2015 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import fnmatch
import hashlib
import io
import netrc
import os
import re
import threading
import zlib
from pathlib import Path
from typing import IO, Any, BinaryIO, Callable, Container, Dict, List, Optional, Tuple, Union
from urllib import parse

import requests
from progressbar import (
    AdaptiveETA,
    AdaptiveTransferSpeed,
    Bar,
    BouncingBar,
    DataSize,
    Percentage,
    ProgressBar,
    Timer,
    UnknownLength,
)

from . import exceptions
from .constants import FIELD_HINTS
from .core import XNATBaseObject, XNATListing, XNATObject, caching
from .exceptions import XNATNotConnectedError, XNATValueError
from .inspect import Inspect
from .map import MappingLevel, MappingObjectStates
from .mixin import Mappable
from .plugins import Plugins
from .prearchive import Prearchive, PrearchiveFile, PrearchiveResource, PrearchiveScan, PrearchiveSession
from .services import Services
from .type_hints import JSONType, TimeoutType
from .users import Users
from .utils import create_filter_funcs


class BaseXNATSession(Mappable):
    """
    The main XNATSession session class. It keeps a connection to XNATSession alive and
    manages the main communication to XNATSession. To keep the connection alive
    there is a background thread that sends a heart-beat to avoid a time-out.

    The main starting points for working with the XNATSession server are:

    * :py:meth:`XNATSession.projects <xnat.session.XNATSession.projects>`
    * :py:meth:`XNATSession.subjects <xnat.session.XNATSession.subjects>`
    * :py:meth:`XNATSession.experiments <xnat.session.XNATSession.experiments>`
    * :py:meth:`XNATSession.plugins <xnat.session.XNATSession.plugins>`
    * :py:meth:`XNATSession.prearchive <xnat.session.XNATSession.prearchive>`
    * :py:meth:`XNATSession.services <xnat.session.XNATSession.services>`
    * :py:meth:`XNATSession.users <xnat.session.XNATSession.users>`

    .. note:: Some methods create listing that are using the :py:class:`xnat.core.XNATListing <xnat.core.XNATListing>`
              class. They allow for indexing with both XNATSession ID and a secondary key (often the
              label). Also they support basic filtering and tabulation.

    There are also methods for more low level communication. The main methods
    are :py:meth:`XNATSession.get <xnat.session.XNATSession.get>`, :py:meth:`XNATSession.post <xnat.session.XNATSession.post>`,
    :py:meth:`XNATSession.put <xnat.session.XNATSession.put>`, and :py:meth:`XNATSession.delete <xnat.session.XNATSession.delete>`.
    The methods do not query URIs but instead query XNATSession REST paths as described in the
    `XNATSession 1.6 REST API Directory <https://wiki.xnat.org/display/XNAT16/XNATSession+REST+API+Directory>`_.

    For an even lower level interfaces, the :py:attr:`XNATSession.interface <xnat.session.XNATSession.interface>`
    gives access to the underlying `requests <https://requests.readthedocs.org>`_ interface.
    This interface has the user credentials and benefits from the keep alive of this class.

    .. note:: :py:class:`XNATSession <xnat.session.XNATSession>` Objects have a client-side cache. This is for efficiency, but might cause
              problems if the server is being changed by a different client. It is possible
              to clear the current cache using :py:meth:`XNATSession.clearcache <xnat.session.XNATSession.clearcache>`.
              Turning off caching complete can be done by setting
              :py:attr:`XNATSession.caching <xnat.session.XNATSession.caching>`.

    .. warning:: You should NOT try use this class directly, it should only
                 be created by :py:func:`xnat.connect <xnat.connect>`.
    """

    def __init__(
        self,
        server,
        logger,
        interface=None,
        user=None,
        password=None,
        keepalive=None,
        debug=False,
        original_uri=None,
        logged_in_user=None,
        default_timeout=300,
        jsession=None,
    ):
        # Class lookup to populate (session specific, as all session have their
        # own classes based on the server xsd)
        self.XNAT_CLASS_LOOKUP = {
            PrearchiveSession.__xsi_type__: PrearchiveSession,
            PrearchiveScan.__xsi_type__: PrearchiveScan,
            PrearchiveResource.__xsi_type__: PrearchiveResource,
            PrearchiveFile.__xsi_type__: PrearchiveFile,
        }

        self.classes = None
        self._interface = interface
        self._projects = None
        self._server = parse.urlparse(server) if server else None
        self._effective_uri = server.rstrip("/")
        if original_uri is not None:
            self._original_uri = original_uri.rstrip("/")
        else:
            self._original_uri = server.rstrip("/")
        self._logged_in_user = logged_in_user
        self._jsession = jsession

        self._cache = {"__objects__": {}}
        self.caching = True
        self._services = Services(xnat_session=self)
        self._plugins = Plugins(xnat_session=self)
        self._prearchive = Prearchive(xnat_session=self)
        self._users = Users(xnat_session=self)
        self._debug = debug
        self._source_code = None
        self._logger = logger
        self.inspect = Inspect(self)
        self.request_timeout = default_timeout

        # Detect mouting for container service/jupyter hub
        self.mount_data_dir = os.environ.get("XNAT_DATA", None)
        self.mount_xsi_type = os.environ.get("XNAT_XSI_TYPE", None)
        self.mount_xnat_item_id = os.environ.get("XNAT_ITEM_ID", None)

        # Accepted status
        self.accepted_status_get = [200]
        self.accepted_status_post = [200, 201]
        self.accepted_status_put = [200, 201]
        self.accepted_status_delete = [200]
        self.skip_response_check = False
        self.skip_response_content_check = False

        session_expiration = self.session_expiration_time
        if session_expiration is not None:
            # 30 seconds before the expiration, at most once per 10 seconds
            if session_expiration[1] < 30:
                self.logger.warning(
                    (
                        "Server session expiration time ({}) is lower than 30 seconds,"
                        " setting heartbeat interval to the minimum of 10 seconds."
                    ).format(session_expiration[1])
                )
            default_keepalive = max(session_expiration[1] // 2 - 20, 10)
        else:
            default_keepalive = 7 * 60  # Default to 14 minutes

        # Set the keep alive settings and spawn the keepalive thread for sending heartbeats
        if keepalive is None or keepalive is True:
            keepalive = default_keepalive

        if isinstance(keepalive, int) and keepalive > 0:
            self._keepalive = True
            self._keepalive_interval = keepalive
        else:
            self._keepalive = bool(keepalive) if keepalive is not None else True  # Keepalive on by default
            self._keepalive_interval = default_keepalive  # Not used while keepalive is false, but set a default

        self._keepalive_running = False
        self._keepalive_thread = None
        self._keepalive_event = threading.Event()

        # If needed connect here
        self.connect(server=server, user=user, password=password)

    def __del__(self):
        self.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self, server=None, user=None, password=None):
        # If not connected, connect now
        if self.interface is None:
            if server is None:
                raise ValueError("Cannot connect if no server is given")
            self.logger.info("Connecting to server {}".format(server))
            if self._interface is not None:
                self.disconnect()

            self._server = parse.urlparse(server)

            if user is None and password is None:
                self.logger.info("Retrieving login info for {}".format(self._server.netloc))
                try:
                    user, _, password = netrc.netrc().authenticators(self._server.netloc)
                except TypeError:
                    raise ValueError('Could not retrieve login info for "{}" from the .netrc file!'.format(server))

            self._interface = requests.Session()
            if (user is not None) or (password is not None):
                self._interface.auth = (user, password)

        # Create a keepalive thread
        self._keepalive_running = True
        self._keepalive_thread = threading.Thread(target=self._keepalive_thread_run, name="XNATpyKeepAliveThread")
        self._keepalive_thread.daemon = True  # Make sure thread stops if program stops
        self._keepalive_thread.start()
        self.heartbeat()  # Make sure the heartbeat is given and there is no chance of timeout

    def disconnect(self):
        # Stop the keepalive thread
        self._keepalive_running = False
        self._keepalive_event.set()

        if self._keepalive_thread is not None:
            if self._keepalive_thread.is_alive():
                self._keepalive_thread.join(3.0)
            self._keepalive_thread = None

        # Set the server and interface to None
        if self._interface is not None:
            self._interface.close()
            self._interface = None
        self._server = None

        self.classes = None

        # Invalidate cache
        self._cache = {"__objects__": {}}
        self.caching = False

    @property
    def keepalive(self) -> bool:
        return self._keepalive

    @keepalive.setter
    def keepalive(self, value: Union[bool, int]):
        if isinstance(value, int):
            if value > 0:
                self._keepalive_interval = value
                value = True
            else:
                value = False

        elif not isinstance(value, bool):
            raise TypeError("Type should be an integer or boolean!")

        self._keepalive = value

        if self.keepalive:
            # Send a new heartbeat and restart the timer to make sure the interval is correct
            self._keepalive_event.set()
            self.heartbeat()

    def heartbeat(self):
        self.get("/data/JSESSION", timeout=10)

    def _keepalive_thread_run(self):
        # This thread runs until the program stops, it should be inexpensive if not used due to the long sleep time
        self.logger.debug("Keep-alive thread started")
        while self._keepalive_running:
            # Wait returns False on timeout and True otherwise
            if not self._keepalive_event.wait(self._keepalive_interval):
                if self.keepalive:
                    self.heartbeat()
            else:
                # Make sure that if the keep alive isn't being killed a heartbeat is sent
                if self._keepalive_running and self.keepalive:
                    self.heartbeat()
                self._keepalive_event.clear()
        else:
            self.logger.debug("Keep-alive thread ended")

    @property
    def logged_in_user(self) -> str:
        return self._logged_in_user

    @property
    def jsession(self) -> str:
        return self._jsession

    @property
    def debug(self) -> bool:
        return self._debug

    @property
    def interface(self) -> requests.Session:
        """
        The underlying `requests <https://requests.readthedocs.org>`_ interface used.
        """
        return self._interface

    @property
    def logger(self):
        return self._logger

    @property
    def uri(self) -> str:
        return "/data/archive"

    @property
    def fulluri(self) -> str:
        return self.uri

    @property
    def xnat_session(self) -> "BaseXNATSession":
        return self

    @property
    def session_expiration_time(self) -> Optional[Tuple[datetime.datetime, float]]:
        """
        Get the session expiration time information from the cookies. This
        returns the timestamp (datetime format) when the session was created
        and an integer with the session timeout interval.

        This can return None if the cookie is not found or cannot be parsed.

        :return: datetime with last session refresh and integer with timeout in seconds
        :rtype: tuple
        """
        expiration_string = self.interface.cookies.get("SESSION_EXPIRATION_TIME")

        if expiration_string is None:
            return

        match = re.match(r'^"(?P<timestamp>\d+),(?P<interval>\d+)"$', expiration_string)
        if match is None:
            self.logger.warning("Could not parse SESSION_EXPIRATION_TIME cookie")
            return None

        session_timestamp = datetime.datetime.fromtimestamp(int(match.group("timestamp")) / 1000)
        expiration_interval = int(match.group("interval")) / 1000
        return session_timestamp, expiration_interval

    def _check_response(
        self, response: requests.Response, accepted_status: Optional[Container[int]] = None, uri: Optional[str] = None
    ):
        if self.debug:
            self.logger.debug(f"Received response with status code: {response.status_code}.")

        if not self.skip_response_check:
            if accepted_status is None:
                accepted_status = [200, 201, 202, 203, 204, 205, 206]  # All successful responses of HTML
            if response.status_code not in accepted_status:
                raise exceptions.XNATResponseError(
                    f"Invalid status for response from XNATSession for url {uri}"
                    f" (status {response.status_code}, accepted status:"
                    f" {accepted_status})",
                    response=response,
                )
            if (not self.skip_response_content_check) and response.text.startswith(("<!DOCTYPE", "<html>")):
                raise exceptions.XNATResponseError(
                    f"Invalid content in response from XNATSession for url {uri}"
                    f" (status {response.status_code}):\n{response.text}",
                    response=response,
                )

    def _check_connection(self):
        """
        Check if connection is still open
        """
        if self.interface is None:
            message = "Not connected to server. Either the connection was not established or was closed!"
            self.logger.error(message)
            raise XNATNotConnectedError(message)

    def get(
        self,
        path: str,
        format: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        accepted_status: Optional[Container[int]] = None,
        timeout: TimeoutType = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Retrieve the content of a given REST directory.

        :param path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                     the remained for the uri is constructed automatically
        :param format: the format of the request, this will add the format= to the query string
        :param query: the values to be added to the query string in the uri
        :param accepted_status: a list of the valid values for the return code, default [200]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :param headers: the HTTP headers to include
        :returns: the requests reponse
        """
        self._check_connection()

        accepted_status = accepted_status or self.accepted_status_get
        uri = self._format_uri(path, format, query=query)
        timeout = timeout or self.request_timeout

        self.logger.info(f"GET URI {uri}")

        try:
            response = self.interface.get(uri, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError(
                "Encountered a problem with the SSL connection, are you sure the server is offering https?"
            )
        self._check_response(response, accepted_status=accepted_status, uri=uri)  # Allow OK, as we want to get data
        return response

    def head(
        self,
        path: str,
        accepted_status: Optional[Container[int]] = None,
        allow_redirects: bool = False,
        timeout: TimeoutType = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Retrieve the header for a http request of a given REST directory.

        :param path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param accepted_status: a list of the valid values for the return code, default [200]
        :param allow_redirects: allow you request to be redirected
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :param headers: the HTTP headers to include
        :returns: the requests reponse
        """
        self._check_connection()

        accepted_status = accepted_status or self.accepted_status_get
        uri = self._format_uri(path)
        timeout = timeout or self.request_timeout

        self.logger.info("HEAD URI {}".format(uri))

        try:
            response = self.interface.head(uri, allow_redirects=allow_redirects, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError(
                "Encountered a problem with the SSL connection, are you sure the server is offering https?"
            )
        self._check_response(response, accepted_status=accepted_status, uri=uri)  # Allow OK, as we want to get data
        return response

    def post(
        self,
        path: str,
        data: Optional[Any] = None,
        json: Optional[JSONType] = None,
        format: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        accepted_status: Optional[Container[int]] = None,
        timeout: TimeoutType = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Post data to a given REST directory.

        :param path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param data: Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: json data to send in the body of the :class:`Request`.
        :param format: the format of the request, this will add the format= to the query string
        :param query: the values to be added to the query string in the uri
        :param accepted_status: a list of the valid values for the return code, default [200, 201]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :param headers: the HTTP headers to include
        :returns: the requests reponse
        """
        self._check_connection()

        accepted_status = accepted_status or self.accepted_status_post
        uri = self._format_uri(path, format, query=query)
        timeout = timeout or self.request_timeout

        self.logger.info("POST URI {}".format(uri))
        if self.debug:
            self.logger.debug("POST DATA {}".format(data))

        try:
            response = self._interface.post(uri, data=data, json=json, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError(
                "Encountered a problem with the SSL connection, are you sure the server is offering https?"
            )
        self._check_response(response, accepted_status=accepted_status, uri=uri)
        return response

    def put(
        self,
        path: str,
        data: Optional[Any] = None,
        files: Optional[Any] = None,
        json: Optional[JSONType] = None,
        format: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        accepted_status: Optional[Container[int]] = None,
        timeout: TimeoutType = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """
        Put the content of a given REST directory.

        :param path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param data: Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: json data to send in the body of the :class:`Request`.
        :param files: Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``) for multipart encoding upload.
                      ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``, 3-tuple ``('filename', fileobj, 'content_type')``
                      or a 4-tuple ``('filename', fileobj, 'content_type', custom_headers)``, where ``'content-type'`` is a string
                      defining the content type of the given file and ``custom_headers`` a dict-like object containing additional headers
                      to add for the file.
        :param format: the format of the request, this will add the format= to the query string
        :param query: the values to be added to the query string in the uri
        :param accepted_status: a list of the valid values for the return code, default [200, 201]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :param dict headers: the HTTP headers to include
        :returns: the requests reponse
        """
        self._check_connection()

        accepted_status = accepted_status or self.accepted_status_put
        uri = self._format_uri(path, format, query=query)
        timeout = timeout or self.request_timeout

        self.logger.info("PUT URI {}".format(uri))
        if self.debug:
            self.logger.debug("PUT DATA {}".format(data))
            self.logger.debug("PUT FILES {}".format(data))

        try:
            response = self._interface.put(uri, data=data, files=files, json=json, timeout=timeout, headers=headers)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError(
                "Encountered a problem with the SSL connection, are you sure the server is offering https?"
            )
        self._check_response(
            response, accepted_status=accepted_status, uri=uri
        )  # Allow created OK or Create status (OK if already exists)
        return response

    def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        accepted_status: Optional[Container[int]] = None,
        query: Optional[Dict[str, str]] = None,
        timeout: TimeoutType = None,
    ) -> requests.Response:
        """
        Delete the content of a given REST directory.

        :param path: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param headers: the HTTP headers to include
        :param query: the values to be added to the query string in the uri
        :param accepted_status: a list of the valid values for the return code, default [200]
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :returns: the requests reponse
        """
        self._check_connection()

        accepted_status = accepted_status or self.accepted_status_delete
        uri = self._format_uri(path, query=query)
        timeout = timeout or self.request_timeout

        self.logger.info("DELETE URI {}".format(uri))
        if self.debug:
            self.logger.debug("DELETE HEADERS {}".format(headers))

        try:
            response = self.interface.delete(uri, headers=headers, timeout=timeout)
        except requests.exceptions.SSLError:
            raise exceptions.XNATSSLError(
                "Encountered a problem with the SSL connection, are you sure the server is offering https?"
            )
        self._check_response(response, accepted_status=accepted_status, uri=uri)
        return response

    def _strip_uri(self, uri: str) -> str:
        if self._effective_uri is not None and uri.startswith(self._effective_uri):
            uri = uri[len(self._effective_uri) :]  # Strip effective uri

        if self._original_uri is not None and uri.startswith(self._original_uri):
            uri = uri[len(self._original_uri) :]  # Strip original uri

        return uri

    def _format_uri(
        self,
        path: str,
        format: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
        scheme: Optional[str] = None,
    ) -> str:
        path = self._strip_uri(path)

        if path[0] != "/":
            raise XNATValueError(
                "The requested URI path should start with a / (e.g. /data/projects), found {}".format(path)
            )

        if query is None:
            query = {}

        if format is not None:
            query["format"] = format

        # Create the query string
        if len(query) > 0:
            query_string = parse.urlencode(query, safe="/", doseq=True)
        else:
            query_string = ""

        data = (
            scheme or self._server.scheme,
            self._server.netloc,
            self._server.path.rstrip("/") + path,
            "",
            query_string,
            "",
        )

        return parse.urlunparse(data)

    def url_for(self, obj: XNATBaseObject, query: Optional[Dict[str, str]] = None, scheme: Optional[str] = None) -> str:
        """
        Return the (external) url for a given XNAT object
        :param obj: object to get url for
        :param query: extra query string parameters
        :param scheme: scheme to use (when not using original url scheme)
        :return: external url for the object
        """
        return self._format_uri(obj.fulluri, query=query, scheme=scheme)

    def get_json(
        self, uri: str, query: Optional[Dict[str, str]] = None, accepted_status: Optional[Container[int]] = None
    ) -> JSONType:
        """
        Helper function that perform a GET, but sets the format to JSON and
        parses the result as JSON

        :param uri: the path of the uri to retrieve (e.g. "/data/archive/projects")
                         the remained for the uri is constructed automatically
        :param query: the values to be added to the query string in the uri
        :param accepted_status: a list of the valid values for the return code, default [200]
        """
        response = self.get(uri, format="json", query=query, accepted_status=accepted_status)
        try:
            return response.json()
        except ValueError:
            # Multiple options to support newer XNAT versions
            if response.text.startswith(
                (
                    '<?xml version="1.0" encoding="UTF-8"?>\n<cat:Catalog',
                    '<?xml version="1.0" encoding="UTF-8"?>\n<cat:DCMCatalog',  # XNAT 1.7.5.3+
                )
            ):
                # Probably XML catalog for resource
                parts = uri.rsplit("/resources/")
                if len(parts) != 2:
                    raise XNATValueError(
                        "Could not decode JSON from [{}] and could not figure out resource URI".format(uri)
                    )

                uri = parts[0] + "/resources"
                # Make sure everything after additional / or ? in uri are ignored
                id = parts[1].split("/")[0].split("?")[0]

                # Unpack result and find correct entry
                data = self.get_json(uri)
                data = data["ResultSet"]["Result"]
                try:
                    data = next(
                        x for x in data if x.get("xnat_abstractresource_id", None) == id or x.get("label", None) == id
                    )
                except StopIteration:
                    raise XNATValueError(
                        "Could not find data for resource with abstract resource id or label matching {}".format(id)
                    )

                # Pack data properly for xnat response
                data = {
                    "items": [
                        {
                            "children": [],
                            "meta": {"xsi:type": "xnat:resourceCatalog", "isHistory": False},
                            "data_fields": data,
                        }
                    ]
                }

                return data
            else:
                raise XNATValueError("Could not decode JSON from [{}] {}".format(uri, response.text))

    def download_stream(
        self,
        uri: str,
        target_stream: BinaryIO,
        format: Optional[str] = None,
        verbose: bool = False,
        chunk_size: int = 524288,
        update_func: Optional[Callable[[int, Optional[int], bool], None]] = None,
        timeout: TimeoutType = None,
        expected_md5_digest: str = None,
    ):
        """
        Download the given ``uri`` to the given ``target_stream``.

        :param uri:           Path of the uri to retrieve.
        :param target_stream: A writable file-like object to save the
                              stream to.
        :param format:         Request format
        :param verbose:       If ``True``, and an ``update_func`` is not
                              specified, a progress bar is shown on
                              stdout.
        :param chunk_size:     Download this many bytes at a time
        :param update_func:   If provided, will be called every
                              ``chunk_size`` bytes. Must accept three
                              parameters:

                                - the number of bytes downloaded so far
                                - the total number of bytes to be
                                  downloaded (might be ``None``),
                                - A boolean flag which is ``False`` during
                                  the download, and ``True`` when the
                                  download has completed (or failed)
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        """
        self._check_connection()

        uri = self._format_uri(uri, format=format)
        self.logger.info("DOWNLOAD STREAM {}".format(uri))

        # Stream the get and write to file
        response = self.interface.get(uri, stream=True, timeout=timeout)

        if response.status_code not in self.accepted_status_get:
            raise exceptions.XNATResponseError(
                f"Invalid response from XNATSession for url {uri} (status {response.status_code}):\n{response.text}",
                response=response,
            )

        # Get the content length if available
        content_length = response.headers.get("Content-Length", None)

        if isinstance(content_length, str):
            content_length = int(content_length)

        if verbose and update_func is None:
            update_func = default_update_func(content_length)
        elif update_func is None:
            update_func = lambda *args: None

        if verbose:
            self.logger.info("Downloading {}:".format(uri))

        bytes_read = 0
        md5_hasher = hashlib.md5()

        try:
            update_func(0, content_length, False)
            for chunk in response.iter_content(chunk_size):
                if bytes_read == 0 and chunk[0] == "<" and chunk.startswith(("<!DOCTYPE", "<html>")):
                    raise ValueError(
                        "Invalid response from XNATSession (status {}):\n{}".format(response.status_code, chunk)
                    )

                bytes_read += len(chunk)
                target_stream.write(chunk)
                if expected_md5_digest:
                    md5_hasher.update(chunk)

                update_func(bytes_read, content_length, False)
        finally:
            update_func(bytes_read, content_length, True)

        if expected_md5_digest:
            data_digest = md5_hasher.hexdigest()
            if data_digest != expected_md5_digest:
                raise exceptions.XNATValueError(
                    f"The downloaded md5 digest ({data_digest}) does not match the "
                    f"expected md5 digest ({expected_md5_digest})"
                )
            else:
                self.logger.info(f"The md5 digests match ({data_digest})")

    def download(
        self,
        uri: str,
        target: Union[str, Path],
        format: Optional[str] = None,
        verbose: bool = True,
        timeout: TimeoutType = None,
        expected_md5_digest: str = None,
    ):
        """
        Download uri to a target file
        """
        self._check_connection()

        with open(target, "wb") as out_fh:
            self.download_stream(
                uri, out_fh, format=format, verbose=verbose, timeout=timeout, expected_md5_digest=expected_md5_digest
            )

        if verbose:
            self.logger.info("Saved as {}...".format(target))

    def download_zip(self, uri: str, target: Union[str, Path], verbose: bool = True, timeout: TimeoutType = None):
        """
        Download uri to a target zip file
        """
        self.download(uri, target, format="zip", verbose=verbose, timeout=timeout)

    def upload_file(self, uri: str, path: Union[str, Path], **kwargs):
        """
        Upload a file to XNAT

        :param str uri: uri to upload to
        :param str path: path to the file to be uploaded (str)
        :param int retries: amount of times xnatpy should retry in case of
                            failure
        :param dict query: extra query string content
        :param content_type: the content type of the file, if not given it will
                             default to ``application/octet-stream``
        :param str method: either ``put`` (default) or ``post``
        :param bool overwrite: indicate if previous data should be overwritten
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        :type timeout: float or tuple
        :return:
        """

        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError("The file you are trying to upload does not exist.")

        if not path.is_file():
            raise FileNotFoundError("The path points to a non-file object")

        with open(path, "rb") as file_handle:
            return self.upload_stream(uri=uri, stream=file_handle, **kwargs)

    def upload_string(self, uri: str, data: Union[str, bytes], **kwargs):
        """
        Upload path from a string to XNAT

        :param uri: uri to upload to
        :param data: the string to upload (has to be of type str), this string will
                     become the content of the target.
        :param retries: amount of times xnatpy should retry in case of
                        failure
        :param query: extra query string content
        :param content_type: the content type of the file, if not given it will
                             default to ``application/octet-stream``
        :param method: either ``put`` (default) or ``post``
        :param overwrite: indicate if previous path should be overwritten
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        """
        if not isinstance(data, (str, bytes)):
            raise TypeError(f"The upload_string needs a string as the path to upload, found {type(data)}!")

        if isinstance(data, str):
            data_stream = io.StringIO(data)
        else:
            data_stream = io.BytesIO(data)

        return self.upload_stream(uri=uri, stream=data_stream, **kwargs)

    def upload(self, uri: str, file_: Union[str, bytes, Path, IO], **kwargs):
        """
        Upload path to XNAT, this method attempt to automatically figure out what
        the type of the source path is.

        .. warning::

            DEPRECATED: This method can have unexpected behaviour (e.g. if you supply a str with
            a path but the file does not exist, it will upload the path as a string
            instead). This method will be removed in a future release of XNATpy

        :param uri: uri to upload to
        :param file_: the data to upload
        :param retries: amount of times xnatpy should retry in case of
                        failure
        :param query: extra query string content
        :param content_type: the content type of the file, if not given it will
                             default to ``application/octet-stream``
        :param method: either ``put`` (default) or ``post``
        :param overwrite: indicate if previous path should be overwritten
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        """
        self.logger.warning(
            "The upload method attempts to autodetect the type of the path, this can lead to "
            "unexpected behaviour. It is advised to use upload_stream , upload_file, or "
            "upload_string instead. The upload method might be removed in a future release."
        )
        # Check if file is an opened file
        if isinstance(file_, (io.BufferedIOBase, io.TextIOBase)):
            self.logger.info("Auto-selected upload_stream to handle the upload")
            return self.upload_stream(uri=uri, stream=file_, **kwargs)
        elif isinstance(file_, Path) or (isinstance(file_, str) and "\0" not in file_ and os.path.isfile(file_)):
            self.logger.info("Auto-selected upload_file to handle the upload")
            return self.upload_file(uri=uri, path=file_, **kwargs)
        elif isinstance(file_, (str, bytes)):
            # File is path to upload
            self.logger.info("Auto-selected upload_string to handle the upload")
            return self.upload_string(uri=uri, data=file_, **kwargs)
        else:
            raise XNATValueError(f"Cannot find correct method to upload data of type {type(file_)}")

    def upload_stream(
        self,
        uri: str,
        stream: Union[IO, io.BufferedIOBase, io.TextIOBase],
        retries: int = 1,
        query: Optional[Dict[str, str]] = None,
        content_type: Optional[str] = None,
        method: str = "put",
        overwrite: bool = False,
        timeout: TimeoutType = None,
    ):
        """
        Upload path from a stream to XNAT

        :param uri: uri to upload to
        :param stream: the file handle, path to a file or a string of path
                      (which should not be the path to an existing file!)
        :param retries: amount of times xnatpy should retry in case of
                        failure
        :param query: extra query string content
        :param content_type: the content type of the file, if not given it will
                             default to ``application/octet-stream``
        :param method: either ``put`` (default) or ``post``
        :param overwrite: indicate if previous data should be overwritten
        :param timeout: timeout in seconds, float or (connection timeout, read timeout)
        """
        self._check_connection()

        if overwrite:
            if query is None:
                query = {}
            query["overwrite"] = "true"

        uri = self._format_uri(uri, query=query)
        self.logger.info("UPLOAD URI {}".format(uri))
        attempt = 0
        response = None

        # Set the content type header
        if content_type is None:
            headers = {"Content-Type": "application/octet-stream"}
        else:
            headers = {"Content-Type": content_type}

        while attempt < retries:
            stream.seek(0)
            attempt += 1

            if method == "put":
                response = self.interface.put(uri, data=stream, headers=headers, timeout=timeout)
            elif method == "post":
                response = self.interface.post(uri, data=stream, headers=headers, timeout=timeout)
            else:
                raise ValueError('Invalid upload method "{}" should be either put or post.'.format(method))

            try:
                self._check_response(response)
                return response
            except exceptions.XNATResponseError:
                pass

        # We didn't return correctly, so we have an error
        raise exceptions.XNATUploadError(
            f"Upload failed after {retries} attempts! Status code"
            f" {response.status_code}, response text {response.text}"
        )

    @property
    @caching
    def access_levels(self):
        """
        Shows the access levels for the currently logged in user for all the projects you have any access to
        """
        # The xapi route was introduced at 1.8.0
        if self.xnat_version_tuple < (1, 8, 0):
            data = {}
        else:
            data = self.get_json("/xapi/access/projects")
        return {x["ID"]: x["role"] for x in data if "ID" in x and "role" in x}

    @property
    @caching
    def scanners(self) -> List:
        """
        A list of scanners referenced in XNATSession
        """
        return [x["scanner"] for x in self.xnat_session.get_json("/data/archive/scanners")["ResultSet"]["Result"]]

    @property
    @caching
    def scan_types(self):
        """
        A list of scan types associated with this XNATSession instance
        """
        return self.xnat_session.get_json("/data/archive/scan_types")["ResultSet"]["Result"]

    @property
    def source_code(self):
        if self._source_code is not None:
            return zlib.decompress(self._source_code).decode("utf-8")

        return None

    @source_code.setter
    def source_code(self, value: str):
        self._source_code = zlib.compress(value.encode("utf-8"))

    def write_source_code(self, path: Union[str, Path]):
        if self._source_code is None:
            self.logger.warning("There is not source code created for this connection (model has not been built).")
            return

        with open(path, "w") as fh_out:
            fh_out.write(self.source_code)

    @property
    @caching
    def xnat_version(self) -> str:
        """
        The version of the XNAT server
        """
        try:
            # XNAT SERVER 1.6.x
            return self.get("/data/version").text
        except exceptions.XNATResponseError:
            # XNAT SERVER 1.7.x
            return self.get_json("/xapi/siteConfig/buildInfo")["version"]

    @property
    @caching
    def xnat_version_tuple(self) -> Tuple[int]:
        return tuple(int(x) for x in self.xnat_version.split(".") if x.isdigit())

    @property
    def xnat_uptime(self):
        """
        The uptime of the XNAT server
        """
        try:
            # XNAT SERVER 1.6.x
            return self.get("/data/uptime").text
        except exceptions.XNATResponseError:
            # XNAT SERVER 1.7.x
            return self.get_json("/xapi/siteConfig/uptime")

    @property
    @caching
    def xnat_build_info(self):
        """
        The build info of the XNAT server
        """
        try:
            # XNAT SERVER 1.6.x
            return self.get("/data/buildInfo").text
        except exceptions.XNATResponseError:
            # XNAT SERVER 1.7.x
            return self.get_json("/xapi/siteConfig/buildInfo")

    def create_object(
        self,
        uri: str,
        type_: Optional[str] = None,
        fieldname: Optional[str] = None,
        datafields: Optional[Dict[str, JSONType]] = None,
        **kwargs,
    ) -> XNATBaseObject:
        """
        Create an xnatpy object for a given uri. This does **not** create anything server sided, but rather
        wraps and uri (and optionally data) in an object. It allows you to create an xnatpy object from an
        arbitrary uri to something on the xnat server and continue as normal from there on.

        :param uri: url of the object
        :param type_: the xsi_type to select the object type (this is option, by default it will be auto retrieved)
        :param fieldname: indicate the name of the field that was used to retrieved this object
        :param datafields: initial data to use for the object
        :param kwargs: arguments to pass to object creation
        :return: newly created xnatpy object
        """
        # Normalise url here so in the cache lookup it is consistent
        uri = self._strip_uri(uri)
        if uri.startswith("/REST/"):
            uri = uri.replace("/REST/", "/data/")
        elif uri.startswith("/data/archive/"):
            uri = uri.replace("/data/archive/", "/data/")

        # Check if we have prearchive uris
        if uri.startswith("/data/prearchive"):
            if re.match(r"/data/prearchive/projects/[^/]+/[\d_]+/[^/]+/scans/[^/]+/resources/[^/]+/files/.*", uri):
                type_ = "xnatpy:prearchiveFile"
            elif re.match(r"/data/prearchive/projects/[^/]+/[\d_]+/[^/]+/scans/[^/]+/resources/[^/]+", uri):
                type_ = "xnatpy:prearchiveResource"
            elif re.match(r"/data/prearchive/projects/[^/]+/[\d_]+/[^/]+/scans/[^/]+", uri):
                type_ = "xnatpy:prearchiveScan"
            elif re.match(r"/data/prearchive/projects/[^/]+/[\d_]+/[^/]+", uri):
                type_ = "xnatpy:prearchiveSession"

        # If the object is not in cache, check type and try to see if fieldname needs updating
        if datafields is None:
            datafields = {}

        if type_ is None:
            if self.xnat_session.debug:
                self.logger.debug("Type unknown, fetching data to get type")
            fulldata = next(x for x in self.xnat_session.get_json(uri)["items"] if not x["meta"]["isHistory"])
            type_ = fulldata["meta"]["xsi:type"]
            datafields = fulldata["data_fields"]

            # If ID is known from the query but not yet in kwargs, insert it
            # Add in the ID for projects/subjects/experiments
            if "id_" not in kwargs and "ID" in datafields:
                kwargs["id_"] = datafields["ID"]

            # Add in ID for resources
            if "id_" not in kwargs and "xnat_abstractresource_id" in datafields:
                kwargs["id_"] = datafields["xnat_abstractresource_id"]

        # If no fieldname is giving, try to extract it from FIELD_HINTS
        if fieldname is None:
            fieldname = FIELD_HINTS.get(type_, None)

        # Check the type class, so we can use it
        if self.xnat_session.debug:
            self.logger.debug(f"Looking up type {type_} [{type(type_).__name__}]")
        if type_ not in self.XNAT_CLASS_LOOKUP:
            raise KeyError(
                f"Type {type_} unknow to this XNATSession REST client (see XNAT_CLASS_LOOKUP class variable)"
            )

        cls = self.XNAT_CLASS_LOOKUP[type_]

        # If object no in cache, create the object and add it to the cache
        self.logger.debug(f"Creating cache id for cls={cls} uri={uri} fieldname={fieldname} kwargs={kwargs}")
        cache_id = cls.create_cache_id(uri, fieldname, kwargs)
        if self.debug:
            self.logger.debug(f"Testing if {cache_id} is in cache")

        if cache_id not in self._cache["__objects__"]:
            if self.xnat_session.debug:
                self.logger.debug(f"Creating object of type {cls}")

            # Add project post-hoc hook for fixing some problems with shared
            # resources, the .+? is the non greedy version of .+
            match = re.search("/data(?:/archive)?/projects/(.+?)/", uri)

            if match:
                # Set overwrite field
                overwrites = {"project": match.group(1)}
            else:
                overwrites = None

            # If the secondary lookup wasn't given in kwargs but is in the extracted datafields, use that instead
            if cls.SECONDARY_LOOKUP_FIELD not in kwargs and cls.SECONDARY_LOOKUP_FIELD in datafields:
                kwargs[cls.SECONDARY_LOOKUP_FIELD] = datafields[cls.SECONDARY_LOOKUP_FIELD]

            # Call object constructor based on collected desired class and arguments
            obj: XNATBaseObject = cls(
                uri, self, datafields=datafields, fieldname=fieldname, overwrites=overwrites, **kwargs
            )

            if self.debug:
                self.logger.debug(f"Storing object [{type(obj)}] {obj} into cache under {cache_id}")

            # Also save under the fulluri in the cache (for e.g. experiments those can differ)
            self._cache["__objects__"][cache_id] = obj
        elif self.debug:
            self.logger.debug(f"Fetching object {cache_id} from cache")

        # Return the object from cache
        return self._cache["__objects__"][cache_id]

    def remove_object(self, obj: XNATBaseObject):
        # Remove object from cache (so re-creation won't use cache object)
        XNATListing.delete_item_from_listings(obj)
        del self._cache["__objects__"][obj.cache_id]

    @property
    @caching
    def projects(self) -> XNATListing:
        """
        Listing of all projects on the XNAT server

        Returns an :py:class:`XNATListing <xnat.core.XNATListing>` with elements
        of :py:class:`ProjectData <xnat.classes.ProjectData>`
        """
        return XNATListing(
            self.uri + "/projects",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="projects",
            xsi_type="xnat:projectData",
            secondary_lookup_field="name",
        )

    @property
    @caching
    def subjects(self) -> XNATListing:
        """
        Listing of all subjects on the XNAT server

        Returns an :py:class:`XNATListing <xnat.core.XNATListing>` with elements
        of :py:class:`SubjectData <xnat.classes.SubjectData>`
        """
        return XNATListing(
            self.uri + "/subjects",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="subjects",
            xsi_type="xnat:subjectData",
            secondary_lookup_field="label",
        )

    @property
    @caching
    def experiments(self) -> XNATListing:
        """
        Listing of all experiments on the XNAT server

        Returns an :py:class:`XNATListing <xnat.core.XNATListing>` with elements
        that are subclasses of :py:class:`ExperimentData <xnat.classes.ExperimentData>`
        """
        return XNATListing(
            self.uri + "/experiments",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="experiments",
            secondary_lookup_field="label",
        )

    @property
    def prearchive(self) -> Prearchive:
        """
        Representation of the prearchive on the XNAT server, see :py:mod:`xnat.prearchive`
        """
        return self._prearchive

    @property
    def users(self) -> Users:
        """
        Representation of the users registered on the XNAT server
        """
        return self._users

    @property
    def services(self) -> Services:
        """
        Collection of services, see :py:mod:`xnat.services`
        """
        return self._services

    @property
    def plugins(self):
        """
        Collection of plugins, see :py:mod:`xnat.plugins`
        """
        return self._plugins

    def mapping_iter(self, states: MappingObjectStates, level: MappingLevel, filter_function):
        self.logger.debug(f"Start Iterating for {self}")
        with states.descend(self, MappingLevel.CONNECTION):
            for xnat_project in self.projects.values():
                if states.succeeded(xnat_project):
                    continue
                if filter_function and not filter_function.project(xnat_project):
                    continue
                if level == MappingLevel.PROJECT:
                    yield xnat_project
                else:
                    yield from xnat_project.mapping_iter(states, level, filter_function)
        self.logger.debug(f"Finished Iterating for {self}")

    def search(
        self,
        project: Optional[str] = None,
        subject: Optional[str] = None,
        experiment: Optional[str] = None,
        scan: Optional[str] = None,
        resource: Optional[str] = None,
        use_regex: bool = False,
        level: MappingLevel = MappingLevel.SCAN,
    ):
        """
        Search for objects matching a set of filters. The
        filters are by default applied using fnmatch can
        using the ``use_regex`` flag this will be
        changed to regular expression matching.

        The level to search on is controlled by the
         enum :py:class:`MappingLevel <xnat.map.MappingLevel>`,

        :param project: filter for project names
        :param subject: filter for subject labels
        :param experiment: filter for experiment labels
        :param scan: filter for scan types
        :param resource: filter for resource labels
        :param use_regex: flag to indicate using regular expression matching
        :param level: level of the objects to download
        """
        filters = create_filter_funcs(
            project=project, subject=subject, experiment=experiment, scan=scan, resource=resource, use_regex=use_regex
        )

        result = self.map(lambda x: x, level=level, filter_function=filters)

        return list(result.values())

    def batch_download(
        self,
        target_directory: Union[str, Path],
        project: Optional[str] = None,
        subject: Optional[str] = None,
        experiment: Optional[str] = None,
        scan: Optional[str] = None,
        resource: Optional[str] = None,
        use_regex: bool = False,
        level: MappingLevel = MappingLevel.SCAN,
    ) -> None:
        """
        Download a batch of data in one go. Will download all data matching a set of filters. The
        filters are by default applied using fnmatch can using the ``use_regex`` flag this will be
        changed to regular expression matching.

        The level to search on is controlled by the enum :py:class:`MappingLevel <xnat.map.MappingLevel>`,

        :param target_directory: Target directory to download in
        :param project: filter for project names
        :param subject: filter for subject labels
        :param experiment: filter for experiment labels
        :param scan: filter for scan types
        :param resource: filter for resource labels
        :param use_regex: flag to indicate using regular expression matching
        :param level: level of the objects to download
        """

        # Define the download function to map
        def download_item(item: XNATObject) -> None:
            self.logger.warning(f"Found match: {item}, downloading...")
            item.download_dir(target_directory)

        filters = create_filter_funcs(
            project=project, subject=subject, experiment=experiment, scan=scan, resource=resource, use_regex=use_regex
        )

        self.map(download_item, level=level, filter_function=filters)

    def clearcache(self):
        """
        Clear the cache of the listings in the Session object
        """
        self._cache.clear()
        self._cache["__objects__"] = {}


def default_update_func(total) -> Callable[[str, str, bool], None]:
    """
    Set up a default update function to be used by the
    :class:`Session.download_stream` method. This function configures a
    ``progressbar.ProgressBar`` object which displays progress as a file
    is downloaded.

    :param int total: Total number of bytes to be downloaded (might be
                      ``None``)

    :returns: A function to be used as the ``update_func`` by the
              ``Session.download_stream`` method.
    """

    if total is not None:
        widgets = [
            Percentage(),
            " of ",
            DataSize("max_value"),
            " ",
            Bar(),
            " ",
            AdaptiveTransferSpeed(),
            " ",
            AdaptiveETA(),
        ]
    else:
        total = UnknownLength
        widgets = [
            DataSize(),
            " ",
            BouncingBar(),
            " ",
            AdaptiveTransferSpeed(),
        ]

    progress_bar = ProgressBar(widgets=widgets, max_value=total)

    # The real update function which gets called by download_stream
    def do_update(nbytes, total, finished, progress_bar=progress_bar):

        if nbytes == 0:
            progress_bar.start()
        elif finished:
            progress_bar.finish()
        else:
            progress_bar.update(nbytes)

    return do_update


class XNATSession(BaseXNATSession):
    def disconnect(self):
        # Kill the session
        if self._server is not None and self._interface is not None:
            self.delete("/data/JSESSION", headers={"Connection": "close"})

        # Call
        super(XNATSession, self).disconnect()
