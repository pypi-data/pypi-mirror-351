import csv
import datetime
from abc import ABCMeta, abstractmethod
from io import StringIO
from xml.etree import ElementTree

from . import exceptions

try:
    import pandas

    PANDAS_AVAILABLE = True
except ImportError:
    pandas = None
    PANDAS_AVAILABLE = False

xdat_ns = "http://nrg.wustl.edu/security"
ElementTree.register_namespace("xdat", xdat_ns)


def and_(*args):
    return CompoundConstraint(tuple(args), "AND")


def or_(*args):
    return CompoundConstraint(tuple(args), "OR")


def inject_search_fields(session):
    session.logger.info("Injecting display fields to classes")
    failed_datatypes = []
    for datatype in session.inspect.datatypes():
        cls = session.XNAT_CLASS_LOOKUP.get(datatype)
        if cls is None:
            session.logger.warning(f"Cannot find matching class for {datatype}")
            continue
        session.logger.debug(f"Inject fields for {datatype} to {cls}")
        try:
            fields = session.inspect.datafields(datatype)
        except exceptions.XNATResponseError as exception:
            failed_datatypes.append(datatype)
            session.logger.info(f"Could not retrieve display fields for {datatype}: {exception}")
            continue

        for field in fields:
            name = field.split("/")[-1]
            field = DisplayFieldSearchField(cls, name, "xs:string")
            setattr(cls, name, field)

    if failed_datatypes:
        session.logger.warning(f"Encountered errors retrieving display fields for: {', '.join(failed_datatypes)}")


class SearchFieldMap:
    def __init__(self, xsi_type):
        self._xsi_type = xsi_type

    def __getitem__(self, item):
        return CustomFieldSearchField(self._xsi_type, item)


class BaseSearchField(property):
    @property
    @abstractmethod
    def xsi_type(self):
        return None

    @property
    @abstractmethod
    def identifier(self):
        return None

    @property
    @abstractmethod
    def field_id(self):
        return None

    def __repr__(self):
        return "<SearchField {}>".format(self.identifier)

    def __eq__(self, other):
        return Constraint(self.identifier, "=", other)

    def __gt__(self, other):
        return Constraint(self.identifier, ">", other)

    def __ge__(self, other):
        return Constraint(self.identifier, ">=", other)

    def __lt__(self, other):
        return Constraint(self.identifier, "<", other)

    def __le__(self, other):
        return Constraint(self.identifier, "<=", other)

    def like(self, other):
        return Constraint(self.identifier, " LIKE ", other)


class CustomFieldSearchField(BaseSearchField):
    def __init__(self, xsi_type, field_name):
        super().__init__()
        self._xsi_type = xsi_type
        self._field_name = field_name
        self.type = "string"

    @property
    def xsi_type(self):
        return self._xsi_type

    @property
    def field_id(self):
        xsi_type = self._xsi_type.upper().replace(":", "_")
        identifier = f"{xsi_type}_FIELD_MAP={self._field_name.lower()}"
        return identifier

    @property
    def identifier(self):
        return f"{self.xsi_type}/{self.field_id}"


class SearchField(BaseSearchField):
    def __init__(self, search_class, field_name, type=None):
        super().__init__()
        self.search_class = search_class
        self.field_name = field_name
        self.type = type

    @property
    def xsi_type(self):
        return self.search_class.__xsi_type__

    @property
    def field_id(self):
        return self.identifier

    @property
    def identifier(self):
        # For the search criteria (where this is used) any xsitype/field
        # can be used (no need for display fields)
        field_name = self.field_name

        parent = self.search_class
        while parent.fieldname is not None:
            field_name = f"{parent.fieldname}/{field_name}"
            if parent.parent is None:
                break
            parent = parent.parent
        return "{}/{}".format(self.xsi_type, field_name)


class DisplayFieldSearchField(SearchField):
    @property
    def field_id(self):
        return self.field_name


