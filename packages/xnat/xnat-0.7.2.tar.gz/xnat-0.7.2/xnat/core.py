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

import csv
import datetime
import fnmatch
import io
import keyword
import re
from abc import ABCMeta, abstractmethod
from collections import OrderedDict, namedtuple
from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from functools import update_wrapper
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from . import exceptions
from .constants import ALL_REST_SHORTCUT_NAMES, DATA_FIELD_HINTS, REST_SHORTCUTS, TYPE_HINTS
from .datatypes import convert_from, convert_to
from .search import SearchField
from .type_hints import JSONType, TimeoutType
from .utils import get_close_matches_icase, mixedproperty, parse_datetime, pythonize_attribute_name

try:
    import pandas

    PANDAS_AVAILABLE = True
except ImportError:
    pandas = None
    PANDAS_AVAILABLE = False

if TYPE_CHECKING:
    from .session import BaseXNATSession


def caching(func) -> Callable:
    """
    This decorator caches the value in self._cache to avoid data to be
    retrieved multiple times. This works for properties or functions without
    arguments.
    """
    name = func.__name__

    def wrapper(self):
        # We use self._cache here, in the decorator _cache will be a member of
        #  the objects, so nothing to worry about
        # pylint: disable=protected-access
        if not self.caching or name not in self._cache:
            # Compute the value if not cached
            self._cache[name] = func(self)

        return self._cache[name]

    update_wrapper(wrapper, func)
    return wrapper


class CustomVariableMap(Mapping):
    def __init__(self, parent):
        # Caching targets
        self._cache = {}
        self._caching = None

        # Set import information
        self.parent = parent

        # TODO: Fix the xsi type in this request when trying to change field datatype
        # sandboxhakim?xsiType=xnatpy:fieldDefinitionGroupFields&xnat:projectData/studyProtocol[ID=sandboxhakim_xnat_mrSessionData]/definitions[None=1]/fields/field[name=test]/datatype=integer
        #              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                                ^^^^^^
        #                This is the problem due to xsi mess                                                                                     and xpath mess with index

    def __repr__(self) -> str:
        return "<CustomVariableMap groups: [{}]>".format(", ".join(self.definitions.keys()))

    def __getitem__(self, item: str):
        return self.definitions[item]

    def __iter__(self):
        for key in self.definitions:
            yield key

    def __len__(self) -> int:
        return len(self.definitions)

    # The next 3 cache properties are to avoid a loop on object creation for Projects (it would try to self-reference)
    # by lazy loading these properties, we ensure the project object is fully created before referencing it
    @property
    @caching
    def project(self):
        return self.parent.xnat_session.projects[self.parent.project]

    @property
    @caching
    def protocol(self):
        protocol_name = "{}_{}".format(self.project.id, self.parent.__xsi_type__.replace(":", "_"))
        if protocol_name in self.project.study_protocol.key_map:
            return self.project.study_protocol[protocol_name]
        else:
            return None

    @property
    @caching
    def definitions(self):
        if self.protocol is None:
            return {}

        definitions = {}
        for definition in self.protocol.definitions.values():
            definitions[definition.id] = CustomVariableGroup(parent=self.parent, definition=definition)

        return definitions

    @property
    def fields(self):
        return self.parent.fields

    @property
    def caching(self) -> bool:
        if self._caching is not None:
            return self._caching
        else:
            return self.parent.xnat_session.caching

    def clearcache(self):
        self._cache.clear()


class CustomVariableGroup(MutableMapping):
    def __init__(self, parent, definition):
        self.definition = definition
        self.parent = parent
        self.fields = {}

        for key, value in definition.fields.items():
            self.fields[key] = CustomVariableDef(
                name=value.name, datatype=value.datatype, options=value.possible_values.listing
            )

    def __repr__(self) -> str:
        return "<CustomVariableGroup {} {{{}}}>".format(
            self.definition.id,
            ", ".join("{} ({}): {!r}".format(x.name, x.datatype, self[x.name]) for x in self.fields.values()),
        )

    def __getitem__(self, key: str):
        field = self.fields[key]
        value = self.parent.fields.get(key)

        if value is None:
            return None

        # Check type and convert
        value = convert_to(value, "xs:{}".format(field.datatype))

        return value

    def __setitem__(self, key: str, value):
        field = self.fields[key]
        value = convert_from(value, "xs:{}".format(field.datatype))

        if field.options and value not in field.options:
            raise exceptions.XNATValueError(
                "Cannot set custom variable, value should be one of {}, found {}".format(field.options, value)
            )

        self.parent.fields[key] = value

    def __delitem__(self, key: str):
        self.parent.logger.warning("Deletion of custom variable is not possible!")

    def __iter__(self) -> str:
        for field in self.fields.keys():
            yield field

    def __len__(self) -> int:
        return len(self.fields)

    @property
    def name(self) -> str:
        return self.definition.id


class CustomVariableDef:
    def __init__(self, name: str, datatype: str, options: Optional[List[str]]):
        self.name: str = name
        self.datatype: str = datatype
        self.options: Optional[List[str]] = options


