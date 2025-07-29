# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
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

"""
This package contains the entire client. The connect function is the only
function actually in the package. All following classes are created based on
the https://central.xnat.org/schema/xnat/xnat.xsd schema and the xnatcore and
xnatbase modules, using the convert_xsd.
"""

import getpass
import hashlib
import importlib.abc
import importlib.machinery
import importlib.util
import logging
import netrc
import os
import platform
import re
import time
from io import StringIO
from pathlib import Path
from urllib import parse

import requests
import requests.cookies
import urllib3

from . import exceptions, search, version
from .constants import DEFAULT_SCHEMAS
from .convert_xsd import SchemaParser
from .map import MappingLevel
from .mixin import FilterFunctions, MappedFunctionFailed
from .session import BaseXNATSession, XNATSession
from .utils import JSessionAuth

GEN_MODULES = {}

__version__ = version.version
__all__ = ["connect", "exceptions", "MappingLevel", "FilterFunctions", "MappedFunctionFailed"]


class StringLoader(importlib.abc.SourceLoader):
    def __init__(self, data):
        self.data = data

    def get_data(self, pathname):
        return self.data.encode("utf-8")

    def get_filename(self, fullname: str) -> str:
        return f"<in_memory:{fullname}>"


def check_auth_guest(requests_session, server, logger):
    """
    Try to figure out of the requests session is properly logged in as the desired user

    :param requests.Session requests_session: requests session
    :param str server: server test
    :param logger: logger to use
    :raises ValueError: Raises a ValueError if the login failed
    """
    logger.debug("Getting {} to test guest auth".format(server))
    test_auth_request = requests_session.get(server, timeout=10)
    logger.debug("Status: {}".format(test_auth_request.status_code))

    match = re.search(
        r'<span id="user_info">Logged in as: <span style="color:red;">Guest</span>', test_auth_request.text
    )

    if match is not None:
        logger.info("Logged in as guest successfully")
        return "guest"

    match = re.search(
        r'<span id="user_info">Logged in as: &nbsp;<a (id="[^"]+" )?href="[^"]+">(?P<username>[^<]+)</a>',
        test_auth_request.text,
    )

    if match is None:
        message = "Could not determine if login was successful!"
        logger.error(message)
        raise exceptions.XNATAuthError(message)

    username = match.group("username")
    logger.warning('Detected (somewhat unexpected) login as "{username}" (expected "guest")'.format(username=username))

    return username


def check_auth(requests_session, server, user, jsession, logger):
    """
    Try to figure out of the requests session is properly logged in as the desired user

    :param requests.Session requests_session: requests session
    :param str server: server test
    :param str user: desired user (None for no specific check)
    :raises ValueError: Raises a ValueError if the login failed
    """
    test_uri = server.rstrip("/") + "/data/auth"
    logger.debug("Getting {} to test auth (user {})".format(test_uri, user))

    test_auth_request = requests_session.get(test_uri, timeout=10)
    logger.debug("Status: {}".format(test_auth_request.status_code))

    if test_auth_request.status_code == 401 or "Login attempt failed. Please try again." in test_auth_request.text:
        message = "Login attempt failed for {}, please make sure your credentials for user {} are correct!".format(
            server, user
        )
        logger.critical(message)
        raise exceptions.XNATLoginFailedError(message)

    if test_auth_request.status_code != 200:
        logger.warning("Simple test requests did not return a 200 or 401 code! Server might not be functional!")

    match = re.search(r"User '(?P<username>[^<]+)' is logged in", test_auth_request.text)

    if match is None:
        match = re.search(
            r'<span id="user_info">Logged in as: &nbsp;<a (id="[^"]+" )?href="[^"]+">(?P<username>[^<]+)</a>',
            test_auth_request.text,
        )

    if match is None:
        match = re.search(
            r'<span id="user_info">Logged in as: <span style="color:red;">Guest</span>', test_auth_request.text
        )
        if match is None:
            match = re.search("Your password has expired", test_auth_request.text)
            if match:
                message = "Your password has expired. Please try again after updating your password on XNAT."
                logger.error(message)
                raise exceptions.XNATExpiredCredentialsError(message)

            match = re.search(r'<form name="form1" method="post" action="/xnat/login"', test_auth_request.text)
            if match:
                message = (
                    "Login attempt failed for {}, please make sure your credentials for user {} are correct!".format(
                        server, user
                    )
                )
                logger.error(message)
                raise exceptions.XNATLoginFailedError(message)

            message = "Could not determine if login was successful!"
            logger.critical(message)
            logger.debug(test_auth_request.text)
            raise exceptions.XNATAuthError(message)
        else:
            message = "Login failed (in guest mode)!"
            logger.error(message)
            raise exceptions.XNATLoginFailedError(message)
    else:
        username = match.group("username")
        if username == user:
            logger.info("Logged in successfully as {}".format(username))
        # changed check_auth to take jsession, so user=None doesn't cause a type error, and re.match here compares against a different pattern specific to jsession
        elif user is not None:
            if re.match(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}", user):
                logger.info("Token login successfully as {}".format(username))
            else:
                logger.warning("Logged in as {} but expected to be logged in as {}".format(username, user))
        elif jsession is not None:
            if re.match(r"[\w]{32}", jsession):
                logger.info("JSESSION login successful for {}".format(username))

        return username


