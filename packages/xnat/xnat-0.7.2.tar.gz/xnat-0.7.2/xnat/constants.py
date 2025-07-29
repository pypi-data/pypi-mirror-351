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
from typing import Dict, List, Optional, Set

TYPE_HINTS: Dict[str, Optional[str]] = {
    "demographics": "xnat:demographicData",
    "investigator": "xnat:investigatorData",
    "metadata": "xnat:subjectMetadata",
    "pi": "xnat:investigatorData",
    "studyprotocol": "xnat:studyProtocol",
    "validation": "xnat:validationData",
    "baseimage": "xnat:abstractResource",
    "projects": "xnat:projectData",
    "subjects": "xnat:subjectData",
    "experiments": None,  # Can be many types, need to check each time
    "scans": None,  # Can be many types, need to check each time
    "resources": None,  # Can be many types, need to check each time
    "assessors": None,  # Can be many types, need to check each time
    "reconstructions": None,  # Can be many types, need to check each time
    "files": "xnat:fileData",
}

FIELD_HINTS: Dict[str, str] = {
    "xnat:projectData": "projects",
    "xnat:subjectData": "subjects",
    "xnat:experimentData": "experiments",
    "xnat:imageScanData": "scans",
    "xnat:reconstructedImageData": "reconstructions",
    "xnat:imageAssessorData": "assessors",
    "xnat:abstractResource": "resources",
    "xnat:fileData": "files",
    "addParam": "parameters/addParam",
}

DATA_FIELD_HINTS: Dict[str, str] = {"addParam": "addField"}

# The following xsi_types are objects with their own REST paths, the
# other are nested in the xml of their parent.
CORE_REST_OBJECTS: Set[str] = {
    "xnat:projectData",
    "xnat:subjectData",
    "xnat:experimentData",
    "xnat:reconstructedImageData",
    "xnat:imageAssessorData",
    "xnat:imageScanData",
    "xnat:abstractResource",
    "xnat:fileData",
}

# Override base class for some types
OVERRIDE_BASE = {
    #    'xnat:demographicData': 'XNATNestedObjectMixin',
}

# These are additions to the DisplayIdentifier set in the xsd files
SECONDARY_LOOKUP_FIELDS: Dict[str, str] = {
    "xnat:projectData": "name",
    "xnat:imageScanData": "type",
    "xnat:fileData": "name",
}

# DEFAULT SCHEMAS IN XNAT 1.7
DEFAULT_SCHEMAS: List[str] = [
    "security",
    "xnat",
    "assessments",
    "screening/screeningAssessment",
    "pipeline/build",
    "pipeline/repository",
    "pipeline/workflow",
    "birn/birnprov",
    "catalog",
    "project",
    "validation/protocolValidation",
    "xdat/display",
    "xdat",
    "xdat/instance",
    "xdat/PlexiViewer",
]


TIMEZONES_STRING = """-12 Y
-11 X NUT SST
-10 W CKT HAST HST TAHT TKT
-9 V AKST GAMT GIT HADT HNY
-8 U AKDT CIST HAY HNP PST PT
-7 T HAP HNR MST PDT
-6 S CST EAST GALT HAR HNC MDT
-5 R CDT COT EASST ECT EST ET HAC HNE PET
-4 Q AST BOT CLT COST EDT FKT GYT HAE HNA PYT
-3 P ADT ART BRT CLST FKST GFT HAA PMST PYST SRT UYT WGT
-2 O BRST FNT PMDT UYST WGST
-1 N AZOT CVT EGT
0 Z EGST GMT UTC WET WT
1 A CET DFT WAT WEDT WEST
2 B CAT CEDT CEST EET SAST WAST
3 C EAT EEDT EEST IDT MSK
4 D AMT AZT GET GST KUYT MSD MUT RET SAMT SCT
5 E AMST AQTT AZST HMT MAWT MVT PKT TFT TJT TMT UZT YEKT
6 F ALMT BIOT BTT IOT KGT NOVT OMST YEKST
7 G CXT DAVT HOVT ICT KRAT NOVST OMSST THA WIB
8 H ACT AWST BDT BNT CAST HKT IRKT KRAST MYT PHT SGT ULAT WITA WST
9 I AWDT IRKST JST KST PWT TLT WDT WIT YAKT
10 K AEST ChST PGT VLAT YAKST YAPT
11 L AEDT LHDT MAGT NCT PONT SBT VLAST VUT
12 M ANAST ANAT FJT GILT MAGST MHT NZST PETST PETT TVT WFT
13 FJST NZDT
11.5 NFT
10.5 ACDT LHST
9.5 ACST
6.5 CCT MMT
5.75 NPT
5.5 SLT
4.5 AFT IRDT
3.5 IRST
-2.5 HAT NDT
-3.5 HNT NST NT
-4.5 HLV VET
-9.5 MART MIT"""