class XNATBaseObject(metaclass=ABCMeta):
    SECONDARY_LOOKUP_FIELD = None
    FROM_SEARCH_URI = None
    DEFAULT_SEARCH_FIELDS = None
    _DISPLAY_IDENTIFIER = None
    _HAS_FIELDS = False
    _CONTAINED_IN = None
    _XSI_TYPE: str = "xnat:baseObject"
    _PARENT_CLASS = None
    _FIELD_NAME = None

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
        if (uri is None or xnat_session is None) and parent is None:
            raise exceptions.XNATValueError("Either the uri and xnat session have to be given, or the parent object")

        # Set the xnat session
        self._cache = {}
        self._caching = None

        # This is the object creation branch
        if uri is None and parent is not None:
            # This is the creation of a new object in the XNAT server
            self._xnat_session = parent.xnat_session
            if isinstance(parent, XNATListing):
                pass
            elif self._CONTAINED_IN is not None:
                parent = getattr(parent, self._CONTAINED_IN)
            else:
                self.logger.debug(f"parent {parent}, self._CONTAINED_IN: {self._CONTAINED_IN}")
                raise exceptions.XNATValueError("Cannot determine PUT url!")

            # Check what argument to use to build the URL
            if self._DISPLAY_IDENTIFIER is not None:
                secondary_lookup_attribute = pythonize_attribute_name(self._DISPLAY_IDENTIFIER)
            elif self.SECONDARY_LOOKUP_FIELD is not None:
                secondary_lookup_attribute = self.SECONDARY_LOOKUP_FIELD
            else:
                raise exceptions.XNATValueError(
                    "Cannot figure out correct object creation url for <{}>, "
                    "creation currently not supported!".format(type(self).__name__)
                )

            # Get extra required url part
            secondary_lookup_value = kwargs.get(secondary_lookup_attribute)

            if secondary_lookup_value is None:
                raise exceptions.XNATValueError(
                    "The {} for a {} need to be specified on creation".format(
                        secondary_lookup_attribute, self.__xsi_type__
                    )
                )
            else:
                self.logger.debug(
                    f"Found secondary lookup value: [{type(secondary_lookup_value)}] {secondary_lookup_value}"
                )

            uri = self._get_creation_uri(parent_uri=parent.uri, id_=id_, secondary_lookup_value=secondary_lookup_value)
            self.logger.debug("PUT URI: {}".format(uri))
            query = {
                "xsiType": self.__xsi_type__,
                "req_format": "qs",
            }

            # Add all kwargs to query with correct xpath to set the fields
            for name, value in kwargs.items():
                xpath = "{}/{}".format(self.xpath, name)
                query[xpath] = value

            self.logger.debug("query: {}".format(query))
            result = self.xnat_session.put(uri, query=query)
            self.logger.debug("PUT RESULT: [{}] {}".format(result.status_code, result.text))
            result_text = result.text.strip()

            # This should be the ID of the newly created object, which is safer than
            # labels that can contain weird characters and break stuff
            if result_text:
                uri = "{}/{}".format(parent.uri, result_text)
                self.logger.debug("UPDATED URI BASED ON RESPONSE: {}".format(uri))

            # Clear parent cache
            parent.clearcache()

            # Parent is no longer needed after creation
            self._uri = uri
            self._parent = None

            # Add url part to overwrites (it should be safe) but rest should be retrieved from server to be sure
            # the creation went correctly
            self._overwrites = overwrites or {}
            self._overwrites[secondary_lookup_attribute] = secondary_lookup_value
        else:
            # This is the creation of a Python proxy for an existing XNAT object
            self._uri = uri
            self._parent = parent

            # Cache the kwargs in the object already
            self._overwrites = overwrites or {}
            self._overwrites.update(kwargs)

        self._xnat_session = xnat_session
        self._fieldname = fieldname

        if self._HAS_FIELDS:
            self.custom_variables = CustomVariableMap(parent=self)

        if id_ is not None:
            self._cache["id"] = id_

        if datafields:
            self._cache["data"] = datafields

    def _get_creation_uri(self, parent_uri, id_, secondary_lookup_value):
        return f"{parent_uri}/{secondary_lookup_value}"

    def __str__(self) -> str:
        if self.SECONDARY_LOOKUP_FIELD is None:
            return f"<{self.__class__.__name__} {self.id}>"
        else:
            return f"<{self.__class__.__name__} {getattr(self, self.SECONDARY_LOOKUP_FIELD)} ({self.id})>"

    def __repr__(self) -> str:
        return str(self)

    @property
    @abstractmethod
    def xpath(self) -> str:
        """
        The xpath of the object as seen from the root of the data. Used for
        setting fields in the object.
        """

    @classmethod
    def create_cache_id(cls, uri, fieldname, data):
        return cls.__name__, uri

    @property
    def cache_id(self):
        return type(self).__name__, self.uri

    @mixedproperty
    def parent(cls):
        return cls._PARENT_CLASS

    @parent.getter
    def parent(self):
        if self._parent is None:
            # Default is just stripping last 2 parts of the uri
            parent_uri = self.fulluri.rsplit("/", 2)[0]
            self._parent = self.xnat_session.create_object(parent_uri)
        return self._parent

    @mixedproperty
    def rest_shortcuts(cls):
        xsi_types = set(x.__xsi_type__ for x in cls.mro() if issubclass(x, XNATBaseObject))

        shortcuts = {}
        for xsi_type in xsi_types:
            shortcuts.update(REST_SHORTCUTS.get(xsi_type, {}))
        return shortcuts

    @property
    def logger(self):
        return self.xnat_session.logger

    @mixedproperty
    def fieldname(self) -> Union[str, int]:
        return self._FIELD_NAME

    @fieldname.getter
    def fieldname(self) -> Union[str, int]:
        return self._fieldname

    def get(self, name, type_=None):
        try:
            value = self._overwrites[name]
        except KeyError:
            value = self.data.get(name)

        if type_ is not None and value is not None:
            if isinstance(type_, str):
                value = convert_to(value, type_)
            else:
                value = type_(value)
        return value

    def get_object(self, fieldname, type_=None):
        try:
            data = next(x for x in self.fulldata.get("children", []) if x["field"] == fieldname)["items"]
            data = next(x for x in data if not x["meta"]["isHistory"])  # Filter out the non-history item
            type_ = data["meta"]["xsi:type"]
        except StopIteration:
            if type_ is None:
                type_ = TYPE_HINTS.get(fieldname, None)

        if type_ is None:
            raise exceptions.XNATValueError("Cannot determine type of field {}!".format(fieldname))

        cls = self.xnat_session.XNAT_CLASS_LOOKUP[type_]

        if not issubclass(cls, (XNATSubObject, XNATNestedObject)):
            raise ValueError("{} is not a subobject type!".format(cls))

        return self.xnat_session.create_object(self.uri, type_=type_, parent=self, fieldname=fieldname)

    @property
    def fulluri(self) -> str:
        return self.uri

    def external_uri(self, query: Dict[str, str] = None, scheme: str = None) -> str:
        """
        Return the external url for this object, not just a REST path

        :param query: extra query string parameters
        :param scheme: scheme to use (when not using original url scheme)
        :return: external url for this object
        """
        return self.xnat_session.url_for(self, query=query, scheme=scheme)

    def _resolve_xsi_type(self) -> str:
        parent = self
        while not isinstance(parent, XNATObject):
            parent = parent.parent
        return parent.__xsi_type__

    def mset(self, values: Dict[str, str] = None, timeout: TimeoutType = None, **kwargs):
        if not isinstance(values, dict):
            values = kwargs

        xsi_type = self._resolve_xsi_type()

        # Add xpaths to query
        query = {"xsiType": xsi_type}
        for name, value in values.items():
            xpath = "{}/{}".format(self.xpath, name)
            query[xpath] = value

        self.xnat_session.put(self.fulluri, query=query, timeout=timeout)
        self.clearcache()
        if hasattr(self.parent, "clearcache"):
            self.parent.clearcache()

    def set(
        self,
        name: str,
        value: Any,
        type_: Optional[Union[str, Callable[[Any], str]]] = None,
        timeout: TimeoutType = None,
    ):
        """
        Set a field in the current object

        :param str name: name of the field
        :param value:  value to set
        :param type_: type of the field
        :param timeout: time for the set request
        """
        if type_ is not None:
            if isinstance(type_, str):
                # Make sure we have a valid string here that is properly casted
                value = convert_from(value, type_)
            else:
                value = type_(value)

        self.mset({name: value}, timeout=timeout)

    def del_(self, name: str):
        self.mset({name: "NULL"})

    @mixedproperty
    def __xsi_type__(self) -> str:
        return self._XSI_TYPE

    @mixedproperty
    def id(cls):
        return SearchField(cls, "ID", "xs:string")

    @id.getter
    @caching
    def id(self) -> str:
        object_id = self.data.get("ID", None)
        if object_id is not None:
            return object_id
        elif self.parent is not None:
            return "{}/{}".format(self.parent.id, self.fieldname)
        elif hasattr(self, "_DISPLAY_IDENTIFIER") and self._DISPLAY_IDENTIFIER is not None:
            return getattr(self, self._DISPLAY_IDENTIFIER)
        else:
            return "#NOID#"

    @property
    @abstractmethod
    def data(self) -> JSONType:
        """
        The data of the current object (data fields only)
        """

    @property
    @abstractmethod
    def fulldata(self) -> JSONType:
        """
        The full data of the current object (incl children, meta etc)
        """

    @property
    def xnat_session(self) -> "BaseXNATSession":
        if self._uri is None:
            raise exceptions.XNATObjectDestroyedError("This object is delete and cannot be used anymore!")

        return self._xnat_session

    @property
    def uri(self) -> str:
        if self._uri is None:
            raise exceptions.XNATObjectDestroyedError("This object is delete and cannot be used anymore!")

        return self._uri

    def clearcache(self):
        self._overwrites.clear()
        self._cache.clear()

    # This needs to be at the end of the class because it shadows the caching
    # decorator for the remainder of the scope.
    @property
    def caching(self) -> bool:
        if self._caching is not None:
            return self._caching
        else:
            return self.xnat_session.caching

    @caching.setter
    def caching(self, value):
        self._caching = value

    @caching.deleter
    def caching(self):
        self._caching = None

    def delete(self, remove_files: bool = True):
        """
        Remove the item from XNATSession
        """
        query = {}

        if remove_files:
            query["removeFiles"] = "true"

        # Try to remove object thoroughly
        self.xnat_session.delete(self.fulluri, query=query)
        self.xnat_session.remove_object(self)
        self._uri = None
        self._xnat_session = None
        self._insert_date = None

        # Make sure there is no cache, this will cause XNATObjectDestroyedError on subsequent use
        # of this object, indicating that is has been in fact removed
        self.clearcache()