def parse_schemas_16(parser, xnat_session, extension_types=True):
    """
    Retrieve and parse schemas for an XNAT version 1.6.x

    :param parser: The parser to use for the parsing
    :param xnat_session: the requests session used for the communication
    :param bool extension_types: flag to enabled/disable scanning for extension types
    """
    # Retrieve schema from XNAT server
    schema_uri = "/schemas/xnat/xnat.xsd"

    success = parser.parse_schema_uri(xnat_session=xnat_session, schema_uri=schema_uri)

    if not success:
        raise RuntimeError("Could not parse the xnat.xsd! See error log for details!")

    # Parse extension types
    if extension_types:
        projects_uri = "/data/projects?format=json"
        try:
            response = xnat_session.get(projects_uri)
        except exceptions.XNATResponseError as exception:
            message = "Could list projects while scanning for extension types: {}".format(exception)
            xnat_session.logger.critical(message)
            raise exception

        try:
            project_id = response.json()["ResultSet"]["Result"][0]["ID"]
        except (KeyError, IndexError):
            raise ValueError("Could not find an example project for scanning extension types!")

        project_uri = "/data/projects/{}".format(project_id)
        try:
            response = xnat_session.get(project_uri, format="xml")
        except exceptions.XNATResponseError as exception:
            message = "Could load example project while scanning for extension types: {}".format(exception)
            xnat_session.logger.critical(message)
            raise exception

        schemas = parser.find_schema_uris(response.text)
        if schema_uri in schemas:
            xnat_session.logger.debug("Removing schema {} from list".format(schema_uri))
            schemas.remove(schema_uri)
        xnat_session.logger.info("Found additional schemas: {}".format(schemas))

        for schema in schemas:
            parser.parse_schema_uri(xnat_session=xnat_session, schema_uri=schema)


def parse_schemas_17(parser, xnat_session, extension_types=True):
    """
    Retrieve and parse schemas for an XNAT version 1.7.x

    :param parser: The parser to use for the parsing
    :param xnat_session: the requests session used for the communication
    :param bool extension_types: flag to enabled/disable scanning for extension types
    """
    if extension_types:
        schemas_uri = "/xapi/schemas"
        try:
            schema_list = xnat_session.get_json(schemas_uri)
        except exceptions.XNATResponseError as exception:
            message = "Problem retrieving schemas list: {}".format(exception)
            xnat_session.logger.critical(message)
            raise ValueError(message)
    else:
        schema_list = DEFAULT_SCHEMAS

    for schema in schema_list:
        if extension_types or schema in ["xdat", "xnat"]:
            parser.parse_schema_uri(
                xnat_session=xnat_session, schema_uri="/xapi/schemas/{schema}".format(schema=schema)
            )


def detect_redirection(response, server, logger):
    """
    Check if there is a redirect going on
    :param response: requests response to extract the redirection from
    :param str server: server url
    :param logger:
    :return: the server url to use later
    """
    logger.debug("Response url: {}".format(response.url))
    response_match = re.match(r"(.*/)(app|data)/", response.url)

    if response_match is not None:
        response_url = response_match.group(1)
    else:
        response_url = response.url

    if response_url != server and response_url != server + "/":
        logger.warning("Detected a redirect from {0} to {1}, using {1} from now on".format(server, response_url))
    return response_url