class Query(object):
    def __init__(self, queried_class, xnat_session, fields=None, constraints=None):
        self.queried_class = queried_class
        self.xnat_session = xnat_session
        self.fields = tuple(fields) if fields else tuple()
        self.constraints = constraints

    @property
    def xsi_type(self):
        return self.queried_class.__xsi_type__

    # for updating the fields to be returned from the query
    def view(self, *fields):
        if len(fields) == 0:
            return self

        if self.fields is not None:
            fields = self.fields + tuple(fields)

        return Query(self.queried_class, self.xnat_session, fields, self.constraints)

    def filter(self, *constraints):
        if len(constraints) == 0:
            return self
        elif len(constraints) == 1:
            constraints = constraints[0]
        else:
            constraints = CompoundConstraint(constraints, "AND")

        if self.constraints is not None:
            constraints = CompoundConstraint((self.constraints, constraints), "AND")

        return Query(self.queried_class, self.xnat_session, self.fields, constraints)

    def to_xml(self):
        # Create main elements
        bundle = ElementTree.Element(ElementTree.QName(xdat_ns, "bundle"))
        root_elem_name = ElementTree.SubElement(bundle, ElementTree.QName(xdat_ns, "root_element_name"))
        root_elem_name.text = self.xsi_type

        # Add search fields
        if (not self.fields) and self.queried_class.DEFAULT_SEARCH_FIELDS:
            self.fields = tuple(getattr(self.queried_class, x) for x in self.queried_class.DEFAULT_SEARCH_FIELDS)

        if self.fields is not None:
            for idx, x in enumerate(self.fields):
                search_where = ElementTree.SubElement(bundle, ElementTree.QName(xdat_ns, "search_field"))
                element_name = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "element_name"))
                element_name.text = x.xsi_type
                field_id = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "field_ID"))
                field_id.text = x.field_id
                sequence = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "sequence"))
                sequence.text = str(idx)
                type_ = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "type"))
                type_.text = str(x.type)
                header = ElementTree.SubElement(search_where, ElementTree.QName(xdat_ns, "header"))
                header.text = "url"

        # Add criteria
        search_where = ElementTree.SubElement(bundle, ElementTree.QName(xdat_ns, "search_where"))
        search_where.set("method", "AND")
        if self.constraints is not None:
            search_where.append(self.constraints.to_xml())

        return bundle

    def to_string(self):
        return ElementTree.tostring(self.to_xml())

    def tabulate_csv(self):
        result = self.xnat_session.post("/data/search", format="csv", data=self.to_string())

        # Parse returned table
        csv_text = str(result.text)

        return csv_text

    def tabulate_json(self):
        result = self.xnat_session.post("/data/search", format="json", data=self.to_string())

        # Parse returned table
        json_text = str(result.text)

        return json_text

    def tabulate_pandas(self):
        if not PANDAS_AVAILABLE:
            raise ModuleNotFoundError("Cannot tabulate to pandas without pandas being installed!")
        csv_data = self.tabulate_csv()
        csv_data = StringIO(csv_data)
        return pandas.read_csv(csv_data)

    def tabulate_dict(self):
        # Parse returned table
        csv_text = self.tabulate_csv()
        csv_dialect = csv.Sniffer().sniff(csv_text)
        data = list(csv.reader(csv_text.splitlines(), dialect=csv_dialect))
        header = data[0]

        data = [dict(zip(header, x)) for x in data[1:]]

        return data

    def _run_query(self):
        result = self.xnat_session.post("/data/search", format="csv", data=self.to_string())

        # Parse returned table
        csv_text = str(result.text)
        csv_dialect = csv.Sniffer().sniff(csv_text)
        data = list(csv.reader(csv_text.splitlines(), dialect=csv_dialect))
        header = data[0]

        data = [dict(zip(header, x)) for x in data[1:]]
        return data

    def _create_object(self, row):
        row["session_uri"] = self.xnat_session.fulluri
        uri = self.queried_class.FROM_SEARCH_URI

        if uri:
            uri = uri.format(**row)
            obj = self.xnat_session.create_object(uri=uri)
        else:
            obj = None

        return obj

    def all(self):
        data = self._run_query()
        objects = []
        for row in data:
            obj = self._create_object(row)
            if obj:
                objects.append(obj)

        return objects

    def first(self):
        data = self._run_query()
        return self._create_object(data[0])

    def last(self):
        data = self._run_query()
        return self._create_object(data[-1])

    def one(self):
        data = self._run_query()

        if len(data) != 1:
            raise ValueError(f"Did not find exactly one result (found {len(data)})")
        return self._create_object(data[0])

    def one_or_none(self):
        data = self._run_query()

        if len(data) > 1:
            raise ValueError(f"Did not find exactly one or no result (found {len(data)})")
        elif len(data) == 0:
            return None

        return self._create_object(data[0])


class BaseConstraint(metaclass=ABCMeta):
    @abstractmethod
    def to_xml(self):
        pass

    def to_string(self):
        return ElementTree.tostring(self.to_xml())

    def __or__(self, other):
        return CompoundConstraint((self, other), "OR")

    def __and__(self, other):
        return CompoundConstraint((self, other), "AND")


class CompoundConstraint(BaseConstraint):
    def __repr__(self):
        return "<CompoundConstraint {} ({})>".format(self.operator, self.constraints)

    def __init__(self, constraints, operator):
        self.constraints = constraints
        self.operator = operator

    def to_xml(self):
        elem = ElementTree.Element(ElementTree.QName(xdat_ns, "child_set"))
        elem.set("method", self.operator)
        elem.extend(x.to_xml() for x in self.constraints)

        return elem


class Constraint(BaseConstraint):
    def __init__(self, identifier, operator, right_hand):
        self.identifier = identifier
        self.operator = operator
        self.right_hand = right_hand

    def __repr__(self):
        return "<Constrain {} {}({})>".format(self.identifier, self.operator, self.right_hand)

    def to_xml(self):
        elem = ElementTree.Element(ElementTree.QName(xdat_ns, "criteria"))
        schema_loc = ElementTree.SubElement(elem, ElementTree.QName(xdat_ns, "schema_field"))
        operator = ElementTree.SubElement(elem, ElementTree.QName(xdat_ns, "comparison_type"))
        value = ElementTree.SubElement(elem, ElementTree.QName(xdat_ns, "value"))

        elem.set("override_value_formatting", "0")
        schema_loc.text = self.identifier
        operator.text = self.operator
        if isinstance(self.right_hand, (datetime.date, datetime.datetime)):
            right_hand = self.right_hand.strftime("%m/%d/%Y")
        else:
            right_hand = str(self.right_hand)
        value.text = right_hand

        return elem