class XNATObject(XNATBaseObject):
    @property
    @caching
    def fulldata(self) -> JSONType:
        data = self.xnat_session.get_json(self.uri)["items"]

        # Determine original insert data (oldest entry)
        insert_date = [parse_datetime(x["meta"]["start_date"]) for x in data if x["meta"].get("start_date")]
        if insert_date:
            insert_date = min(insert_date)
        else:
            insert_date = None

        # Collect data and insert extra field
        data = next(x for x in data if not x["meta"]["isHistory"])
        data["xnatpy"] = {"insert_date": insert_date}
        return data

    @property
    def data(self) -> JSONType:
        return self.fulldata["data_fields"]

    @property
    def xpath(self) -> str:
        return "{}".format(self.__xsi_type__)

    @property
    def is_history(self) -> bool:
        return bool(self.fulldata["meta"]["isHistory"])

    @property
    def insert_date(self) -> datetime:
        return self.fulldata["xnatpy"]["insert_date"]


class XNATNestedObject(XNATBaseObject):
    @property
    def fulldata(self) -> JSONType:
        try:
            if isinstance(self.parent.fulldata, dict):
                data = next(x for x in self.parent.fulldata["children"] if x["field"] == self.fieldname)["items"]
                data = next(x for x in data if not x["meta"]["isHistory"])
            elif isinstance(self.parent.fulldata, list):
                if self.parent.secondary_lookup_field is not None:
                    data = next(
                        x
                        for x in self.parent.fulldata
                        if x["data_fields"][self.parent.secondary_lookup_field] == self.fieldname
                    )
                else:
                    # Just simply select the index
                    data = self.parent.fulldata[self.fieldname]
            else:
                raise ValueError("Found unexpected data in parent! ({})".format(self.parent.fulldata))

        except StopIteration:
            data = {"data_fields": {}}

        return data

    @property
    def data(self) -> JSONType:
        return self.fulldata["data_fields"]

    @property
    def uri(self) -> str:
        return self.parent.uri

    @property
    def xpath(self) -> str:
        if isinstance(self.parent, XNATBaseObject):
            return "{}/{}[@xsi:type={}]".format(self.parent.xpath, self.fieldname, self.__xsi_type__)
        elif isinstance(self.fieldname, int) or self.parent.secondary_lookup_field is None:
            return "{}[{}]".format(self.parent.xpath, self.fieldname + 1)
        else:
            return "{}[{}={}]".format(self.parent.xpath, self.parent.secondary_lookup_field, self.fieldname)

    def clearcache(self):
        super(XNATNestedObject, self).clearcache()
        self.parent.clearcache()


