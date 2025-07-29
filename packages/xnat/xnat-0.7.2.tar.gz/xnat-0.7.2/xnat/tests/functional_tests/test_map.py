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

import pytest

from xnat import MappingLevel
from xnat.mixin import MappedFunctionFailed

# Mark this entire module as functional tests requiring docker
pytestmark = [pytest.mark.docker_test, pytest.mark.functional_test]


def test_map_loglevel(xnat4tests_connection):
    # Test mapping over projects, but use string to indicate level
    result0 = xnat4tests_connection.map(lambda x: x.name, level="project")

    assert len(result0) == 2
    assert result0 == {
        "/data/archive/projects/dummydicomproject": "dummydicomproject",
        "/data/archive/projects/TRAINING": "TRAINING",
    }

    with pytest.raises(ValueError, match=r'Level "wrong_level" is not a valid MappingLevel, available: .*'):
        xnat4tests_connection.map(lambda x: x.name, level="wrong_level")


def test_map_connection(xnat4tests_connection):
    # Test mapping over projects
    result0 = xnat4tests_connection.map(lambda x: x.name, level=MappingLevel.PROJECT)

    assert len(result0) == 2
    assert result0 == {
        "/data/archive/projects/dummydicomproject": "dummydicomproject",
        "/data/archive/projects/TRAINING": "TRAINING",
    }

    # Test a mapping over all experiments
    result1 = xnat4tests_connection.map(lambda x: x.label, level=MappingLevel.EXPERIMENT)

    assert len(result1) == 9
    assert result1 == {
        "/data/archive/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001": "dummydicomsession",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00002": "CONT01_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00004": "CONT01_MR02",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00003": "CONT02_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00005": "CONT02_MR02",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00004/experiments/Xnat4Tests_E00006": "TEST01_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00004/experiments/Xnat4Tests_E00007": "TEST01_MR02",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00005/experiments/Xnat4Tests_E00008": "TEST02_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00005/experiments/Xnat4Tests_E00009": "TEST02_MR02",
    }

    # Do a search with a filter
    result2 = xnat4tests_connection.search(level=MappingLevel.EXPERIMENT, subject="CONT*")

    assert len(result2) == 4
    assert all(isinstance(x, xnat4tests_connection.classes.MrSessionData) for x in result2)
    assert sorted(x.id for x in result2) == [
        "Xnat4Tests_E00002",
        "Xnat4Tests_E00003",
        "Xnat4Tests_E00004",
        "Xnat4Tests_E00005",
    ]

    result3 = xnat4tests_connection.search(level=MappingLevel.SCAN, subject="CONT*", experiment="*_MR02")

    assert len(result3) == 4
    assert all(isinstance(x, xnat4tests_connection.classes.MrScanData) for x in result3)
    assert sorted(x.id for x in result3) == ["2", "2", "6", "6"]
    assert sorted(x.type for x in result3) == [
        "gre_field_mapping 3mm",
        "gre_field_mapping 3mm",
        "t1_mprage_sag_p2_iso_1",
        "t1_mprage_sag_p2_iso_1",
    ]

    result4 = xnat4tests_connection.search(
        level=MappingLevel.SCAN_RESOURCE, subject="CONT[0-9][0-9]", experiment=".*_MR02", use_regex=True
    )
    print(f"{[x.uri for x in result4]=}")
    assert len(result4) == 4
    assert all(isinstance(x, xnat4tests_connection.classes.ResourceCatalog) for x in result4)
    assert [x.label for x in result4] == ["DICOM", "DICOM", "DICOM", "DICOM"]
    assert sorted(x.uri for x in result4) == [
        "/data/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00004/scans/2/resources/9",
        "/data/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00004/scans/6/resources/10",
        "/data/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00005/scans/2/resources/11",
        "/data/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00005/scans/6/resources/12",
    ]

    result5 = xnat4tests_connection.search(level=MappingLevel.SUBJECT, project="TRAINING", subject="TEST*")
    assert len(result5) == 2
    assert all(isinstance(x, xnat4tests_connection.classes.SubjectData) for x in result5)
    assert sorted(x.label for x in result5) == ["TEST01", "TEST02"]


