# Copyright 2011-2025 Biomedical Imaging Group Rotterdam, Departments of
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

import re

import click

import xnat

from .helpers import connect_cli, xnatpy_login_options


@click.group()
def download():
    """
    Commands to download XNAT objects to your machine.
    """
    pass


@download.command()
@click.argument("project")
@click.argument("targetdir")
@xnatpy_login_options
def project(project, targetdir, **kwargs):
    """Download XNAT project to the target directory."""
    with connect_cli(**kwargs) as session:
        xnat_project = session.projects.get(project)

        if xnat_project is None:
            session.logger.error("[ERROR] Could not find project!".format(project))
            return

        result = xnat_project.download_dir(targetdir)
        session.logger.info("Download complete!")


@download.command()
@click.argument("project")
@click.argument("experiments", nargs=-1)
@click.argument("targetdir")
@xnatpy_login_options
def experiments(project, experiments, targetdir, **kwargs):
    """Download XNAT project to the target directory."""
    with connect_cli(**kwargs) as session:

        if project not in session.projects:
            session.logger.error(f"[ERROR] Could not find project: '{project} for user {kwargs.get('user')}'")
            return

        xnat_project = session.projects[project]

        for experiment in experiments:
            if experiment not in xnat_project.experiments:
                session.logger.warning(f"[WARNING] Could not find experiment '{experiment}'")
                continue

            xnat_project.experiments[experiment].download_dir(targetdir)
        session.logger.info("Download complete!")


@download.command()
@click.option("--project", help="Filter for the project names")
@click.option("--experiment", help="Filter for the experiment labels")
@click.option("--subject", help="Filter for the subject labels")
@click.option("--scan", help="Filter for the scan types")
@click.option("--resource", help="Filter for the resource labels")
@click.option(
    "--level",
    type=click.Choice(xnat.MappingLevel),
    default=xnat.MappingLevel.SCAN_RESOURCE,
    help="What resource level to search on",
)
@click.option("--regex", is_flag=True, default=False, help="Flag to switch from fnmatch to regular expressions")
@click.argument("targetdir", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, writable=True))
@xnatpy_login_options
def batch(project, experiment, subject, scan, resource, level, regex, targetdir, **kwargs):
    """Download a batch of data based on a search to target directory

    Download a batch of data in one go. Will download all data matching a set of filters. The
    filters are by default applied using fnmatch can using the use_regex flag this will be
    changed to regular expression matching.

    The level to search on is controlled by the level, possible options are: connection,
    project, project_resource, subject, subject_resource, experiment, experiment_resource,
    scan, or scan_resource

    Note that on Windows click expands the * character automatically and on linux there is shell
    expansion, which can make it hard to pass a correct filter string. In that case you can pass
    the filter as: r'$filter' instead, and it will be automatically turned back into $filter,
    e.g. r'test*' would become test* and avoid being automatically expanded.
    """

    def fix_escaped_arg(value):
        if isinstance(value, str) and re.match("^r'.*'$", value):
            return value[2:-1]
        return value

    project = fix_escaped_arg(project)
    subject = fix_escaped_arg(subject)
    experiment = fix_escaped_arg(experiment)
    scan = fix_escaped_arg(scan)
    resource = fix_escaped_arg(resource)

    with connect_cli(**kwargs) as session:
        session.batch_download(
            targetdir,
            project=project,
            subject=subject,
            experiment=experiment,
            scan=scan,
            resource=resource,
            level=level,
            use_regex=regex,
        )