def query_netrc(server, netrc_file, logger):
    # Get the login info
    parsed_server = parse.urlparse(server)

    logger.info("Retrieving login info for {}".format(parsed_server.netloc))
    try:
        # First query the NETRC envirnonment variable
        if netrc_file is None:
            netrc_file = os.environ.get("NETRC", None)

        # Otherwise pick a default
        if netrc_file is None:
            if os.name == "nt":
                netrc_file = Path.home() / "_netrc"
            else:
                netrc_file = Path.home() / ".netrc"

        logger.info(f"Querying netrc file: {netrc_file}")
        user, _, password = netrc.netrc(netrc_file).authenticators(parsed_server.netloc)
        logger.info("Found login for {}".format(parsed_server.netloc))
    except (TypeError, IOError):
        logger.info("Could not find login for {}, continuing without login".format(parsed_server.netloc))
        user = password = None

    return user, password


def _create_jsession(requests_session, server, user, password, provider, debug, logger):
    # Check if a token login is used, and  use basic auth to set the login if so

    data = {
        "username": user,
        "password": password,
    }

    if provider:
        data["provider"] = provider

    if re.match(r"[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}", user):
        if debug:
            logger.debug("Suspected username {user} to be an alias token.".format(user=user))
            logger.debug("GET URI {} with basic auth".format(server.rstrip("/")))
        response = requests_session.get(server.rstrip("/"), timeout=10, auth=(user, password))
        return response.cookies.get("JSESSIONID", None)
    else:
        try:
            uri = server.rstrip("/") + "/data/services/auth"

            if debug:
                logger.debug("PUT URI {}".format(uri))
                data_to_print = dict(data)
                del data_to_print["password"]
                logger.debug("PUT DATA {}".format(data_to_print))

            response = requests_session.put(uri, data=data, timeout=10)

            # Try to give a clean error in case of login problems
            if response.status_code != 200:
                match = re.search("<h3>(.*)</h3>", response.text)
                if match:
                    message = match.group(1)
                elif debug:
                    message = response.text
                else:
                    message = "unknown error"
                raise exceptions.XNATLoginFailedError("Encountered a problem logging in: {}".format(message))

            return response.text
        except (requests.ConnectionError, requests.ReadTimeout) as exception:
            exception_type = type(exception).__name__
            # Do no raise here by default, it will make the error trace huge and scare of new users
            if debug:
                raise exceptions.XNATConnectionError(
                    "Could not connect to {}, encountered {} exception".format(server, exception_type)
                )

        raise exceptions.XNATConnectionError("Could not connect to {} (encountered {})".format(server, exception_type))


def _query_jsession(requests_session, server, debug, logger):
    try:
        uri = server.rstrip("/") + "/data/JSESSION"
        if debug:
            logger.debug("GET URI {uri}".format(uri=uri))
        return requests_session.get(uri, timeout=10).text
    except (requests.ConnectionError, requests.ReadTimeout) as exception:
        exception_type = type(exception).__name__
        # Do no raise here by default, it will make the error trace huge and scare of new users
        if debug:
            raise exceptions.XNATConnectionError(
                "Could not connect to {}, encountered {} exception".format(server, exception_type)
            )

    raise exceptions.XNATConnectionError("Could not connect to {} (encountered {})".format(server, exception_type))


def _wipe_jsession(requests_session, server):
    requests_session.delete(server.rstrip("/") + "/data/JSESSION", timeout=10)
    requests_session.close()