# Convert the string into a dictionary to be used by dateutil.parser.parse,
# see https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.parse
TIMEZONES_DICT = {}
for _timezone in TIMEZONES_STRING.split("\n"):
    _timezone = _timezone.split()
    _offset = int(float(_timezone[0]) * 3600)
    for _code in _timezone[1:]:
        TIMEZONES_DICT[_code] = _offset


PROJECT_DATA_REST_SHORTCUTS = {
    "ID": "xnat:projectData/ID",
    "secondary_ID": "xnat:projectData/secondary_ID",
    "name": "xnat:projectData/name",
    "description": "xnat:projectData/description",
    "keywords": "xnat:projectData/keywords",
    "alias": "xnat:projectData/aliases/alias",
    "pi_firstname": "xnat:projectData/PI/firstname",
    "pi_lastname": "xnat:projectData/PI/lastname",
    "note": "xnat:projectData/fields/fieldname=note/field",
    "last_modified": "xnat:projectData/meta/last_modified",
    "insert_date": "xnat:projectData/meta/insert_date",
    "insert_user": "xnat:projectData/meta/insert_user/login",
}

SUBJECT_DATA_REST_SHORTCUTS = {
    "age": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/age",
    "birth_weight": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/birth_weight",
    "dob": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/dob",
    "education": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/education",
    "educationDesc": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/educationDesc",
    "ethnicity": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/ethnicity",
    "gender": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/gender",
    "gestational_age": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/gestational_age",
    "group": "xnat:subjectData/group",
    "handedness": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/handedness",
    "height": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/height",
    "insert_date": "xnat:subjectData/meta/insert_date",
    "insert_user": "xnat:subjectData/meta/insert_user/login",
    "last_modified": "xnat:subjectData/meta/last_modified",
    "pi_firstname": "xnat:subjectData/investigator/firstname",
    "pi_lastname": "xnat:subjectData/investigator/lastname",
    "post_menstrual_age": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/post_menstrual_age",
    "race": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/race",
    "ses": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/ses",
    "src": "xnat:subjectData/src",
    "weight": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/weight",
    "yob": "xnat:subjectData/demographics[@xsi:type=xnat:demographicData]/yob",
}

EXPERIMENT_DATA_REST_SHORTCUTS = {
    "visit_id": "xnat:experimentdata/visit_id",
    "date": "xnat:experimentdata/date",
    "ID": "xnat:experimentdata/ID",
    "project": "xnat:experimentdata/project",
    "label": "xnat:experimentdata/label",
    "time": "xnat:experimentdata/time",
    "note": "xnat:experimentdata/note",
    "pi_firstname": "xnat:experimentdata/investigator/firstname",
    "pi_lastname": "xnat:experimentdata/investigator/lastname",
    "validation_method": "xnat:experimentdata/validation/method",
    "validation_status": "xnat:experimentdata/validation/status",
    "validation_date": "xnat:experimentdata/validation/date",
    "validation_notes": "xnat:experimentdata/validation/notes",
    "last_modified": "xnat:experimentdata/meta/last_modified",
    "insert_date": "xnat:experimentdata/meta/insert_date",
    "insert_user": "xnat:experimentdata/meta/insert_user/login",
    "subject_ID": "xnat:subjectData/ID",
    "subject_label": "xnat:subjectData/label",
    "subject_project": "xnat:subjectData/project",
}

IMAGE_SESSION_DATA_REST_SHORTCUTS = {
    "scanner": "xnat:imageSessionData/scanner",
    "operator": "xnat:imageSessionData/operator",
    "dcmAccessionNumber": "xnat:imageSessionData/dcmAccessionNumber",
    "dcmPatientId": "xnat:imageSessionData/dcmPatientId",
    "dcmPatientName": "xnat:imageSessionData/dcmPatientName",
    "session_type": "xnat:imageSessionData/session_type",
    "modality": "xnat:imageSessionData/modality",
    "UID": "xnat:imageSessionData/UID",
}

MR_SESSION_DATA_REST_SHORTCUTS = {
    "coil": "xnat:mrSessionData/coil",
    "fieldStrength": "xnat:mrSessionData/fieldStrength",
    "marker": "xnat:mrSessionData/marker",
    "stabilization": "xnat:mrSessionData/stabilization",
}

PET_SESSION_DATA_REST_SHORTCUTS = {
    "studyType": "xnat:petSessionData/studyType",
    "patientID": "xnat:petSessionData/patientID",
    "patientName": "xnat:petSessionData/patientName",
    "stabilization": "xnat:petSessionData/stabilization",
    "scan_start_time": "xnat:petSessionData/start_time/scan",
    "injection_start_time": "xnat:petSessionData/start_time/injection",
    "tracer_name": "xnat:petSessionData/tracer/name",
    "tracer_startTime": "xnat:petSessionData/tracer/startTime",
    "tracer_dose": "xnat:petSessionData/tracer/dose",
    "tracer_sa": "xnat:petSessionData/tracer/specificActivity",
    "tracer_totalmass": "xnat:petSessionData/tracer/totalMass",
    "tracer_intermediate": "xnat:petSessionData/tracer/intermediate",
    "tracer_isotope": "xnat:petSessionData/tracer/isotope",
    "tracer_isotope": "xnat:petSessionData/tracer/isotope/half-life",
    "tracer_transmissions": "xnat:petSessionData/tracer/transmissions",
    "tracer_transmissions_start": "xnat:petSessionData/tracer/transmissions/startTime",
}