class XNATSubObject(XNATBaseObject):
    _PARENT_CLASS = None

    @property
    def uri(self) -> str:
        return self.parent.fulluri

    @mixedproperty
    def __xsi_type__(cls) -> str:
        parent = cls.parent
        while not issubclass(parent, XNATBaseObject):
            new_parent = parent.parent

            if new_parent is None:
                break

            parent = new_parent
        return parent.__xsi_type__

    @__xsi_type__.getter
    def __xsi_type__(self) -> str:
        parent = self.parent
        while not isinstance(parent, XNATBaseObject):
            parent = parent.parent
        return parent.__xsi_type__

    @property
    def xpath(self) -> str:
        if isinstance(self.parent, XNATBaseObject):
            # XPath is this plus fieldname
            return "{}/{}".format(self.parent.xpath, self.fieldname)
        elif isinstance(self.parent, XNATBaseListing):
            # XPath is an index in a list
            if isinstance(self.fieldname, int) or self.parent.secondary_lookup_field is None:
                return "{}[{}]".format(self.parent.xpath, self.fieldname + 1)
            else:
                return "{}[{}={}]".format(self.parent.xpath, self.parent.secondary_lookup_field, self.fieldname)
        else:
            raise TypeError("Type of parent is invalid! (Found {})".format(type(self.parent).__name__))

    @property
    def fulldata(self) -> JSONType:
        prefix = "{}/".format(self.fieldname)

        result = self.parent.fulldata

        if isinstance(result, dict):
            data_fields = {k[len(prefix) :]: v for k, v in result["data_fields"].items() if k.startswith(prefix)}
            children = [child for child in result["children"] if child["field"].startswith(prefix)]
            result = {
                "data_fields": data_fields,
                "children": children,
            }
        elif isinstance(result, list):
            try:
                if self.parent.secondary_lookup_field is not None:
                    result = next(
                        x for x in result if x["data_fields"][self.parent.secondary_lookup_field] == self.fieldname
                    )
                else:
                    result = result[self.fieldname]
            except (IndexError, KeyError):
                return {"data_fields": {}}
        else:
            raise ValueError("Found unexpected data in parent! ({})".format(result))

        return result

    @property
    def data(self) -> JSONType:
        return self.fulldata["data_fields"]

    def clearcache(self):
        super(XNATSubObject, self).clearcache()
        self.parent.clearcache()