def build_parser(xnat_session, extension_types):
    """
    Build the XNAT parser
    """

    logger = xnat_session.logger
    debug = xnat_session.debug

    # Check XNAT version
    logger.info("Determining XNAT version")
    version = xnat_session.xnat_version

    # Generate module
    parser = SchemaParser(debug=debug, logger=logger)

    if xnat_session.xnat_version.startswith("1.6"):
        logger.info("Found an 1.6 version ({})".format(version))
        build_function = parse_schemas_16
    elif version.startswith("1.7"):
        logger.info("Found an 1.7 version ({})".format(version))
        build_function = parse_schemas_17
    elif version.startswith("1.8"):
        # Can use the same builder as 1.7 for now
        logger.info("Found an 1.8 version ({})".format(version))
        build_function = parse_schemas_17
    elif version.startswith("1.9"):
        # Can use the same builder as 1.7 for now
        logger.info("Found an 1.9 version ({})".format(version))
        build_function = parse_schemas_17
    elif version.startswith("ML-BETA"):
        # Can use the same builder as 1.7 for now
        logger.info("Found an ML beta version ({})".format(version))
        build_function = parse_schemas_17
    else:
        logger.warning("Found an unsupported version ({}), trying 1.7 compatible model builder".format(version))
        build_function = parse_schemas_17

    logger.info("Start parsing schemas and building object model")
    build_function(parser, xnat_session, extension_types=extension_types)

    return parser, xnat_session


def build_model(xnat_session, extension_types, connection_id):
    """
    Build the XNAT data model for a given connection
    """

    logger = xnat_session.logger

    parser, xnat_session = build_parser(xnat_session, extension_types=extension_types)

    # Write code to temp file
    code_stringio = StringIO()
    parser.write(code_file=code_stringio)

    # The module is loaded in its private namespace based on the connection_id
    source_code = code_stringio.getvalue()
    module_name = "xnat.generated.model_{}".format(connection_id)
    loader = StringLoader(source_code)
    spec = importlib.util.spec_from_loader(module_name, loader)
    xnat_module = importlib.util.module_from_spec(spec)
    loader.exec_module(xnat_module)

    logger.debug("Loaded generated module")

    # Register all types parsed
    for key, cls in parser.class_list.items():
        if not (cls.name is None or (cls.base_class is not None and cls.base_class.startswith("xs:"))):
            cls_obj = getattr(xnat_module, cls.writer.python_name, None)
            if cls_obj is not None:
                cls_obj.__register__(xnat_module.XNAT_CLASS_LOOKUP)
            else:
                logger.warning("Cannot find class to register for {}".format(cls.name))

    xnat_module.SESSION = xnat_session

    # Add the required information from the module into the xnat_session object
    xnat_session.XNAT_CLASS_LOOKUP.update(xnat_module.XNAT_CLASS_LOOKUP)
    xnat_session.classes = xnat_module
    xnat_session.source_code = source_code
    search.inject_search_fields(xnat_session)
    logger.info("Object model created successfully")


