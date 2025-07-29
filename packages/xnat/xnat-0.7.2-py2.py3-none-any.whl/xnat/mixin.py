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

from __future__ import annotations

import os
import shutil
import tarfile
import tempfile
from abc import ABCMeta, abstractmethod
from io import BytesIO
from pathlib import Path
from typing import IO, Callable, Optional, Union
from zipfile import ZipFile

from . import exceptions
from .core import XNATBaseObject, XNATListing, caching
from .map import MappingLevel, MappingObjectStates, check_result_type
from .search import SearchField
from .type_hints import JSONType
from .users import User, Users
from .utils import FilterFunctions, mixedproperty, pythonize_attribute_name

try:
    PYDICOM_LOADED = True
    import pydicom
except ImportError:
    PYDICOM_LOADED = False


class MappedFunctionFailed:
    def __init__(self, reason: str):
        self.reason = reason

    def __eq__(self, other):
        return isinstance(other, MappedFunctionFailed) and self.reason == other.reason


class Mappable(metaclass=ABCMeta):
    @property
    @abstractmethod
    def logger(self):
        raise NotImplementedError()

    @abstractmethod
    def mapping_iter(self, states: MappingObjectStates, level: MappingLevel, filter_function):
        raise NotImplementedError()

    def map(
        self,
        function: Callable[[XNATBaseObject, ...], JSONType],
        level: Union[MappingLevel, str],
        args: Optional[list] = None,
        kwargs: Optional[dict] = None,
        filter_function: "FilterFunctions" = None,
        logfile: Union[str, Path, None] = None,
    ) -> dict[str, JSONType]:
        """
        Map a given function over all items of a certain level in a project. Function should take the XNAT object of the
        level specified as the first argument and can take additional args and kwargs.

        :param function: Function to apply to all items, this should return json serializable data.
        :param level: The level off items which to apply the function to.
        :param args: Extra position arguments to pass the function.
        :param kwargs: Extra keyword arguments to pass to the function.
        :param filter_function: Filter functions object that allows you to add filters for subject, experiments, and
                                scans.
        :param logfile: path to a logfile for recording the results of the map operation, this allows the resume the
                        map in case of errors/crashes.
        :return: A dictionary with the fulluri of each object found at the specified level as the key and the result of
                 the function as the value. If the function fails the value will be a MappingFunctionFailed object
                 instead.
        """
        self.logger.info(f"Mapping {self} at level: {level}")
        states = MappingObjectStates(logger=self.logger, filename=logfile)

        if states.succeeded(self):
            return {x.uri: x.result for x in states.values() if x.requested}

        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        if not isinstance(level, MappingLevel):
            try:
                level = MappingLevel(level)
            except (ValueError, KeyError):
                msg = f'Level "{level}" is not a valid MappingLevel, available: {[x.value for x in MappingLevel]}'
                self.logger.error(msg)
                raise ValueError(msg)

        for uri, values in states.items():
            self.logger.info(f"{uri}-{values.success}")

        # Basically a for loop but with the option to send to the generator
        for xnat_object in self.mapping_iter(states, level, filter_function):
            try:
                result = function(xnat_object, *args, **kwargs)
            except BaseException as e:
                states.failed(xnat_object, str(e), requested=True)
            else:
                # Make sure that if a logfile is used the result is compatible
                if logfile and not check_result_type(result):
                    raise TypeError(
                        f"The result of the function is of incompatible"
                        f" with the map function logfile: [{type(result).__name__}] {result}"
                    )

                states.success(xnat_object, result, requested=True)

        # Wrap failed cases in the MappingFunctionFailed object so it can be recognised as failed
        return {
            x.uri: x.result if x.success else MappedFunctionFailed(x.result) for x in states.values() if x.requested
        }


