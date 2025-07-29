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

from pathlib import Path

import click

import xnat

from .. import mixin
from .helpers import connect_cli, xnatpy_login_options


@click.command()
@click.argument('data_path', type=click.Path(), nargs=-1)
@click.option("--project", help="Filter for the project names")
@click.option("--subject", help="Filter for the subject labels")
@click.option("--experiment", help="Filter for the experiment labels")
@click.option("--scan", help="Filter for the scan types")
@click.option("--resource", help="Filter for the resource labels", required=True)
@click.option("--names", multiple=True, help="Name for the files on the remote server", required=False)
@xnatpy_login_options
def upload(data_path, project, subject, experiment, scan, resource, names, **kwargs):
    """
    Commands to upload data to XNAT. If the DATA_PATH is point to a file, upload the file
    to the resource. If DATA_PATH is a directory, upload the directory contents to the resource.

    DATA_PATH is the path to the data to upload to the specified resource
    """
    if names and len(names) != len(data_path):
        raise ValueError(f"The amount of names to use for the uploads and the files to upload should match!")

    # Convert data_paths to Path and set names if not given
    data_path = [Path(x) for x in data_path]
    if not names:
        names = [x.name for x in data_path]

    with connect_cli(**kwargs) as connection:
        target = connection
        logger = connection.logger

        if project:
            logger.info(f'Selecting project {project} from {target}')
            target = target.projects[project]

        if subject:
            logger.info(f'Selecting subject {subject} from {target}')
            target = target.subjects[subject]

        if experiment:
            logger.info(f'Selecting experiment {experiment} from {target}')
            target = target.experiments[experiment]

        # Make sure we have an ImageSessionData if we want to extract a scan
        if scan:
            if not isinstance(target, mixin.ImageSessionData):
                raise xnat.exceptions.XNATValueError(f"Cannot extract scan {scan} from a non-ImageSessionData {target}")
            if scan not in target.scans:
                raise xnat.exceptions.XNATKeyError(f"Scan {scan} not found under {target}")

            logger.info(f'Selecting scan {scan} from {target}')
            target = target.scans[scan]

        # Get the target resource
        logger.info(f'Selecting resource {resource} from {target}')
        target_resource = target.resources.get(resource)

        if target_resource is None:
            uri = "{}/resources/{}".format(target.uri, resource)
            connection.put(uri, format=None)
            target.clearcache()  # The resources changed, so we have to clear the cache
            target_resource = target.resources[resource]

        for name, item_to_upload in zip(names, data_path):
            if item_to_upload.is_file():
                logger.info(f'Uploading file {item_to_upload} to {target_resource} with remote_path {name}')
                target_resource.upload(item_to_upload, name)
            elif item_to_upload.is_dir():
                logger.info(f'Uploading directory {item_to_upload} to {target_resource}')
                target_resource.upload_dir(item_to_upload, target_resource)
            else:
                logger.error(f'Unknown item to upload: {item_to_upload}, not a valid file or directory, skipping')