def test_map_project(xnat4tests_connection):
    project = xnat4tests_connection.projects["dummydicomproject"]

    # Map over experiments
    result = project.map(lambda x: x.label, level=MappingLevel.EXPERIMENT)

    assert result == {
        "/data/archive/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001": "dummydicomsession"
    }

    result = project.map(lambda x: x.type, level=MappingLevel.SCAN)

    # Map over scans
    assert result == {
        "/data/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001/scans/2": "t1_mprage_sag_p2_iso_1",
        "/data/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001/scans/6": "gre_field_mapping 3mm",
        "/data/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001/scans/13": "R-L MRtrix 60 directions interleaved B0 ep2d_diff_p2",
    }

    # This causes errors in the function supplied, but should not crash the map code
    # A scan object does not have a label, so an AttributeError is raised
    result = project.map(lambda x: x.label, level=MappingLevel.SCAN)
    print(result)

    # Exceptions can't be directly compared, so compare the type and str version
    assert set(result.keys()) == {
        "/data/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001/scans/13",
        "/data/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001/scans/2",
        "/data/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001/scans/6",
    }

    for item in result.values():
        assert item == MappedFunctionFailed("'MrScanData' object has no attribute 'label'")


def test_map_logfile(xnat4tests_connection, tmp_path):
    log_file = tmp_path / "map_log.yaml"
    message = f"We cannot process experiment with label CONT02_MR02"

    def test_func(experiment):
        if experiment.label == "CONT02_MR02":
            raise ValueError(message)
        return experiment.label

    result1 = xnat4tests_connection.map(test_func, level=MappingLevel.EXPERIMENT, logfile=log_file)

    assert len(result1) == 9
    assert result1 == {
        "/data/archive/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001": "dummydicomsession",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00002": "CONT01_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00004": "CONT01_MR02",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00003": "CONT02_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00005": MappedFunctionFailed(
            message
        ),
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00004/experiments/Xnat4Tests_E00006": "TEST01_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00004/experiments/Xnat4Tests_E00007": "TEST01_MR02",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00005/experiments/Xnat4Tests_E00008": "TEST02_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00005/experiments/Xnat4Tests_E00009": "TEST02_MR02",
    }

    # Run with logfile in place to see if shortcuts are used
    result2 = xnat4tests_connection.map(test_func, level=MappingLevel.EXPERIMENT, logfile=log_file)

    assert len(result2) == 9
    assert result2 == {
        "/data/archive/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001": "dummydicomsession",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00002": "CONT01_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00002/experiments/Xnat4Tests_E00004": "CONT01_MR02",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00003": "CONT02_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00003/experiments/Xnat4Tests_E00005": MappedFunctionFailed(
            message
        ),
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00004/experiments/Xnat4Tests_E00006": "TEST01_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00004/experiments/Xnat4Tests_E00007": "TEST01_MR02",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00005/experiments/Xnat4Tests_E00008": "TEST02_MR01",
        "/data/archive/projects/TRAINING/subjects/Xnat4Tests_S00005/experiments/Xnat4Tests_E00009": "TEST02_MR02",
    }


def test_map_return_value(xnat4tests_connection, tmp_path):
    project = xnat4tests_connection.projects["dummydicomproject"]
    log_file1 = tmp_path / "map_log1.yaml"
    log_file2 = tmp_path / "map_log2.yaml"

    # Return some more complex data that is valid for logfile
    def test_func_valid(experiment):
        return {
            "label": experiment.label,
            "one": [1, 2, 3],
            "two": "three",
            "four": None,
            "five": {"foo": False, "bar": True},
        }

    # This data is invalid because the experiment cannot be JSON serialised
    def test_func_invalid(experiment):
        return {
            "label": experiment.label,
            "object": experiment,
        }

    result = project.map(test_func_valid, level=MappingLevel.EXPERIMENT)
    assert result == {
        "/data/archive/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001": {
            "label": "dummydicomsession",
            "one": [1, 2, 3],
            "two": "three",
            "four": None,
            "five": {"foo": False, "bar": True},
        }
    }

    result = project.map(test_func_valid, level=MappingLevel.EXPERIMENT, logfile=log_file1)
    assert result == {
        "/data/archive/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001": {
            "label": "dummydicomsession",
            "one": [1, 2, 3],
            "two": "three",
            "four": None,
            "five": {"foo": False, "bar": True},
        }
    }

    # Validate that this works as long as no logfile is used
    result = project.map(test_func_invalid, level=MappingLevel.EXPERIMENT)
    assert len(result) == 1
    assert list(result.keys()) == [
        "/data/archive/projects/dummydicomproject/subjects/Xnat4Tests_S00001/experiments/Xnat4Tests_E00001"
    ]

    value = list(result.values())[0]
    assert value["label"] == "dummydicomsession"
    assert isinstance(value["object"], xnat4tests_connection.classes.MrSessionData)

    # Validate that this cannot work with the logfile and a correct error is raised
    with pytest.raises(
        TypeError, match="The result of the function is of incompatible with the map function logfile.*"
    ):
        project.map(test_func_invalid, level=MappingLevel.EXPERIMENT, logfile=log_file2)