class ProjectData(XNATBaseObject, Mappable):
    SECONDARY_LOOKUP_FIELD = "name"
    FROM_SEARCH_URI = "{session_uri}/projects/{id}"

    @classmethod
    def create_cache_id(cls, uri, fieldname, data):
        return cls.__name__, data["id_"]

    @property
    def cache_id(self):
        return type(self).__name__, self.id

    def _get_creation_uri(self, parent_uri, id_, secondary_lookup_value):
        return f"/data/archive/projects/{id_}"

    # just for consistency with subject/experiment for custom variable map
    @property
    def project(self):
        return self.id

    @property
    def users(self):
        return Users(self.xnat_session, path=self.uri + "/users")

    @property
    def access_level(self):
        """
        Shows the access level the currently logged in users has for this particular project
        """
        return self.xnat_session.access_levels.get(self.id, "No access")

    def set_access(self, user: Union[User, str], level: str):
        if isinstance(user, User):
            user = user.login

        self.xnat_session.put(f"{self.uri}/users/{level}/{user}")

    def remove_access(self, user: Union[User, str]):

        if not isinstance(user, User):
            try:
                next(x for x in self.users.values() if x.login == user or x.email == user)
            except StopIteration:
                message = f"Cannot find a username with either login or email matching {user}!"
                self.logger.error(message)
                raise exceptions.XNATValueError(message)

        self.xnat_session.delete(f"{self.uri}/users/{user.access_level}/{user.login}")

    @mixedproperty
    def parent(cls):
        return cls._PARENT_CLASS

    @parent.getter
    def parent(self):
        return self.xnat_session

    @property
    def fulluri(self):
        return "{}/projects/{}".format(self.xnat_session.fulluri, self.id)

    @property
    @caching
    def subjects(self):
        return XNATListing(
            self.uri + "/subjects",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="subjects",
            secondary_lookup_field="label",
            xsi_type="xnat:subjectData",
        )

    @property
    @caching
    def experiments(self):
        return XNATListing(
            self.uri + "/experiments",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="experiments",
            secondary_lookup_field="label",
        )

    @property
    @caching
    def files(self):
        return XNATListing(
            self.uri + "/files",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="files",
            secondary_lookup_field="Name",
            xsi_type="xnat:fileData",
        )

    @property
    @caching
    def resources(self):
        return XNATListing(
            self.uri + "/resources",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="resources",
            secondary_lookup_field="label",
            xsi_type="xnat:resourceCatalog",
        )

    def create_resource(self, label, format=None, data_dir=None, method=None) -> "AbstractResource":
        uri = f"{self.fulluri}/resources/{label}"
        self.xnat_session.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache
        resource = self.xnat_session.create_object(uri)

        if data_dir is not None:
            resource.upload_dir(data_dir, method=method)

        return resource

    def download_dir(self, target_dir, verbose=True, progress_callback=None):
        """
        Download the entire project and unpack it in a given directory. Note
        that this method will create a directory structure following
        $target_dir/{project.name}/{subject.label}/{experiment.label}
        and unzip the experiment zips as given by XNAT into that. If
        the $target_dir/{project.name} does not exist, it will be created.

        :param str target_dir: directory to create project directory in
        :param bool verbose: show progress
        :param progress_callback: function to call with progress string
                                  should be a function with one argument
        """

        project_dir = os.path.join(target_dir, self.name)
        if not os.path.isdir(project_dir):
            os.mkdir(project_dir)

        number_of_subjects = len(self.subjects)

        for n, subject in enumerate(self.subjects.values(), start=1):
            if progress_callback:
                progress_callback("Downloading subject {} of {}".format(n, number_of_subjects))

            subject.download_dir(project_dir, verbose=verbose, progress_callback=progress_callback)

        if verbose:
            self.logger.info("Downloaded project to {}".format(project_dir))

    def cli_str(self):
        return "Project {name}: id={id}, full URI:{uri}".format(name=self.name, id=self.id, uri=self.fulluri)

    @property
    @caching
    def data_dir(self):
        if self.xnat_session.mount_data_dir is None:
            return None

        data_dir = f"{self.xnat_session.mount_data_dir}/projects/{self.id}"

        if not os.path.isdir(data_dir):
            self.logger.info(f"Determined data_dir to be {data_dir}, but it does not exist!")
            return None

        return data_dir

    def mapping_iter(self, states: MappingObjectStates, level: MappingLevel, filter_function):
        self.logger.debug(f"Start Iterating for project {self}")
        with states.descend(self, MappingLevel.PROJECT):
            if level == MappingLevel.PROJECT_RESOURCE:
                for resource in self.resources.values():
                    if states.succeeded(resource):
                        continue
                    if filter_function and not filter_function.resource(resource):
                        continue
                    yield resource
            else:
                for xnat_subject in self.subjects.values():
                    if states.succeeded(xnat_subject):
                        continue
                    if filter_function and not filter_function.subject(xnat_subject):
                        continue
                    if level == MappingLevel.SUBJECT:
                        yield xnat_subject
                    else:
                        yield from xnat_subject.mapping_iter(states, level, filter_function)
        self.logger.debug(f"Finished Iterating for project {self}")


class InvestigatorData(XNATBaseObject):
    def __str__(self):
        title = self.title or ""
        first = self.firstname or ""
        last = self.lastname or ""
        fullname = "{title} {first} {last}".format(title=title, first=first, last=last).strip()
        return "<InvestigatorData {fullname}>".format(fullname=fullname)