class XNATBaseListing(Mapping, Sequence, metaclass=ABCMeta):
    __ALL_LISTINGS__ = []

    def __init__(
        self,
        parent: XNATBaseObject,
        field_name,
        secondary_lookup_field: Optional[str] = None,
        xsi_type: Optional[str] = None,
        **kwargs,
    ):
        # Cache fields
        self._cache = {}
        self._caching = None

        # Save the parent and field name
        self.parent = parent
        self.field_name = field_name

        # Copy parent xnat session for future use
        self._xnat_session = parent.xnat_session

        # Get the lookup field before type hints, they can ruin it for abstract types
        if secondary_lookup_field is None:
            if xsi_type is not None:
                secondary_lookup_field = self.xnat_session.XNAT_CLASS_LOOKUP.get(xsi_type).SECONDARY_LOOKUP_FIELD

        # Make it possible to override the xsi_type for the contents
        if self.field_name not in TYPE_HINTS:
            self._xsi_type = xsi_type
        else:
            self._xsi_type = TYPE_HINTS[field_name]

        # If Needed, try again
        if secondary_lookup_field is None and self._xsi_type is not None:
            secondary_lookup_field = self.xnat_session.XNAT_CLASS_LOOKUP.get(self._xsi_type).SECONDARY_LOOKUP_FIELD

        self.secondary_lookup_field = secondary_lookup_field

        # Register listing
        self.__ALL_LISTINGS__.append(self)

    def sanitize_name(self, name: str) -> str:
        name = re.sub("[^0-9a-zA-Z]+", "_", name)

        # Change CamelCaseString to camel_case_string
        # Note that addID would become add_id
        name = re.sub("[A-Z]+", lambda x: "_" + x.group(0).lower(), name)
        if name[0] == "_":
            name = name[1:]

        # Avoid multiple underscores (replace them by single underscore)
        name = re.sub("__+", "_", name)

        # Avoid overwriting keywords TODO: Do we want this, as a property it is not a huge problem?
        if keyword.iskeyword(name):
            name += "_"

        return name

    @property
    @abstractmethod
    def data_maps(self):
        """
        The generator function (should be cached) of all the data access
        properties. They are all generated from the same data, so their
        caching is shared.
        """

    @property
    def data(self):
        """
        The data mapping using the primary key
        """
        return self.data_maps[0]

    @property
    def key_map(self):
        """
        The data mapping using the secondary key
        """
        return self.data_maps[1]

    @property
    def non_unique_keys(self):
        """
        Set of non_unique keys
        """
        return self.data_maps[2]

    @property
    def listing(self):
        """
        The listing view of the data
        """
        return self.data_maps[3]

    def __str__(self) -> str:
        if self.secondary_lookup_field is not None:
            content = ", ".join(
                "({}, {}): {}".format(k, getattr(v, self.sanitize_name(self.secondary_lookup_field)), v)
                for k, v in self.items()
            )
            content = "{{{}}}".format(content)
        else:
            content = ", ".join(str(v) for v in self.values())
            content = "[{}]".format(content)
        return "<{} {}>".format(type(self).__name__, content)

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self.listing[item]

        try:
            return self.data[item]
        except KeyError:
            if item in self.non_unique_keys:
                raise KeyError(
                    "There are multiple items with that key in"
                    " this collection! To avoid problem you need"
                    " to use the ID."
                )
            try:
                return self.key_map[item]
            except KeyError:
                raise KeyError("Could not find ID/label {} in collection!".format(item))

    def __iter__(self):
        # Avoid re-requesting the data for every item
        for value in self.listing:
            yield value

    def __len__(self) -> int:
        return len(self.listing)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    @property
    @abstractmethod
    def uri(self) -> str:
        pass

    @property
    def logger(self):
        return self.parent.logger

    @property
    def xnat_session(self):
        return self._xnat_session

    def clearcache(self):
        self._cache.clear()

    # This needs to be at the end of the class because it shadows the caching
    # decorator for the remainder of the scope.
    @property
    def caching(self):
        if self._caching is not None:
            return self._caching
        else:
            return self.xnat_session.caching

    @caching.setter
    def caching(self, value):
        self._caching = value

    @caching.deleter
    def caching(self):
        self._caching = None

    # These two methods allow for wiping the cache of all listings that had obj in them
    # this is required for object deletions so that the objects are no longer presented
    # in the listings
    @classmethod
    def delete_item_from_listings(cls, obj):
        for listing in cls.__ALL_LISTINGS__:
            listing.delete_item_from_cache(obj)

    def delete_item_from_cache(self, obj):
        data_maps = self._cache.get("data_maps", None)

        if data_maps is None:
            return

        if obj in data_maps[0].values() or obj in data_maps[1].values() or obj in data_maps[3]:
            self.clearcache()


