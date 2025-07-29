#  Copyright 2011-2025 Biomedical Imaging Group Rotterdam, Departments of
#  Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import inspect
from typing import Any, Literal

import click
from click_option_group import optgroup

import xnat

OUTPUT_OPTIONS = ["raw", "csv", "human"]
OUTPUT_OPTIONS_TYPE = Literal["raw", "csv", "human"]


def xnatpy_common_options(func):
    common_options = [
        optgroup.group("Common XNATpy options", help="Options respected by (most) XNATpy commands"),
        optgroup.option(
            "--output-format",
            envvar="XNATPY_OUTPUT",
            type=click.Choice(OUTPUT_OPTIONS, case_sensitive=False),
            help="Output format",
            default="human",
        ),
    ]

    for option in reversed(common_options):
        func = option(func)

    return func


def xnatpy_login_options(func):
    login_options = [
        optgroup.group("Server configuration", help="The configuration of some server connection"),
        optgroup.option(
            "--host",
            "server",
            envvar=["XNATPY_HOST", "XNAT_HOST"],
            required=True,
            help="URL of the XNAT host to connect to, if not given will check XNAT_HOST or XNATPY_HOST environment variables",
        ),
        optgroup.option("--user", "-u", envvar=["XNATPY_USER", "XNAT_USER"], help="Username to connect to XNAT with."),
        optgroup.option(
            "--netrc",
            "netrc_file",
            "-n",
            help=".netrc file location, if not given will check NETRC environment variable or default to ~/.netrc",
        ),
        optgroup.option(
            "--jsession", envvar="XNATPY_JSESSION", help="JSESSION value for re-using a previously opened login session"
        ),
        optgroup.option(
            "--timeout",
            "default_timeout",
            envvar="XNATPY_TIMEOUT",
            type=float,
            help="Timeout for requests made by this command in ms.",
        ),
        optgroup.option(
            "--loglevel",
            envvar="XNATPY_LOGLEVEL",
            type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
            help="Logging verbosity level.",
        ),
    ]

    for option in reversed(login_options):
        func = option(func)

    return func


def xnatpy_all_options(func):
    func = xnatpy_common_options(func)
    func = xnatpy_login_options(func)
    return func


def connect_cli(**options: Any):
    # Ensure that only valid connection arguments are in the options
    connect_signature = inspect.signature(xnat.connect)
    options = {k: v for k, v in options.items() if k in connect_signature.parameters}

    # The cli argument is True by default
    if "cli" not in options:
        options["cli"] = True

    # Create the connection using the filtered arguments
    return xnat.connect(**options)