IMAGE_ASSESSOR_DATA_REST_SHORTCUTS = {
    "visit_id": "xnat:experimentdata/visit_id",
    "date": "xnat:experimentdata/date",
    "time": "xnat:experimentdata/time",
    "note": "xnat:experimentdata/note",
    "pi_firstname": "xnat:experimentdata/investigator/firstname",
    "pi_lastname": "xnat:experimentdata/investigator/lastname",
    "validation_method": "xnat:experimentdata/validation/method",
    "validation_status": "xnat:experimentdata/validation/status",
    "validation_date": "xnat:experimentdata/validation/date",
    "validation_notes": "xnat:experimentdata/validation/notes",
    "last_modified": "xnat:experimentdata/meta/last_modified",
    "insert_date": "xnat:experimentdata/meta/insert_date",
    "insert_user": "xnat:experimentdata/meta/insert_user/login",
}

IMAGE_SCAN_DATA_REST_SHORTCUTS = {
    "ID": "xnat:imageScanData/ID",
    "type": "xnat:imageScanData/type",
    "UID": "xnat:imageScanData/UID",
    "note": "xnat:imageScanData/note",
    "quality": "xnat:imageScanData/quality",
    "condition": "xnat:imageScanData/condition",
    "series_description": "xnat:imageScanData/series_description",
    "documentation": "xnat:imageScanData/documentation",
    "scanner": "xnat:imageScanData/scanner",
    "modality": "xnat:imageScanData/modality",
    "frames": "xnat:imageScanData/frames",
    "validation_method": "xnat:imageScanData/validation/method",
    "validation_status": "xnat:imageScanData/validation/status",
    "validation_date": "xnat:imageScanData/validation/date",
    "validation_notes": "xnat:imageScanData/validation/notes",
    "last_modified": "xnat:imageScanData/meta/last_modified",
    "insert_date": "xnat:imageScanData/meta/insert_date",
    "insert_user": "xnat:imageScanData/meta/insert_user/login",
}

MR_SCAN_DATA_REST_SHORTCUTS = {
    "coil": "xnat:mrScanData/coil",
    "fieldStrength": "xnat:mrScanData/fieldStrength",
    "marker": "xnat:mrScanData/marker",
    "stabilization": "xnat:mrScanData/stabilization",
}

PET_SCAN_DATA_REST_SHORTCUTS = {
    "orientation": "xnat:petScanData/parameters/orientation",
    "scanTime": "xnat:petScanData/parameters/scanTime",
    "originalFileName": "xnat:petScanData/parameters/originalFileName",
    "systemType": "xnat:petScanData/parameters/systemType",
    "fileType": "xnat:petScanData/parameters/fileType",
    "transaxialFOV": "xnat:petScanData/parameters/transaxialFOV",
    "acqType": "xnat:petScanData/parameters/acqType",
    "facility": "xnat:petScanData/parameters/facility",
    "numPlanes": "xnat:petScanData/parameters/numPlanes",
    "numFrames": "xnat:petScanData/parameters/frames/numFrames",
    "numGates": "xnat:petScanData/parameters/numGates",
    "planeSeparation": "xnat:petScanData/parameters/planeSeparation",
    "binSize": "xnat:petScanData/parameters/binSize",
    "dataType": "xnat:petScanData/parameters/dataType",
}

REST_SHORTCUTS = {
    "xnat:projectData": PROJECT_DATA_REST_SHORTCUTS,
    "xnat:subjectData": SUBJECT_DATA_REST_SHORTCUTS,
    "xnat:experimentData": EXPERIMENT_DATA_REST_SHORTCUTS,
    "xnat:imageSessionData": IMAGE_SESSION_DATA_REST_SHORTCUTS,
    "xnat:mrSessionData": MR_SESSION_DATA_REST_SHORTCUTS,
    "xnat:petSessionData": PET_SESSION_DATA_REST_SHORTCUTS,
    "xnat:imageAssessorData": IMAGE_ASSESSOR_DATA_REST_SHORTCUTS,
    "xnat:imageScanData": IMAGE_SCAN_DATA_REST_SHORTCUTS,
    "xnat:mrScanData": MR_SCAN_DATA_REST_SHORTCUTS,
    "xnat:petScanData": PET_SCAN_DATA_REST_SHORTCUTS,
}

ALL_REST_SHORTCUT_NAMES = set()
for shortcuts in REST_SHORTCUTS.values():
    ALL_REST_SHORTCUT_NAMES.update(shortcuts.keys())
