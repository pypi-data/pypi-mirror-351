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

from datetime import datetime

import pytest

# Mark this entire module as functional tests requiring docker
pytestmark = [pytest.mark.functional_test, pytest.mark.server_test]

QUERY1 = (
    b'<xdat:bundle xmlns:xdat="http://nrg.wustl.edu/security"><xdat:root_element_n'
    b"ame>xnat:mrSessionData</xdat:root_element_name><xdat:search_field><xdat:elem"
    b"ent_name>xnat:mrSessionData</xdat:element_name><xdat:field_ID>PROJECT</xdat:"
    b"field_ID><xdat:sequence>0</xdat:sequence><xdat:type>xs:string</xdat:type><xd"
    b"at:header>url</xdat:header></xdat:search_field><xdat:search_field><xdat:elem"
    b"ent_name>xnat:mrSessionData</xdat:element_name><xdat:field_ID>xnat:mrSession"
    b"Data/label</xdat:field_ID><xdat:sequence>1</xdat:sequence><xdat:type>None</x"
    b"dat:type><xdat:header>url</xdat:header></xdat:search_field><xdat:search_wher"
    b'e method="AND"><xdat:criteria override_value_formatting="0"><xdat:schema_fie'
    b"ld>xnat:mrSessionData/label</xdat:schema_field><xdat:comparison_type>=</xdat"
    b":comparison_type><xdat:value>test</xdat:value></xdat:criteria></xdat:search_"
    b"where></xdat:bundle>"
)

QUERY2 = (
    b'<xdat:bundle xmlns:xdat="http://nrg.wustl.edu/security"><xdat:root_element_'
    b"name>xnat:mrSessionData</xdat:root_element_name><xdat:search_field><xdat:el"
    b"ement_name>xnat:mrSessionData</xdat:element_name><xdat:field_ID>xnat:mrSess"
    b"ionData/ID</xdat:field_ID><xdat:sequence>0</xdat:sequence><xdat:type>xs:str"
    b"ing</xdat:type><xdat:header>url</xdat:header></xdat:search_field><xdat:sear"
    b"ch_field><xdat:element_name>xnat:mrSessionData</xdat:element_name><xdat:fie"
    b"ld_ID>xnat:mrSessionData/project</xdat:field_ID><xdat:sequence>1</xdat:sequ"
    b"ence><xdat:type>xs:string</xdat:type><xdat:header>url</xdat:header></xdat:s"
    b"earch_field><xdat:search_field><xdat:element_name>xnat:mrSessionData</xdat:"
    b"element_name><xdat:field_ID>xnat:mrSessionData/subject_ID</xdat:field_ID><x"
    b"dat:sequence>2</xdat:sequence><xdat:type>xs:string</xdat:type><xdat:header>"
    b'url</xdat:header></xdat:search_field><xdat:search_where method="AND"><xdat:'
    b'child_set method="AND"><xdat:criteria override_value_formatting="0"><xdat:s'
    b"chema_field>xnat:mrSessionData/PROJECT</xdat:schema_field><xdat:comparison_"
    b"type>=</xdat:comparison_type><xdat:value>sandbox</xdat:value></xdat:criteri"
    b'a><xdat:criteria override_value_formatting="0"><xdat:schema_field>xnat:mrSe'
    b"ssionData/INSERT_DATE</xdat:schema_field><xdat:comparison_type>&gt;=</xdat:"
    b"comparison_type><xdat:value>12/11/2023</xdat:value></xdat:criteria><xdat:cr"
    b'iteria override_value_formatting="0"><xdat:schema_field>xnat:mrSessionData/'
    b"INSERT_DATE</xdat:schema_field><xdat:comparison_type>&lt;=</xdat:comparison"
    b"_type><xdat:value>12/13/2023</xdat:value></xdat:criteria></xdat:child_set><"
    b"/xdat:search_where></xdat:bundle>"
)

