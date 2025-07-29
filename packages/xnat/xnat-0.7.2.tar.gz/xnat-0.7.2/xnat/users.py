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

from collections.abc import Mapping

from . import exceptions
from .core import caching


class Users(Mapping):
    """
    Listing of the users on the connected XNAT installation
    """

    def __init__(self, xnat_session, path="/data/users"):
        # cache fields
        self._cache = {}
        self._caching = True
        self.path = path

        # keep session available
        self._xnat_session = xnat_session

    def __repr__(self):
        return "Users:\n------\n{}".format("\n".join(str(x) for x in self.data.values()))

    def __getitem__(self, item):
        return self.data[item]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for x in self.data:
            yield x

    @property
    def xnat_session(self):
        return self._xnat_session

    @property
    @caching
    def data(self):
        try:
            users = self.xnat_session.get_json(self.path, accepted_status=[200, 403])["ResultSet"]["Result"]
        except exceptions.XNATResponseError as exception:
            if exception.status_code == 403:
                users = []
            else:
                raise
        return {x["login"]: User(x) for x in users}

    @property
    def caching(self) -> bool:
        if self._caching is not None:
            return self._caching
        else:
            return self.xnat_session.caching

    def clearcache(self):
        self._cache.clear()


class User(object):
    """
    Representation of a user on the connected XNAT systen
    """

    def __init__(self, data):
        self._fulldata = data

    def __repr__(self) -> str:
        return "<User {}>".format(self.login)

    def __str__(self) -> str:
        if self.access_level:
            return f"{self.login} ({self.access_level})"
        else:
            return self.login

    @property
    def data(self):
        return self._fulldata

    @property
    def id(self):
        """
        The id of the user
        """
        return self.data.get("xdat_user_id", None)

    @property
    def login(self):
        """
        The login name of the user
        """
        return self.data["login"]

    @property
    def access_level(self):
        return self.data.get("displayname", None)

    @property
    def group(self):
        return self.data.get("GROUP_ID", None)

    @property
    def email(self):
        """
        The email of the user
        """
        return self.data["email"]

    @property
    def first_name(self):
        """
        The first name of the user
        """
        return self.data["firstname"]

    @property
    def last_name(self):
        """
        The last name of the user
        """
        return self.data["lastname"]
