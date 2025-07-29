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

from time import sleep

import click

import xnat

from ..scripts.copy_project import XNATProjectCopier
from ..scripts.data_integrity_check import XNATIntegrityCheck
from ..scripts.delete_project import delete_object, read_description
from .helpers import connect_cli, xnatpy_login_options


@click.group(name="script")
def script():
    """
    Collection of various XNAT-related scripts.
    """
    pass


@script.command()
@click.option("--source-host", required=True, help="Source XNAT URL")
@click.option("--source-project", required=True, help="Source XNAT project")
@click.option("--dest-host", required=True, help="Destination XNAT URL")
@click.option("--dest-project", required=True, help="Destination XNAT project")
def copy_project(source_host, source_project, dest_host, dest_project):
    """Copy all data from source project to destination project. Source and destination projects can be located in different XNAT instances."""
    with xnat.connect(source_host, default_timeout=900) as source_xnat, xnat.connect(
        dest_host, default_timeout=900
    ) as dest_xnat:
        # Find projects
        try:
            source_project = source_xnat.projects[source_project]
            dest_project = dest_xnat.projects[dest_project]
        except KeyError as error:
            print(error.message)
        else:
            # Create and start copier
            copier = XNATProjectCopier(source_xnat, source_project, dest_xnat, dest_project)
            copier.start()


@script.command()
@click.option("--project", required="True", help="XNAT project ID")
@click.option("--force", is_flag=True, default=False, help="Skips project description check")
@click.option("--remove", is_flag=True, default=False, help="Remove the actual project from XNAT")
@click.option("--dry-run-false", is_flag=True, default=False, help="Actually delete data")
@xnatpy_login_options
def delete_project(project, force, remove, dry_run_false, **kwargs):
    """Delete a project from XNAT."""

    # Ensure a long minimum default timeout as this script might cause to server to respond slowly for
    # some of the operations
    if not isinstance(kwargs["default_timeout"], (int, float)) or kwargs["default_timeout"] < 1800:
        kwargs["default_timeout"] = 1800

    with connect_cli(**kwargs) as xnat_host:
        print(f'Connected to {kwargs.get("host")}')
        try:
            xnat_project = xnat_host.projects[project]
        except KeyError:
            print(f"Could not locate project: {project}")
        if not force:
            project_description = read_description()
            xnat_description = xnat_project.description.strip()
            if project_description != xnat_description:
                print(f"ERROR Description does not match. xnat_description:")
                print(f'"{xnat_description}"')
                print(f"VS project_description:")
                print(f'"{project_description}"')
                return
        # Start looping over subjects/experiments
        print(f"Start deleting {xnat_project.name}")
        for _, xnat_subject in sorted(xnat_project.subjects.items()):
            subject_label = xnat_subject.label
            print(f"Start deleting {subject_label}")
            for _, xnat_experiment in xnat_subject.experiments.items():
                experiment_label = xnat_experiment.label
                print(f"Start deleting {experiment_label}")
                for _, xnat_scan in xnat_experiment.scans.items():
                    delete_object(xnat_scan, dry_run_false)
                delete_object(xnat_experiment, dry_run_false)
            delete_object(xnat_subject, dry_run_false)
        if remove:
            delete_object(xnat_project, dry_run_false)


@script.command()
@click.option("--host", required=True, help="XNAT URL")
@click.option("--xnat-home-dir", required=True, help="Path to XNAT home directory")
@click.option("--report", required=True, help="Path to report file")
def data_integrity_check(host, xnat_home_dir, report):
    """Perform data integrity check."""
    xnat_integrity_checker = XNATIntegrityCheck(host, xnat_home_dir)
    xnat_integrity_checker.start()
    print("progress\t FS\tXNAT")
    while xnat_integrity_checker.is_running():
        xnat_progress, fs_progress = xnat_integrity_checker.progress()
        print(f"\t\t{fs_progress*100}\t{xnat_progress*100}", end="\r")
        sleep(1)
    fs_progress, xnat_progress = xnat_integrity_checker.progress()
    print(f"\t\t{fs_progress*100}\t{xnat_progress*100}")
    print("--- REPORT ---")
    xnat_integrity_checker.write_report(report)
    print("--- DONE ---")
