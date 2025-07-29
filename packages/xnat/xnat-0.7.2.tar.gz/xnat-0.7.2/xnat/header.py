#  Copyright 2011-2025 Biomedical Imaging Group Rotterdam, Departments of
#  Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
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

from __future__ import absolute_import, unicode_literals

import os
import tempfile  # Needed by generated code
from gzip import GzipFile  # Needed by generated code
from io import BytesIO  # Needed by generated code
from tarfile import TarFile  # Needed by generated code
from zipfile import ZipFile  # Needed by generated code

from xnat import mixin, search
from xnat.core import (
    XNATListing,
    XNATNestedObject,
    XNATObject,
    XNATSimpleListing,
    XNATSubListing,
    XNATSubObject,
    caching,
)
from xnat.utils import RequestsFileLike, mixedproperty

try:
    PYDICOM_LOADED = True
    import pydicom
except ImportError:
    PYDICOM_LOADED = False

SESSION = None


def current_session():
    return SESSION


# These mixins are to set the xnat_session automatically in all created classes
class XNATObjectMixin(XNATObject):
    @mixedproperty
    def xnat_session(self):
        return current_session()

    @classmethod
    def query(cls, *constraints) -> search.Query:
        query = search.Query(cls, cls.xnat_session)

        # Add in constraints immediatly
        if len(constraints) > 0:
            query = query.filter(*constraints)

        return query


class XNATNestedObjectMixin(XNATNestedObject):
    @mixedproperty
    def xnat_session(self):
        return current_session()


class XNATSubObjectMixin(XNATSubObject):
    @mixedproperty
    def xnat_session(self):
        return current_session()


class FileData(XNATObjectMixin):
    SECONDARY_LOOKUP_FIELD = "$FILE_SECONDARY_LOOKUP"
    _XSI_TYPE = "xnat:fileData"

    def __init__(
        self,
        uri=None,
        xnat_session=None,
        id_=None,
        datafields=None,
        parent=None,
        fieldname=None,
        overwrites=None,
        name=None,
    ):
        super(FileData, self).__init__(
            uri=uri,
            xnat_session=xnat_session,
            id_=id_,
            datafields=datafields,
            parent=parent,
            fieldname=fieldname,
            overwrites=overwrites,
        )

        # Save path (that functions as id) because we need it if cache gets wiped
        self._path = id_

        if name is not None:
            self._name = name

    @mixedproperty
    def parent(cls):
        return cls._PARENT_CLASS

    @parent.getter
    def parent(self):
        if self._parent is None:
            # Default is just stripping last 2 parts of the uri
            parent_uri = self.fulluri.split("/files/", 1)[0]
            self._parent = self.xnat_session.create_object(parent_uri)
        return self._parent

    @property
    def id(self):
        return self._path

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    def delete(self):
        self.xnat_session.delete(self.uri)

    def download(self, *args, **kwargs):
        self.xnat_session.download(self.uri, *args, expected_md5_digest=self.digest, **kwargs)

    def download_stream(self, *args, **kwargs):
        self.xnat_session.download_stream(self.uri, *args, expected_md5_digest=self.digest, **kwargs)

    def open(self):
        data_path = self.data_path

        if data_path is not None:
            self.logger.info("Opening file from filesystem!")
            return open(data_path, "rb")
        else:
            self.logger.info("Opening file over http!")

        uri = self.xnat_session._format_uri(self.uri)
        request = self.xnat_session.interface.get(uri, stream=True)
        return RequestsFileLike(request)

    @property
    @caching
    def fulldata(self):
        # Find the url of the parent listing by splitting on /files/ (most left split)
        listing_uri = self.uri.split("/files/", 1)[0] + "/files"
        data = self.xnat_session.get_json(listing_uri)
        data = data["ResultSet"]["Result"]
        item = next(x for x in data if x["URI"] == self.uri)
        return item

    @property
    def data(self):
        return self.fulldata

    @property
    def cat_id(self):
        return self.get("cat_ID", str)

    @property
    def collection(self):
        return self.get("collection", str)

    @property
    def digest(self):
        return self.get("digest", str)

    @property
    def file_content(self):
        return self.get("file_content", str)

    @property
    def file_format(self):
        return self.get("file_format", str)

    @property
    def file_tags(self):
        return self.get("file_tags", str)

    @property
    def file_size(self):
        return self.get("Size", str)

    @property
    @caching
    def size(self):
        response = self.xnat_session.head(self.uri, allow_redirects=True)
        return response.headers["Content-Length"]

    @property
    @caching
    def data_path(self):
        if self.xnat_session.mount_data_dir is None:
            return None

        parent = self.xnat_session.create_object(self.uri.split("/files/")[0])

        if parent.data_dir is None:
            return None

        data_path = f"{parent.data_dir}/{self.path}"

        if not os.path.exists(data_path):
            self.logger.info(f"Determined data_path to be {data_path}, but it does not exist!")
            return None

        return data_path


# Empty class lookup to place all new lookup values
XNAT_CLASS_LOOKUP = {
    "xnat:fileData": FileData,
}


# The following code represents the data structure of the XNAT server
# It is automatically generated using
# $SCHEMAS