QUERY3 = (
    b'<xdat:bundle xmlns:xdat="http://nrg.wustl.edu/security"><xdat:root_element_'
    b"name>xnat:mrSessionData</xdat:root_element_name><xdat:search_field><xdat:el"
    b"ement_name>xnat:mrSessionData</xdat:element_name><xdat:field_ID>xnat:mrSess"
    b"ionData/ID</xdat:field_ID><xdat:sequence>0</xdat:sequence><xdat:type>xs:str"
    b"ing</xdat:type><xdat:header>url</xdat:header></xdat:search_field><xdat:sear"
    b"ch_field><xdat:element_name>xnat:mrSessionData</xdat:element_name><xdat:fie"
    b"ld_ID>xnat:mrSessionData/project</xdat:field_ID><xdat:sequence>1</xdat:sequ"
    b"ence><xdat:type>xs:string</xdat:type><xdat:header>url</xdat:header></xdat:s"
    b"earch_field><xdat:search_field><xdat:element_name>xnat:mrSessionData</xdat:"
    b"element_name><xdat:field_ID>xnat:mrSessionData/subject_ID</xdat:field_ID><x"
    b"dat:sequence>2</xdat:sequence><xdat:type>xs:string</xdat:type><xdat:header>"
    b'url</xdat:header></xdat:search_field><xdat:search_where method="AND"><xdat:'
    b'child_set method="AND"><xdat:child_set method="AND"><xdat:criteria override'
    b'_value_formatting="0"><xdat:schema_field>xnat:mrSessionData/PROJECT</xdat:s'
    b"chema_field><xdat:comparison_type>=</xdat:comparison_type><xdat:value>sandb"
    b'ox</xdat:value></xdat:criteria><xdat:criteria override_value_formatting="0"'
    b"><xdat:schema_field>xnat:mrSessionData/INSERT_DATE</xdat:schema_field><xdat"
    b":comparison_type>&gt;=</xdat:comparison_type><xdat:value>12/11/2023</xdat:v"
    b"alue></xdat:criteria></xdat:child_set><xdat:criteria override_value_formatt"
    b'ing="0"><xdat:schema_field>xnat:mrSessionData/INSERT_DATE</xdat:schema_fiel'
    b"d><xdat:comparison_type>&lt;=</xdat:comparison_type><xdat:value>12/13/2023<"
    b"/xdat:value></xdat:criteria></xdat:child_set></xdat:search_where></xdat:bun"
    b"dle>"
)


def test_querying(test_server_connection):
    MrSessionData = test_server_connection.classes.MrSessionData

    # Simple query
    query = MrSessionData.query().filter(MrSessionData.label == "test").view(MrSessionData.PROJECT, MrSessionData.label)

    # Test chaining the views instead of a single multi-argument view
    assert query.to_string() == QUERY1

    result = query.tabulate_dict()
    assert result == [{"project": "sandbox", "quarantine_status": "active", "xnat_col_mrsessiondatalabel": "test"}]

    result = query.tabulate_json()
    assert (
        result == '{"ResultSet":{"Columns":[{"key":"project","type":"string","xPATH":"xnat:mrSessionData.PROJ'
        'ECT","element_name":"xnat:mrSessionData","header":"url","id":"PROJECT"},{"key":"xnat_col_m'
        'rsessiondatalabel","type":"string","xPATH":"xnat:mrSessionData.XNAT_COL_MRSESSIONDATALABEL'
        '","element_name":"xnat:mrSessionData","header":"url","id":"XNAT_COL_MRSESSIONDATALABEL"},{'
        '"key":"quarantine_status"}],"Result":[{"quarantine_status":"active","project":"sandbox","x'
        'nat_col_mrsessiondatalabel":"test"}], "rootElementName": "xnat:mrSessionData","totalRecord'
        's": "1"}}'
    )

    result = query.tabulate_csv()
    assert result == "project,xnat_col_mrsessiondatalabel,quarantine_status\nsandbox,test,active\n"

    query = (
        MrSessionData.query()
        .filter(MrSessionData.label == "test")
        .view(MrSessionData.PROJECT)
        .view(MrSessionData.label)
    )

    assert query.to_string() == QUERY1

    # Test a query with multiple filter constraints
    query = MrSessionData.query().filter(
        MrSessionData.PROJECT == "sandbox",
        MrSessionData.INSERT_DATE >= datetime.strptime("2023-12-11", "%Y-%m-%d"),
        MrSessionData.INSERT_DATE <= datetime.strptime("2023-12-13", "%Y-%m-%d"),
    )

    # Write the query with & operators, this nests the AND in a ((X and Y) and Z)
    assert query.to_string() == QUERY2

    result = query.all()
    assert len(result) == 1
    assert isinstance(result[0], MrSessionData)
    assert result[0].label == "test"
    assert result[0].id == "BMIAXNAT_E82572"

    query = MrSessionData.query().filter(
        (MrSessionData.PROJECT == "sandbox")
        & (MrSessionData.INSERT_DATE >= datetime.strptime("2023-12-11", "%Y-%m-%d"))
        & (MrSessionData.INSERT_DATE <= datetime.strptime("2023-12-13", "%Y-%m-%d"))
    )

    assert query.to_string() == QUERY3

    result = query.one()
    assert isinstance(result, MrSessionData)
    assert result.label == "test"
    assert result.id == "BMIAXNAT_E82572"

    # Different way of writing the same query
    query = (
        MrSessionData.query()
        .filter(
            (MrSessionData.PROJECT == "sandbox"),
            (MrSessionData.INSERT_DATE >= datetime.strptime("2023-12-11", "%Y-%m-%d")),
        )
        .filter(MrSessionData.INSERT_DATE <= datetime.strptime("2023-12-13", "%Y-%m-%d"))
    )

    assert query.to_string() == QUERY3

    result = query.first()
    assert isinstance(result, MrSessionData)
    assert result.label == "test"
    assert result.id == "BMIAXNAT_E82572"