class XNATListing(XNATBaseListing):
    def __init__(self, uri: str, filter: Optional[Dict] = None, pass_datafields: bool = False, **kwargs):
        # Important for communication, needed before superclass is called
        self._uri = uri
        self._pass_datafields = pass_datafields

        super(XNATListing, self).__init__(**kwargs)

        # Manager the filters
        self._used_filters = filter or {}

    @property
    def uri(self) -> str:
        return self._uri

    @property
    @caching
    def data_maps(self):
        columns = "ID,URI"
        if self.secondary_lookup_field is not None:
            columns = "{},{}".format(columns, self.secondary_lookup_field)
        if self._xsi_type is None:
            columns += ",xsiType"

        query = dict(self.used_filters)
        query["columns"] = columns
        result = self.xnat_session.get_json(self.uri, query=query)

        try:
            result = result["ResultSet"]["Result"]
        except KeyError:
            raise exceptions.XNATValueError("Query GET from {} returned invalid data: {}".format(self.uri, result))

        for entry in result:
            if "URI" not in entry and "ID" not in entry:
                # HACK: This is a Resource, that misses the URI and ID field (let's fix that)
                if "xnat_abstractresource_id" in entry:
                    # This is a resource in the archive
                    entry["ID"] = entry["xnat_abstractresource_id"]
                else:
                    # This is a resource in the prearchive
                    entry["ID"] = entry["label"]
                entry["URI"] = "{}/{}".format(self.uri, entry["ID"])
            elif "ID" not in entry:
                # HACK: This is a File and it misses an ID field and has Name (let's fix that)
                entry["path"] = re.sub(r"^.*/resources/[^/]+/files/", "", entry["URI"], 1)
                entry["ID"] = entry["path"]
                entry["fieldname"] = type(self.parent).__name__
            else:
                entry["URI"] = "{}/{}".format(self.uri, entry["ID"])

        # Post filter result if server side query did not work
        if self.used_filters:
            result = [
                x for x in result if all(fnmatch.fnmatch(x[k], v) for k, v in self.used_filters.items() if k in x)
            ]

        # Create object dictionaries
        id_map = {}
        key_map = {}
        listing = []
        non_unique = {None}
        datafields = None
        for x in result:
            # HACK: xsi_type of resources is called element_name... yay!
            xsi_type = x.get("xsiType", x.get("element_name", self._xsi_type)).strip()
            if x["ID"].strip() == "" or xsi_type == "":
                self.logger.warning("Found empty object {}, skipping!".format(x.get("URI")))
                continue

            if self._pass_datafields:
                datafields = x

            if self.secondary_lookup_field is not None:
                secondary_lookup_value = x.get(self.secondary_lookup_field)
                # Note that if XNAT has the secondary_lookup field with a capital, we want it to be lowercase for
                # create object argument, as we like python-style names
                new_object = self.xnat_session.create_object(
                    x["URI"],
                    type_=xsi_type,
                    id_=x["ID"],
                    fieldname=x.get("fieldname"),
                    datafields=datafields,
                    **{self.secondary_lookup_field.lower(): secondary_lookup_value},
                )
                if secondary_lookup_value in key_map:
                    non_unique.add(secondary_lookup_value)
                key_map[secondary_lookup_value] = new_object
            else:
                new_object = self.xnat_session.create_object(
                    x["URI"], type_=xsi_type, id_=x["ID"], fieldname=x.get("fieldname"), datafields=datafields
                )

            listing.append(new_object)
            id_map[x["ID"]] = new_object

        return id_map, key_map, non_unique, listing

    def _tabulate(self, columns=None, filter=None):
        """
        Create a table (tuple of namedtuples) from this listing. It is possible
        to choose the columns and add a filter to the tabulation.

        :param tuple columns: names of the variables to use for columns
        :param dict filter: update filters to use (form of {'variable': 'filter*'}),
                             setting this option will try to merge the filters and
                             throw an error if that is not possible.
        :return: tabulated data
        :rtype: tuple
        :raises ValueError: if the new filters conflict with the object filters
        """
        if columns is None:
            columns = ("DEFAULT",)
        else:
            for column in columns:
                if column not in ALL_REST_SHORTCUT_NAMES:
                    options = get_close_matches_icase(column, ALL_REST_SHORTCUT_NAMES)
                    self.logger.warning(
                        f"Column {column} is not a valid REST shortcut, did you mean {', '.join(options)}"
                    )

        if filter is None:
            filter = self.used_filters
        else:
            filter = self.merge_filters(self.used_filters, filter)

        query = dict()
        query["columns"] = ",".join(columns)

        result = self.xnat_session.get_json(self.uri, query=query)
        result = result["ResultSet"]["Result"]

        if filter:
            result = [x for x in result if all(fnmatch.fnmatch(x[k], v) for k, v in filter.items() if k in x)]

        if len(result) > 0:

            result_columns = list(result[0].keys())

            # Retain requested order
            if columns != ("DEFAULT",):
                result_columns = [x for x in columns if x in result_columns]

            # Replace all non-alphanumeric characters with an underscore
            result_columns = [(s, re.sub("[^0-9a-zA-Z]+", "_", s)) for s in result_columns]

            # Replace all non-alphanumeric characters in each key of the keyword dictionary
            return tuple(
                OrderedDict([(result_column, x.get(source_column)) for source_column, result_column in result_columns])
                for x in result
            )
        else:
            return ()

    def tabulate(self, columns=None, filter=None):
        data = self._tabulate(columns=columns, filter=filter)

        if data:
            # Set the result type
            rowtype = namedtuple("TableRow", data[0].keys())

            # Replace all non-alphanumeric characters in each key of the keyword dictionary
            return tuple(rowtype(**x) for x in data)
        else:
            return ()

    def tabulate_csv(self, columns=None, filter=None, header=True):
        output = io.StringIO()
        data = self._tabulate(columns=columns, filter=filter)

        if not data:
            return ""

        writer = csv.DictWriter(output, data[0].keys())
        if header:
            writer.writeheader()

        for row in data:
            writer.writerow(row)
        result = output.getvalue()

        # FIXME: A context would be nicer, but doesn't work in Python 2.7
        output.close()
        return result

    def tabulate_pandas(self):
        if not PANDAS_AVAILABLE:
            raise ModuleNotFoundError("Cannot tabulate to pandas without pandas being installed!")
        csv_data = self.tabulate_csv()
        csv_data = io.StringIO(csv_data)
        return pandas.read_csv(csv_data)

    @property
    def used_filters(self):
        return self._used_filters

    @staticmethod
    def merge_filters(old_filters, extra_filters):
        # First check for conflicting filters
        for key in extra_filters:
            if key in old_filters and old_filters[key] != extra_filters[key]:
                raise ValueError(
                    "Trying to redefine filter {key}={oldval} to {key}={newval}".format(
                        key=key, oldval=old_filters[key], newval=extra_filters[key]
                    )
                )

        new_filters = dict(old_filters)
        new_filters.update(extra_filters)

        return new_filters

    def filter(self, filters=None, **kwargs):
        """
        Create a new filtered listing based on this listing. There are two way
        of defining the new filters. Either by passing a dict as the first
        argument, or by adding filters as keyword arguments.

        For example::
          >>> listing.filter({'ID': 'A*'})
          >>> listing.filter(ID='A*')

        are equivalent.

        :param dict filters: a dictionary containing the filters
        :param str kwargs: keyword arguments containing the filters
        :return: new filtered XNATListing
        :rtype: XNATListing
        """
        if filters is None:
            filters = kwargs

        new_filters = self.merge_filters(self.used_filters, filters)
        return XNATListing(
            uri=self.uri,
            xnat_session=self.xnat_session,
            parent=self.parent,
            field_name=self.field_name,
            secondary_lookup_field=self.secondary_lookup_field,
            xsi_type=self._xsi_type,
            filter=new_filters,
        )