def connect(
    server=None,
    user=None,
    password=None,
    verify=True,
    netrc_file=None,
    debug=False,
    extension_types=True,
    loglevel=None,
    logger=None,
    detect_redirect=True,
    no_parse_model=False,
    default_timeout=300,
    auth_provider=None,
    jsession=None,
    cli=False,
):
    """
    Connect to a server and generate the correct classed based on the servers xnat.xsd
    This function returns an object that can be used as a context operator. It will call
    disconnect automatically when the context is left. If it is used as a function, then
    the user should call ``.disconnect()`` to destroy the session and temporary code file.

    :param str server: uri of the server to connect to (including http:// or https://),
                       leave empty to use the `XNATPY_HOST` or `XNAT_HOST` environment variables
    :param str user: username to use, leave empty to use the `XNATPY_USER` or `XNAT_USER`
                     environment variables, netrc entry or anonymous login (in that order).
    :param str password: password to use with the username, leave empty when using netrc or the
                         `XNATPY_PASS` or `XNAT_PASS` environment variables.
                         If a username is given and no password, there will be a prompt
                         on the console requesting the password.
    :param bool verify: verify the https certificates, if this is false the connection will
                        be encrypted with ssl, but the certificates are not checked. This is
                        potentially dangerous, but required for self-signed certificates.
    :param str netrc_file: alternative location to use for the netrc file (path pointing to
                           a file following the netrc syntax)
    :param bool debug: Set debug information printing on and print extra debug information.
                       This is meant for xnatpy developers and not for normal users. If you
                       want to debug your code using xnatpy, just set the loglevel to DEBUG
                       which will show you all requests being made, but spare you the
                       xnatpy internals.
    :param bool extension_types: Flag to indicate whether or not to build an object model for
                                 extension types added by plugins.
    :param str loglevel: Set the level of the logger to desired level
    :param logging.Logger logger: A logger to reuse instead of creating an own logger
    :param bool detect_redirect: Try to detect a redirect (via a 302 response) and short-cut
                                 for subsequent requests
    :param bool no_parse_model: Create an XNAT connection without parsing the server data
                                model, this create a connection for which the simple
                                get/head/put/post/delete functions where, but anything
                                requiring the data model will file (e.g. any wrapped classes)
    :param int default_timeout: The default timeout of requests sent by xnatpy, is a 5 minutes
                                per default.
    :param str auth_provider: Set the auth provider to use to log in to XNAT.
    :return: XNAT session object
    :rtype: XNATSession

    Preferred use::

        >>> import xnat
        >>> with xnat.connect('https://central.xnat.org') as connection:
        ...    subjects = connection.projects['Sample_DICOM'].subjects
        ...    print('Subjects in the SampleDICOM project: {}'.format(subjects))
        Subjects in the SampleDICOM project: <XNATListing (CENTRAL_S01894, dcmtest1): <SubjectData CENTRAL_S01894>, (CENTRAL_S00461, PACE_HF_SUPINE): <SubjectData CENTRAL_S00461>>

    Alternative use::

        >>> import xnat
        >>> connection = xnat.connect('https://central.xnat.org')
        >>> subjects = connection.projects['Sample_DICOM'].subjects
        >>> print('Subjects in the SampleDICOM project: {}'.format(subjects))
        Subjects in the SampleDICOM project: <XNATListing (CENTRAL_S01894, dcmtest1): <SubjectData CENTRAL_S01894>, (CENTRAL_S00461, PACE_HF_SUPINE): <SubjectData CENTRAL_S00461>>
        >>> connection.disconnect()
    """

    # Generate a hash for the connection
    hasher = hashlib.md5()
    hasher.update(server.encode("utf-8"))
    hasher.update(str(time.time()).encode("utf-8"))
    connection_id = hasher.hexdigest()

    # Setup the logger for this connection
    if logger is None:
        logger = logging.getLogger("xnat-{}".format(connection_id))
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        # create formatter
        if debug:
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(module)s:%(lineno)d >> %(message)s")
        else:
            formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)

        if loglevel is not None:
            logger.setLevel(loglevel)
        elif debug:
            logger.setLevel("DEBUG")
        else:
            logger.setLevel("WARNING")

    # If verify is False, disable urllib3 warning and give a one time warning!
    if not verify:
        logger.warning("Verify is disabled, this will NOT verify the certificate of SSL connections!")
        logger.warning("Warnings about invalid certificates will be HIDDEN to avoid spam, but this")
        logger.warning("means that your connection can be potentially unsafe!")
        urllib3.disable_warnings()

    # Also possibly use the SSL_CERT_FILE and SSL_CERT_DIR env vars if other ones aren't set
    if verify is True or verify is None:
        verify = (
            os.environ.get("REQUESTS_CA_BUNDLE")
            or os.environ.get("CURL_CA_BUNDLE")
            or os.environ.get("SSL_CERT_FILE")
            or os.environ.get("SSL_CERT_DIR")
            or verify
        )

    # Create the correct requests session
    requests_session = requests.Session()
    user_agent = "xnatpy/{version} ({platform}/{release}; python/{python}; requests/{requests})".format(
        version=__version__,
        platform=platform.system(),
        release=platform.release(),
        python=platform.python_version(),
        requests=requests.__version__,
    )

    requests_session.headers.update({"User-Agent": user_agent})

    if not verify:
        requests_session.verify = False

    # Start out with any accidental auth, fill token once retrieved
    requests_session.auth = JSessionAuth()

    # Auto-detect server based on environment variables
    if not server:
        if not (server := os.environ.get("XNATPY_HOST")):
            if not (server := os.environ.get("XNAT_HOST")):
                raise RuntimeError("No server specified: no argument nor environment variable found")
    if not user:
        if not (user := os.environ.get("XNATPY_USER")):
            if not (user := os.environ.get("XNAT_USER")):
                logger.info("No username set, using anonymous/netrc login")
    if not password:
        if not (password := os.environ.get("XNATPY_PASS")):
            if not (password := os.environ.get("XNAT_PASS")):
                logger.info("No password set, using anonymous/netrc login")
    if server is None:
        raise exceptions.XNATValueError(
            "Cannot auto-detect which server to use, make sure either the XNAT_HOST"
            " or XNATPY_HOST environment variable is set!"
        )

    # Remove port and add .local to the domain in case there is no . in host
    # See issue #5388 in psf/requests for more info
    domain = parse.urlparse(server).netloc
    if ":" in domain:
        domain = domain.split(":")[0]
    if "." not in domain:
        domain = "{domain}.local".format(domain=domain)

    if jsession is not None:
        cookie = requests.cookies.create_cookie(
            domain=domain,
            name="JSESSIONID",
            value=jsession,
        )
        requests_session.cookies.set_cookie(cookie)
    else:
        if password is None:
            queried_user, queried_password = query_netrc(server, netrc_file, logger)
            if user is None or queried_user == user:
                user = queried_user
                password = queried_password
            elif queried_user is not None:
                logger.warning(f"Query result from .netrc is user {queried_user} but specified user was {user}")

        if user is not None and password is None:
            password = getpass.getpass(prompt=str("Please enter the password for user '{}':".format(user)))

    # Check for redirects
    original_uri = server
    logger.debug("GET URI {} for redirection detections".format(server))
    redirect_check_response = requests_session.get(server, timeout=10)

    if detect_redirect:
        server = detect_redirection(redirect_check_response, server, logger)

    if jsession is None:
        # If no username and password is found yet, re-query netrc after redirection
        if user is None and password is None:
            user, password = query_netrc(server, netrc_file, logger)

        if user is not None:
            # Get JSESSIONID and remove auth info again
            jsession_token = _create_jsession(
                requests_session,
                server=server,
                user=user,
                password=password,
                provider=auth_provider,
                debug=debug,
                logger=logger,
            )
        else:
            jsession_token = _query_jsession(requests_session, server=server, debug=debug, logger=logger)
    else:
        if requests_session.cookies.get("JSESSIONID", domain=domain) != jsession:
            message = "Failed to login by re-using existing jsession, the session is probably close on the server!"
            logger.error(message)
            raise exceptions.XNATLoginFailedError(message)
        jsession_token = jsession

    # Set JSESSION token for rest of requests if it is know, otherwise fall
    # back to basic auth
    if jsession_token:
        requests_session.auth = JSessionAuth(jsession_token)

        # Set the JSESSIONID cookie if it is not set
        if not requests_session.cookies.get("JSESSIONID", domain=domain):
            logger.warning("JSESSIONID cookie was not set automatically, do it manually...")
            cookie = requests.cookies.create_cookie(
                domain=domain,
                name="JSESSIONID",
                value=jsession_token,
            )
            requests_session.cookies.set_cookie(cookie)
    elif user is not None:
        logger.warning("Login using JSESSION failed, falling back to basic-auth.")
        requests_session.auth = (user, password)

    # Use a try so that errors result in closing the JSESSION and requests session
    try:
        # Check if login is successful
        if user is None and jsession is None:
            logged_in_user = check_auth_guest(requests_session, server=server, logger=logger)
        else:
            logger.debug("Checking login for {}".format(user))
            logged_in_user = check_auth(requests_session, server=server, user=user, jsession=jsession, logger=logger)

        if jsession and logged_in_user == "guest":
            logger.warning(
                "Attempt to log in with jsession resulted in being logged in as"
                ' "guest", something might have gone wrong'
            )

        # Create the XNAT connection
        if cli:
            SessionType = BaseXNATSession
        else:
            SessionType = XNATSession

        xnat_session = SessionType(
            server=server,
            logger=logger,
            interface=requests_session,
            debug=debug,
            original_uri=original_uri,
            logged_in_user=logged_in_user,
            default_timeout=default_timeout,
            jsession=jsession_token,
        )

        # Parse data model and create classes
        if not no_parse_model:
            build_model(xnat_session, extension_types=extension_types, connection_id=connection_id)

        return xnat_session
    except:
        _wipe_jsession(requests_session, server)
        raise