class SubjectData(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = "label"
    FROM_SEARCH_URI = "{session_uri}/projects/{project}/subjects/{subjectid}"

    @classmethod
    def create_cache_id(cls, uri, fieldname, data):
        return cls.__name__, data["id_"]

    @property
    def cache_id(self):
        return type(self).__name__, self.id

    @property
    def fulluri(self):
        return "{}/projects/{}/subjects/{}".format(self.xnat_session.fulluri, self.project, self.id)

    @mixedproperty
    def label(cls):
        # 0 Automatically generated Property, type: xs:string
        return SearchField(cls, "label")

    @label.getter
    def label(self):
        # Check if label is already inserted during listing, that should be valid
        # label for the project under which it was listed in the first place
        try:
            return self._overwrites["label"]
        except KeyError:
            pass

        # Retrieve the label the hard and costly way
        try:
            # First check if subject is shared into current project
            sharing = next(x for x in self.fulldata["children"] if x["field"] == "sharing/share")
            share_info = next(x for x in sharing["items"] if x["data_fields"]["project"] == self.project)
            label = share_info["data_fields"]["label"]
        except (KeyError, StopIteration):
            label = self.get("label", type_=str)

        # Cache label for future use
        self._overwrites["label"] = label
        return label

    @label.setter
    def label(self, value):
        self.xnat_session.put(self.fulluri, query={"label": value})
        self.clearcache()

    @property
    @caching
    def files(self):
        return XNATListing(
            self.uri + "/files",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="files",
            secondary_lookup_field="Name",
            xsi_type="xnat:fileData",
        )

    def download_dir(self, target_dir, verbose=True, progress_callback=None):
        """
        Download the entire subject and unpack it in a given directory. Note
        that this method will create a directory structure following
        $target_dir/{subject.label}/{experiment.label}
        and unzip the experiment zips as given by XNAT into that. If
        the $target_dir/{subject.label} does not exist, it will be created.

        :param str target_dir: directory to create subject directory in
        :param bool verbose: show progress
        :param progress_callback: function to call with progress string
                                  should be a function with one argument
        """
        subject_dir = os.path.join(target_dir, self.label)
        if not os.path.isdir(subject_dir):
            os.mkdir(subject_dir)

        number_of_experiments = len(self.experiments)

        for n, experiment in enumerate(self.experiments.values(), start=1):
            if progress_callback is not None:
                progress_callback("Downloading experiment {} of {}".format(n, number_of_experiments))
            experiment.download_dir(subject_dir, verbose=verbose)

        if verbose:
            self.logger.info("Downloaded subject to {}".format(subject_dir))

    def share(self, project, label=None):
        # Create the uri for sharing
        share_uri = "{}/projects/{}".format(self.fulluri, project)

        # Add label if needed
        query = {}
        if label is not None:
            query["label"] = label

        self.xnat_session.put(share_uri, query=query)
        self.clearcache()

    def create_resource(self, label, format=None, data_dir=None, method=None):
        uri = "{}/resources/{}".format(self.fulluri, label)
        self.xnat_session.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache
        resource = self.xnat_session.create_object(uri)

        if data_dir is not None:
            resource.upload_dir(data_dir, method=method)

        return resource

    def cli_str(self):
        return "Subject {name}: id={id}, project:{proj}, full URI:{uri}".format(
            name=self.label, id=self.id, proj=self.project, uri=self.fulluri
        )

    def mapping_iter(self, states: MappingObjectStates, level: MappingLevel, filter_function: "FilterFunctions"):
        self.logger.info(f"Start Iterating for subject {self.label}")
        with states.descend(self, MappingLevel.SUBJECT):
            if level == MappingLevel.SUBJECT_RESOURCE:
                for resource in self.resources.values():
                    if states.succeeded(resource):
                        continue
                    if filter_function and not filter_function.resource(resource):
                        continue
                    yield resource
            else:
                for xnat_experiment in self.experiments.values():
                    if states.succeeded(xnat_experiment):
                        continue
                    if filter_function and not filter_function.experiment(xnat_experiment):
                        continue
                    if level == MappingLevel.EXPERIMENT:
                        yield xnat_experiment
                    else:
                        yield from xnat_experiment.mapping_iter(states, level, filter_function)
        self.logger.info(f"Finished Iterating for subject {self.label}")


class ExperimentData(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = "label"
    FROM_SEARCH_URI = "{session_uri}/projects/{project}/subjects/{subject_id}/experiments/{session_id}"
    DEFAULT_SEARCH_FIELDS = ["id", "project", "subject_id"]

    def __init__(
        self,
        uri=None,
        xnat_session=None,
        id_=None,
        datafields=None,
        parent=None,
        fieldname=None,
        overwrites=None,
        **kwargs,
    ):

        # If experiment is being created, check if experiment already exists
        if uri is None and parent is not None:
            if isinstance(parent, XNATListing):
                check_parent = parent.parent
            else:
                check_parent = parent

            if isinstance(check_parent, SubjectAssessorData):
                check_parent = check_parent.subject

            if not isinstance(check_parent, SubjectData):
                raise exceptions.XNATValueError(
                    f"Cannot determine parent for experiment, should be a"
                    f" SubjectData or SubjectAssessorData, found {type(parent)}!"
                )

            project = check_parent.xnat_session.projects[check_parent.project]

            # Check what argument to use to build the URL
            if self._DISPLAY_IDENTIFIER is not None:
                url_part_argument = pythonize_attribute_name(self._DISPLAY_IDENTIFIER)
            elif self.SECONDARY_LOOKUP_FIELD is not None:
                url_part_argument = self.SECONDARY_LOOKUP_FIELD

            # Get extra required url part
            url_part = str(kwargs.get(url_part_argument))
            if project.experiments.get(url_part) and not overwrites:
                self.logger.error(f"Experiment with label {url_part} already exists in project {project.id}.")
                raise exceptions.XNATObjectAlreadyExistsError(
                    f"Experiment with label {url_part} already exists in project {project.id}."
                )

        super().__init__(uri, xnat_session, id_, datafields, parent, fieldname, overwrites, **kwargs)

    @classmethod
    def create_cache_id(cls, uri, fieldname, data):
        return cls.__name__, data["id_"]

    @property
    def cache_id(self):
        return type(self).__name__, self.id

    @mixedproperty
    def label(cls):
        return SearchField(cls, "label")

    @label.getter
    def label(self):
        # Check if label is already inserted during listing, that should be valid
        # label for the project under which it was listed in the first place
        try:
            return self._overwrites["label"]
        except KeyError:
            pass

        # Retrieve the label the hard and costly way
        try:
            # First check if subject is shared into current project
            sharing = next(x for x in self.fulldata["children"] if x["field"] == "sharing/share")
            share_info = next(x for x in sharing["items"] if x["data_fields"]["project"] == self.project)
            label = share_info["data_fields"]["label"]
        except (KeyError, StopIteration):
            label = self.get("label", type_=str)

        # Cache label for future use
        self._overwrites["label"] = label
        return label

    @label.setter
    def label(self, value):
        self.xnat_session.put(self.fulluri, query={"label": value})
        self.clearcache()

    def cli_str(self):
        return "Session {name}".format(name=self.label)

    @property
    @caching
    def status(self) -> str:
        response = self.xnat_session.get(f"{self.fulluri}/status")
        return response.text

    @status.setter
    def status(self, value):
        if value == "active":
            self.activate()
        elif value == "quarantined":
            self.quarantine()
        else:
            raise exceptions.XNATValueError(
                f"Status of an experiments has to be 'active' or 'quarantined', found {value}"
            )

    def activate(self):
        self.xnat_session.put(self.fulluri, query={"activate": "true"})
        self._cache.pop("status", None)

    def quarantine(self):
        self.xnat_session.put(self.fulluri, query={"quarantine": "true"})
        self._cache.pop("status", None)

    @property
    @caching
    def data_dir(self):
        if self.xnat_session.mount_data_dir is None:
            return None

        data_dir = f"{self.xnat_session.mount_data_dir}/projects/{self.project}/experiments/{self.label}"

        if not os.path.isdir(data_dir):
            self.logger.info(f"Determined data_dir to be {data_dir}, but it does not exist!")
            return None

        return data_dir

    def mapping_iter(self, states: MappingObjectStates, level: MappingLevel, filter_function: "FilterFunctions"):
        self.logger.info(f"Start Iterating for experiment {self.label}")
        with states.descend(self, MappingLevel.EXPERIMENT):
            if level == MappingLevel.EXPERIMENT_RESOURCE:
                for resource in self.resources.values():
                    if states.succeeded(resource):
                        continue
                    if filter_function and not filter_function.resource(resource):
                        continue
                    yield resource
            else:
                for xnat_scan in self.scans.values():
                    if states.succeeded(xnat_scan):
                        continue
                    if filter_function and not filter_function.scan(xnat_scan):
                        continue
                    if level == MappingLevel.SCAN:
                        self.logger.info(f"Starting {xnat_scan}")
                        yield xnat_scan
                    else:
                        yield from xnat_scan.mapping_iter(states, level, filter_function)
        self.logger.info(f"Finished Iterating for experiment {self.label}")


class SubjectAssessorData(XNATBaseObject):
    @property
    def fulluri(self):
        return "/data/archive/projects/{}/subjects/{}/experiments/{}".format(self.project, self.subject_id, self.id)

    @property
    def subject(self):
        return self.xnat_session.subjects[self.subject_id]


class ImageSessionData(XNATBaseObject):
    @property
    @caching
    def files(self):
        return XNATListing(
            self.fulluri + "/files",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="files",
            secondary_lookup_field="Name",
            xsi_type="xnat:fileData",
        )

    def create_assessor(self, label, type_):
        uri = "{}/assessors/{label}?xsiType={type}&label={label}&req_format=qs".format(
            self.fulluri, type=type_, label=label
        )
        self.xnat_session.put(uri, accepted_status=(200, 201))
        self.clearcache()  # The resources changed, so we have to clear the cache
        return self.xnat_session.create_object("{}/assessors/{}".format(self.fulluri, label), type_=type_)

    def download(self, path, scan_filter="ALL", verbose=True):
        self.xnat_session.download_zip(self.fulluri + "/scans/{}/files".format(scan_filter), path, verbose=verbose)

    def download_dir(self, target_dir, scan_filter="ALL", verbose=True):
        """
        Download the entire experiment and unpack it in a given directory. Note
        that this method will create a directory structure following
        $target_dir/{experiment.label} and unzip the experiment zips
        as given by XNAT into that. If the $target_dir/{experiment.label} does
        not exist, it will be created.

        :param str target_dir: directory to create experiment directory in
        :param bool verbose: show progress
        """
        # Check if there are actually file to be found
        file_list = self.xnat_session.get_json(self.fulluri + "/scans/{}/files".format(scan_filter))
        if len(file_list["ResultSet"]["Result"]) == 0:
            # Just make sure the target directory exists and stop
            if not os.path.exists(target_dir):
                os.mkdir(target_dir)
            return

        with tempfile.TemporaryFile() as temp_path:
            self.xnat_session.download_stream(
                self.fulluri + "/scans/ALL/files", temp_path, format="zip", verbose=verbose
            )

            with ZipFile(temp_path) as zip_file:
                zip_file.extractall(target_dir)

        if verbose:
            self.logger.info("\nDownloaded image session to {}".format(target_dir))

    def share(self, project, label=None):
        # Create the uri for sharing
        share_uri = "{}/projects/{}".format(self.fulluri, project)

        # Add label if needed
        query = {}
        if label is not None:
            query["label"] = label

        self.xnat_session.put(share_uri, query=query)
        self.clearcache()


class DerivedData(XNATBaseObject):
    @property
    def fulluri(self):
        return "/data/experiments/{}/assessors/{}".format(self.image_session_id, self.id)

    @property
    @caching
    def files(self):
        return XNATListing(
            self.fulluri + "/files",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="files",
            secondary_lookup_field="Name",
            xsi_type="xnat:fileData",
        )

    @property
    @caching
    def resources(self):
        return XNATListing(
            self.fulluri + "/resources",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="resources",
            secondary_lookup_field="label",
            xsi_type="xnat:resourceCatalog",
        )

    def create_resource(self, label, format=None, data_dir=None, method=None):
        uri = "{}/resources/{}".format(self.fulluri, label)
        self.xnat_session.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache
        resource = self.xnat_session.create_object(uri)

        if data_dir is not None:
            resource.upload_dir(data_dir, method=method)

        return resource

    def download(self, path, verbose=True):
        self.xnat_session.download_zip(self.uri + "/files", path, verbose=verbose)


class ImageScanData(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = "type"

    def mapping_iter(self, states: MappingObjectStates, level: MappingLevel, filter_function: "FilterFunctions"):
        self.logger.info(f"Start Iterating for scan {self}")
        with states.descend(self, MappingLevel.SCAN):
            if level == MappingLevel.SCAN_RESOURCE:
                for resource in self.resources.values():
                    if states.succeeded(resource):
                        continue
                    if filter_function and not filter_function.resource(resource):
                        continue
                    yield resource
        self.logger.info(f"Finished Iterating for experiment {self}")

    @property
    def fields(self):
        return self.parameters.add_param

    @property
    @caching
    def files(self):
        return XNATListing(
            self.uri + "/files",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="files",
            secondary_lookup_field="Name",
            xsi_type="xnat:fileData",
        )

    @property
    @caching
    def resources(self):
        return XNATListing(
            self.uri + "/resources",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="resources",
            secondary_lookup_field="label",
            xsi_type="xnat:resourceCatalog",
        )

    def create_resource(self, label, format=None, data_dir=None, method="tgz_file"):
        uri = "{}/resources/{}".format(self.uri, label)
        self.xnat_session.put(uri, format=format)
        self.clearcache()  # The resources changed, so we have to clear the cache
        resource = self.xnat_session.create_object(uri)

        if data_dir is not None:
            resource.upload_dir(data_dir, method=method)

        return resource

    def download(self, path, verbose=True):
        self.xnat_session.download_zip(self.uri + "/files", path, verbose=verbose)

    def download_dir(self, target_dir, verbose=True):
        with tempfile.TemporaryFile() as temp_path:
            self.xnat_session.download_stream(self.uri + "/files", temp_path, format="zip", verbose=verbose)

            with ZipFile(temp_path) as zip_file:
                zip_file.extractall(target_dir)

        if verbose:
            self.logger.info("Downloaded image scan data to {}".format(target_dir))

    def dicom_dump(self, fields=None):
        """
        Retrieve a dicom dump as a JSON data structure
        See the XAPI documentation for more detailed information: `DICOM Dump Service <https://wiki.xnat.org/display/XAPI/DICOM+Dump+Service+API>`_

        :param list fields: Fields to filter for DICOM tags. It can either a tag name or tag number in the format GGGGEEEE (G = Group number, E = Element number)
        :return: JSON object (dict) representation of DICOM header
        :rtype: dict
        """
        experiment = self.xnat_session.create_object(f"/data/experiments/{self.image_session_id}")

        uri = "/archive/projects/{}/experiments/{}/scans/{}".format(
            experiment.project,
            self.image_session_id,
            self.id,
        )
        return self.xnat_session.services.dicom_dump(src=uri, fields=fields)

    def read_dicom(self, file=None, read_pixel_data=False, force=False):
        if not PYDICOM_LOADED:
            raise RuntimeError("Cannot read DICOM, missing required dependency: pydicom")

        dicom_resource = self.resources.get("DICOM", self.resources.get("secondary"))

        if dicom_resource is None:
            raise ValueError("Scan {} does not contain a DICOM resource!".format(self))

        if file is None:
            dicom_files = sorted(dicom_resource.files.values(), key=lambda x: x.path)
            file = dicom_files[0]
        else:
            if file not in dicom_resource.files.values():
                raise ValueError("File {} not part of scan {} DICOM resource".format(file, self))

        with file.open() as dicom_fh:
            dicom_data = pydicom.dcmread(dicom_fh, stop_before_pixels=not read_pixel_data, force=force)

        return dicom_data

    @property
    @caching
    def data_dir(self):
        if self.xnat_session.mount_data_dir is None:
            return None

        parent = self.xnat_session.create_object(self.uri.split("/scans/")[0])

        if parent.data_dir is None:
            return None

        data_dir = f"{parent.data_dir}/SCANS/{self.id}"

        if not os.path.isdir(data_dir):
            self.logger.info(f"Determined data_dir to be {data_dir}, but it does not exist!")
            return None

        return data_dir


class AbstractResource(XNATBaseObject):
    SECONDARY_LOOKUP_FIELD = "label"

    def __init__(
        self,
        uri=None,
        xnat_session=None,
        id_=None,
        datafields=None,
        parent=None,
        fieldname=None,
        overwrites=None,
        data_dir=None,
        upload_method=None,
        **kwargs,
    ):

        super(AbstractResource, self).__init__(
            uri=uri,
            xnat_session=xnat_session,
            id_=id_,
            datafields=datafields,
            parent=parent,
            fieldname=fieldname,
            overwrites=overwrites,
            **kwargs,
        )

        if data_dir is not None:
            self.upload_dir(data_dir, method=upload_method)

    @classmethod
    def create_cache_id(cls, uri, fieldname, data):
        return cls.__name__, data["id_"]

    @property
    def cache_id(self):
        return type(self).__name__, self.id

    @property
    @caching
    def fulldata(self):
        # Ugly hack because direct query fails, we retrieve the parent listing data instead and filter from there
        uri, label = self.uri.rsplit("/", 1)
        data = self.xnat_session.get_json(uri)["ResultSet"]["Result"]

        # First try to retrieve by id
        try:
            data = next(x for x in data if x.get("xnat_abstractresource_id") == label)
        except StopIteration:
            # Then try to retrieve by label
            try:
                data = next(x for x in data if x.get("label") == label)
            except StopIteration:
                raise ValueError("Cannot find full data!")

        data["ID"] = data["xnat_abstractresource_id"]  # Make sure the ID is present
        return data

    @property
    def data(self):
        return self.fulldata

    @property
    def file_size(self) -> int:
        file_size = self.data["file_size"]
        if file_size.strip() == "":
            return 0
        else:
            return int(file_size)

    @property
    def file_count(self) -> int:
        file_count = self.data["file_count"]
        if file_count.strip() == "":
            return 0
        else:
            return int(file_count)

    def refresh_catalog(self):
        """
        Call refresh catalog on this object, see :py:meth:`xnat.services.Services.refresh_catalog` for details.
        """
        self.xnat_session.services.refresh_catalog(self)

    @property
    @caching
    def files(self):
        return XNATListing(
            self.uri + "/files",
            xnat_session=self.xnat_session,
            parent=self,
            field_name="files",
            secondary_lookup_field="Name",
            xsi_type="xnat:fileData",
        )

    def download(self, path, verbose=True):
        self.xnat_session.download_zip(self.uri + "/files", path, verbose=verbose)

    def download_dir(self, target_dir, verbose=True, flatten_dirs=False):
        """
        Download the entire resource and unpack it in a given directory

        :param str target_dir: directory to unpack to
        :param bool verbose: show progress
        """
        with tempfile.TemporaryFile() as temp_path:
            self.xnat_session.download_stream(self.uri + "/files", temp_path, format="zip", verbose=verbose)

            with ZipFile(temp_path) as zip_file:
                zip_file.extractall(target_dir)
                extracted_files = zip_file.namelist()

            extraction_sub_directories = [
                os.path.dirname(os.path.normpath(i_extracted_file)) for i_extracted_file in extracted_files
            ]
            unique_extraction_sub_directories = list(set(extraction_sub_directories))
            # Check if we have multiple resources
            multiple_resources = len(unique_extraction_sub_directories) > 1

            if flatten_dirs:
                for i_extracted_file in extracted_files:
                    new_resource_path = target_dir
                    if multiple_resources:
                        # With multiple resources we keep the subfolder
                        new_resource_path = os.path.join(
                            new_resource_path, os.path.basename(os.path.dirname(os.path.normpath(i_extracted_file)))
                        )
                    if not os.path.exists(new_resource_path):
                        os.makedirs(new_resource_path)

                    new_resource_path = os.path.join(
                        new_resource_path, os.path.basename(os.path.normpath(i_extracted_file))
                    )

                    shutil.move(os.path.join(target_dir, i_extracted_file), new_resource_path)

                # Remove the original download directory
                root_extraction_sub_dir = os.path.join(
                    target_dir, os.path.normpath(extraction_sub_directories[0]).split(os.sep)[0]
                )
                shutil.rmtree(root_extraction_sub_dir)
                scan_directory = target_dir
            else:
                if multiple_resources:
                    scan_directory = os.path.join(
                        target_dir, os.path.dirname(os.path.normpath(unique_extraction_sub_directories[0]))
                    )
                else:
                    scan_directory = os.path.join(target_dir, unique_extraction_sub_directories[0])

        if verbose:
            self.logger.info("Downloaded resource path to {}".format(scan_directory))
        return scan_directory

    def upload(
        self,
        path: Union[str, Path],
        remotepath: str,
        overwrite: bool = False,
        extract: bool = False,
        file_content: Optional[str] = None,
        file_format: Optional[str] = None,
        file_tags: Optional[str] = None,
        **kwargs,
    ):
        """
        Upload a file as an XNAT resource.

        :param path: The path to the file to upload
        :param remotepath: The remote path to which to upload to
        :param overwrite: Flag to force overwriting of files
        :param extract: Extract the files on the XNAT server
        :param file_content: Set the Content of the file on XNAT
        :param file_format: Set the format of the file on XNAT
        :param file_tags: Set the tags of the file on XNAT
        """
        uri = f"{self.uri}/files/{remotepath.lstrip('/')}"
        query = {}

        if extract:
            query["extract"] = "true"
        if file_content is not None:
            query["content"] = file_content
        if file_format is not None:
            query["format"] = file_format
        if file_tags is not None:
            query["tags"] = file_tags

        self.xnat_session.upload_file(uri, path=path, overwrite=overwrite, query=query, **kwargs)
        self.files.clearcache()

    def upload_data(
        self,
        data: Union[str, bytes, IO],
        remotepath: str,
        overwrite: bool = False,
        extract: bool = False,
        file_content: Optional[str] = None,
        file_format: Optional[str] = None,
        file_tags: Optional[str] = None,
        **kwargs,
    ):
        """
        Upload a file as an XNAT resource.

        :param str data: The data to upload, either a str, bytes or an IO object
        :param str remotepath: The remote path to which to uploadt
        :param bool overwrite: Flag to force overwriting of files
        :param bool extract: Extract the files on the XNAT server
        :param str file_content: Set the Content of the file on XNAT
        :param str file_format: Set the format of the file on XNAT
        :param str file_tags: Set the tags of the file on XNAT
        """
        uri = f"{self.uri}/files/{remotepath.lstrip('/')}"
        query = {}

        if extract:
            query["extract"] = "true"
        if file_content is not None:
            query["content"] = file_content
        if file_format is not None:
            query["format"] = file_format
        if file_tags is not None:
            query["tags"] = file_tags

        if isinstance(data, (str, bytes)):
            self.xnat_session.upload_string(uri, data=data, overwrite=overwrite, query=query, **kwargs)
        else:
            self.xnat_session.upload_stream(uri, stream=data, overwrite=overwrite, query=query, **kwargs)

        self.files.clearcache()

    def upload_dir(self, directory: Union[str, Path], overwrite: bool = False, method: str = "tgz_file", **kwargs):
        """
        Upload a directory to an XNAT resource. This means that if you do
        resource.upload_dir(directory) that if there is a file directory/a.txt
        it will be uploaded to resource/files/a.txt

        The method has 5 options, default is tgz_file:

        #. ``per_file``: Scans the directory and uploads file by file
        #. ``tar_memory``: Create a tar archive in memory and upload it in one go
        #. ``tgz_memory``: Create a gzipped tar file in memory and upload that
        #. ``tar_file``: Create a temporary tar file and upload that
        #. ``tgz_file``: Create a temporary gzipped tar file and upload that

        The considerations are that sometimes you can fit things in memory so
        you can save disk IO by putting it in memory. The per file does not
        create additional archives, but has one request per file so might be
        slow when uploading many files.

        :param directory: The directory to upload
        :param overwrite: Flag to force overwriting of files
        :param method: The method to use
        """
        if not isinstance(directory, Path):
            directory = Path(directory)

        if not directory.is_dir():
            raise exceptions.XNATValueError(f"The argument directory {directory} is not a path to a valid directory")

        # Make sure that a None or empty string is replaced by the default
        method = method or "tgz_file"

        if method == "per_file":
            for file_path in directory.rglob("*"):
                if os.path.getsize(file_path) == 0:
                    continue

                target_path = str(file_path.relative_to(directory))
                self.upload(file_path, target_path, overwrite=overwrite, **kwargs)
        elif method == "tar_memory":
            fh = BytesIO()
            with tarfile.open(mode="w", fileobj=fh) as tar_file:
                tar_file.add(directory, "")
            fh.seek(0)
            self.upload_data(fh, "upload.tar", overwrite=overwrite, extract=True, **kwargs)
            fh.close()
        elif method == "tgz_memory":
            fh = BytesIO()
            with tarfile.open(mode="w:gz", fileobj=fh) as tar_file:
                tar_file.add(directory, "")

            fh.seek(0)
            self.upload_data(fh, "upload.tar.gz", overwrite=overwrite, extract=True, **kwargs)
            fh.close()
        elif method == "tar_file":
            # Max-size is 256 MB
            with tempfile.SpooledTemporaryFile(max_size=268435456, mode="wb+") as fh:
                with tarfile.open(mode="w", fileobj=fh) as tar_file:
                    tar_file.add(directory, "")
                fh.seek(0)
                self.upload_data(fh, "upload.tar", overwrite=overwrite, extract=True, **kwargs)
        elif method == "tgz_file":
            # Max-size is 256 MB
            with tempfile.SpooledTemporaryFile(max_size=268435456, mode="wb+") as fh:
                with tarfile.open(mode="w:gz", fileobj=fh) as tar_file:
                    tar_file.add(directory, "")

                fh.seek(0)
                self.upload_data(fh, "upload.tar.gz", overwrite=overwrite, extract=True, **kwargs)
        else:
            self.logger.warning("Selected invalid upload directory method!")

    @property
    def parent_obj(self):
        return self.xnat_session.create_object(self.uri.split("/resources/")[0])

    @property
    @caching
    def data_dir(self):
        if self.xnat_session.mount_data_dir is None:
            return None

        parent = self.parent_obj

        if parent.data_dir is None:
            return None

        if isinstance(parent, ProjectData):
            data_dir = f"{parent.data_dir}/resources/{self.label}"
        elif isinstance(parent, SubjectData):
            data_dir = (
                f"{self.xnat_session.mount_data_dir}/projects/{parent.project}/subjects/{parent.label}/{self.label}"
            )
        elif isinstance(parent, ExperimentData):
            data_dir = f"{parent.data_dir}/RESOURCES/{self.label}"
        else:
            data_dir = f"{parent.data_dir}/{self.format}"

        if not os.path.isdir(data_dir):
            self.logger.info(f"Determined data_dir to be {data_dir}, but it does not exist!")
            return None

        return data_dir