class XNATSimpleListing(XNATBaseListing, MutableMapping, MutableSequence):
    def __init__(self, parent, field_name, secondary_lookup_field=None, xsi_type=None, data_field_name=None, **kwargs):
        super(XNATSimpleListing, self).__init__(
            parent, field_name, secondary_lookup_field=secondary_lookup_field, xsi_type=xsi_type, **kwargs
        )

        self._data_field_name = data_field_name

        if self._data_field_name is None:
            self._data_field_name = self.field_name.rsplit("/", 1)[-1]

            if self._data_field_name in DATA_FIELD_HINTS:
                self._data_field_name = DATA_FIELD_HINTS[self._data_field_name]

    def __str__(self) -> str:
        if self.secondary_lookup_field is not None:
            content = ", ".join("{!r}: {!r}".format(key, value) for key, value in self.items())
            content = "{{{}}}".format(content)
        else:
            content = ", ".join(repr(v) for v in self.listing)
            content = "[{}]".format(content)
        return "<{} {}>".format(type(self).__name__, content)

    def __iter__(self):
        for key in self.key_map:
            yield key

    @property
    def xnat_session(self):
        return self.parent.xnat_session

    def _resolve_fieldname(self):
        parent = self.parent
        fieldname = self.field_name

        # Make sure we are looking at a proper Object and not a SubObject (which might had part of the data we need)
        while isinstance(parent, XNATSubObject) and isinstance(parent.parent, XNATBaseObject):
            fieldname = "{}/{}".format(parent.fieldname, fieldname)
            parent = parent.parent

        return fieldname

    @property
    def fulldata(self):
        fieldname = self._resolve_fieldname()

        for child in self.parent.fulldata["children"]:
            if child["field"] == fieldname:
                return child["items"]
        return []

    @property
    def uri(self):
        return self.parent.fulluri

    @property
    @caching
    def data_maps(self):
        id_map = {}
        key_map = {}
        listing = []
        non_unique_keys = set()

        for index, element in enumerate(self.fulldata):
            if self.secondary_lookup_field is not None:
                key = element["data_fields"].get(self.secondary_lookup_field)
                # Make sure wiped fields are ignored
                if key is None:
                    continue
            else:
                key = index

            try:
                value = element["data_fields"][self._data_field_name]
            except KeyError:
                continue

            if key in key_map:
                non_unique_keys.add(key)
                key_map[key] = None
            elif self.secondary_lookup_field is not None:
                key_map[key] = value

            listing.append(value)

        return id_map, key_map, non_unique_keys, listing

    def __setitem__(self, key, value):
        parent = self.parent

        if self.secondary_lookup_field:
            lookup = "{}={}".format(self.secondary_lookup_field, key)
        else:
            lookup = key + 1

        query = {
            "xsiType": parent.__xsi_type__,
            "{xpath}/{fieldname}[{lookup}]/{fieldpart}".format(
                xpath=parent.xpath, fieldname=self.field_name, lookup=lookup, fieldpart=self._data_field_name
            ): value,
        }

        self.xnat_session.put(parent.fulluri, query=query)

        # Remove cache and make sure the reload the data
        self.clearcache()
        parent.clearcache()

    def __delitem__(self, key):
        fieldname = self._resolve_fieldname()
        parent = self.parent

        if self.secondary_lookup_field:
            lookup = "{}={}".format(self.secondary_lookup_field, key)
        else:
            lookup = key + 1

        query = {
            "xsiType": self.parent.__xsi_type__,
            "{xpath}/{fieldname}[{lookup}]/{fieldpart}".format(
                xpath=parent.xpath, fieldname=fieldname, lookup=lookup, fieldpart=self._data_field_name
            ): "NULL",
        }
        if self.secondary_lookup_field:
            query[
                "{xpath}/{fieldname}[{lookup}]/{key}".format(
                    xpath=parent.xpath, fieldname=fieldname, lookup=lookup, key=key
                )
            ] = "NULL"

        self.xnat_session.put(self.parent.fulluri, query=query)

        # Remove cache and make sure the reload the data
        self.clearcache()

    def insert(self, index, value):
        pass

    def clearcache(self):
        super(XNATSimpleListing, self).clearcache()
        self.parent.clearcache()


class XNATSubListing(XNATBaseListing, MutableMapping, MutableSequence):
    def __getitem__(self, item):
        try:
            return super(XNATSubListing, self).__getitem__(item)
        except (IndexError, KeyError):
            cls = self.xnat_session.XNAT_CLASS_LOOKUP[self._xsi_type]
            object = cls(uri=self.parent.uri, id_=item, datafields={}, parent=self, fieldname=item)
            return object

    @property
    def xnat_session(self):
        return self.parent.xnat_session

    @property
    def fulldata(self):
        for child in self.parent.fulldata["children"]:
            if child["field"] == self.field_name or child["field"].startswith(self.field_name + "/"):
                return child["items"]
        return []

    @property
    def uri(self):
        return self.parent.fulluri

    @property
    def fulluri(self):
        return self.parent.fulluri

    @property
    @caching
    def data_maps(self):
        id_map = {}
        key_map = {}
        listing = []
        non_unique_keys = set()

        for index, element in enumerate(self.fulldata):
            if self.secondary_lookup_field is not None:
                key = element["data_fields"][self.secondary_lookup_field]
            else:
                key = index

            try:
                xsi_type = element["meta"]["xsi:type"]
            except KeyError:
                xsi_type = self._xsi_type

            # XNAT seems to like to sometimes give a non-defined XSI type back
            #  (e.g. 'xnat:fieldDefinitionGroup_field'), make sure the XNAT
            # reply contains a valid XSI
            if xsi_type not in self.xnat_session.XNAT_CLASS_LOOKUP:
                xsi_type = self._xsi_type

            cls = self.xnat_session.XNAT_CLASS_LOOKUP[xsi_type]
            object = cls(uri=self.parent.uri, id_=key, datafields=element["data_fields"], parent=self, fieldname=key)

            if key in key_map:
                non_unique_keys.add(key)
                key_map[key] = None
            elif self.secondary_lookup_field is not None:
                key_map[key] = object

            listing.append(object)

        return id_map, key_map, non_unique_keys, listing

    @property
    def __xsi_type__(self):
        return self._xsi_type

    @property
    def xpath(self):
        return "{}/{}".format(self.parent.xpath, self.field_name)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        # Determine XPATH of item to remove
        if isinstance(key, int):
            xpath = "{}[{}]".format(self.xpath, key + 1)
        else:
            xpath = "{}[{}={}]".format(self.xpath, self.secondary_lookup_field, key)

        # Get correct xsi type
        if self.parent is not None:
            xsi_type = self.parent.__xsi_type__
        else:
            xsi_type = self.__xsi_type__

        query = {"xsiType": xsi_type, xpath: "NULL"}

        self.xnat_session.put(self.fulluri, query=query)
        self.clearcache()

    def insert(self, index, value):
        pass

    def clearcache(self):
        super(XNATSubListing, self).clearcache()
        self.parent.clearcache()
