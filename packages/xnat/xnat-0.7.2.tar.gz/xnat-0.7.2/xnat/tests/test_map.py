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

import logging
import re
import time

from xnat.map import MappingLevel, MappingObjectStates, StackEntry


def test_mapping_object_state_stack(dummy_object):
    logger = logging.getLogger()
    states = MappingObjectStates(logger=logger)

    # Check if descending manages the stack properly and entries are pushed and popped at the correct moment
    assert states._stack == []

    with states.descend(dummy_object, MappingLevel.PROJECT):
        project_stack_entry = StackEntry(xnat_object=dummy_object, level=MappingLevel.PROJECT)
        experiment_stack_entry = StackEntry(xnat_object=dummy_object, level=MappingLevel.EXPERIMENT)

        assert states._stack == [project_stack_entry]

        with states.descend(dummy_object, MappingLevel.EXPERIMENT):
            assert states._stack == [project_stack_entry, experiment_stack_entry]

        assert states._stack == [project_stack_entry]

    assert states._stack == []


def test_mapping_object_state_fail(dummy_object):
    logger = logging.getLogger()
    states = MappingObjectStates(logger=logger)

    # Check if failing marks the correct stack items as failed, if an item is marked as failed, the entire
    # stack gets marked failed, but when descending the new stack items won't be marked as failed (yet)
    assert states._stack == []

    with states.descend(dummy_object, MappingLevel.PROJECT):
        project_stack_entry = StackEntry(xnat_object=dummy_object, level=MappingLevel.PROJECT)
        project_stack_entry_failed = StackEntry(xnat_object=dummy_object, level=MappingLevel.PROJECT, success=False)
        experiment_stack_entry = StackEntry(xnat_object=dummy_object, level=MappingLevel.EXPERIMENT)
        experiment_stack_entry_failed = StackEntry(
            xnat_object=dummy_object, level=MappingLevel.EXPERIMENT, success=False
        )

        assert states._stack == [project_stack_entry]

        with states.descend(dummy_object, MappingLevel.EXPERIMENT):
            assert states._stack == [project_stack_entry, experiment_stack_entry]

            states.failed(dummy_object)

            assert states._stack == [project_stack_entry_failed, experiment_stack_entry_failed]

        with states.descend(dummy_object, MappingLevel.EXPERIMENT):
            assert states._stack == [project_stack_entry_failed, experiment_stack_entry]

        assert states._stack == [project_stack_entry_failed]

    assert states._stack == []


def perform_descends(states, create_object):
    dummy_project = create_object("/projects/dummy_project")
    dummy_subject1 = create_object("/projects/dummy_project/subjects/dummy_sub1")
    dummy_subject2 = create_object("/projects/dummy_project/subjects/dummy_sub2")
    dummy_exp1 = create_object("/projects/dummy_project/subjects/dummy_sub1/experiments/dummy1")
    dummy_exp2 = create_object("/projects/dummy_project/subjects/dummy_sub2/experiments/dummy2")
    dummy_exp3 = create_object("/projects/dummy_project/subjects/dummy_sub3/experiments/dummy3")
    dummy_exp0 = create_object("/projects/dummy_project/subjects/dummy_sub3/experiments/dummy0")

    with states.descend(dummy_project, MappingLevel.PROJECT):
        with states.descend(dummy_subject1, MappingLevel.SUBJECT):
            states.success(dummy_exp1, result={"label": "dummy1", "id": 1}, requested=True)
            states.failed(dummy_exp2, result={"label": "dummy2", "error": "failed"}, requested=True)
        with states.descend(dummy_subject2, MappingLevel.SUBJECT):
            states.success(dummy_exp3, result={"label": "dummy3", "id": 3}, requested=True)

    # Make sure the correct states as set
    assert states.succeeded(dummy_exp1)
    assert not states.succeeded(dummy_exp2)
    assert states.succeeded(dummy_exp3)

    # Check if not visited object is not succeeded
    assert not states.succeeded(dummy_exp0)


def test_mapping_object_state_result(dummy_object_generator):
    logger = logging.getLogger()
    states = MappingObjectStates(logger=logger)

    perform_descends(states, dummy_object_generator)

    # Check requested results
    result = {x.uri: x.result for x in states.values() if x.requested}
    assert result == {
        "/projects/dummy_project/subjects/dummy_sub1/experiments/dummy1": {"id": 1, "label": "dummy1"},
        "/projects/dummy_project/subjects/dummy_sub2/experiments/dummy2": {"error": "failed", "label": "dummy2"},
        "/projects/dummy_project/subjects/dummy_sub3/experiments/dummy3": {"id": 3, "label": "dummy3"},
    }

    # Check all results
    result = {x.uri: x.result for x in states.values()}
    assert result == {
        "/projects/dummy_project": None,
        "/projects/dummy_project/subjects/dummy_sub1": None,
        "/projects/dummy_project/subjects/dummy_sub1/experiments/dummy1": {"id": 1, "label": "dummy1"},
        "/projects/dummy_project/subjects/dummy_sub2": None,
        "/projects/dummy_project/subjects/dummy_sub2/experiments/dummy2": {"error": "failed", "label": "dummy2"},
        "/projects/dummy_project/subjects/dummy_sub3/experiments/dummy3": {"id": 3, "label": "dummy3"},
    }

    # Check if there are 6 entries in states
    assert (len(states)) == 6

    # Remove one item
    del states["/projects/dummy_project/subjects/dummy_sub1/experiments/dummy1"]
    assert (len(states)) == 5


FILE_CONTENTS_STEP_1 = r"""- date: '\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d+'
  requested: true
  result:
    id: 1
    label: dummy1
  success: true
  uri: /projects/dummy_project/subjects/dummy_sub1/experiments/dummy1"""

FILE_CONTENTS_STEP_2 = (
    FILE_CONTENTS_STEP_1
    + r"""
- date: '\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d+'
  requested: true
  result:
    error: failed
    label: dummy2
  success: false
  uri: /projects/dummy_project/subjects/dummy_sub1/experiments/dummy2"""
)

FILE_CONTENTS_STEP_3 = (
    FILE_CONTENTS_STEP_2
    + r"""
- date: '\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d+'
  requested: false
  result: null
  success: false
  uri: /projects/dummy_project/subjects/dummy_sub1"""
)

FILE_CONTENTS_STEP_4 = (
    FILE_CONTENTS_STEP_3
    + r"""
- date: '\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d+'
  requested: false
  result: null
  success: false
  uri: /projects/dummy_project
"""
)


def test_mapping_object_state_file(tmp_path, dummy_object_generator, caplog):
    caplog.set_level(logging.DEBUG)
    logger = logging.getLogger()

    logfile = tmp_path / "map_log.yaml"

    states = MappingObjectStates(logger=logger, filename=str(logfile))

    dummy_project = dummy_object_generator("/projects/dummy_project")
    dummy_subject1 = dummy_object_generator("/projects/dummy_project/subjects/dummy_sub1")
    dummy_exp1 = dummy_object_generator("/projects/dummy_project/subjects/dummy_sub1/experiments/dummy1")
    dummy_exp2 = dummy_object_generator("/projects/dummy_project/subjects/dummy_sub1/experiments/dummy2")

    # Log file should not exist yet
    assert not logfile.is_file()
    with states.descend(dummy_project, MappingLevel.PROJECT):
        assert not logfile.is_file()
        with states.descend(dummy_subject1, MappingLevel.SUBJECT):
            assert not logfile.is_file()

            states.success(dummy_exp1, result={"label": "dummy1", "id": 1}, requested=True)
            assert re.match(FILE_CONTENTS_STEP_1, logfile.read_text())

            states.failed(dummy_exp2, result={"label": "dummy2", "error": "failed"}, requested=True)
            assert re.match(FILE_CONTENTS_STEP_2, logfile.read_text())

        assert re.match(FILE_CONTENTS_STEP_3, logfile.read_text())

    assert re.match(FILE_CONTENTS_STEP_4, logfile.read_text())

    # Load the states file into a new states object
    states_loaded = MappingObjectStates(logger=logger, filename=str(logfile))

    result = {x.uri: x.result for x in states_loaded.values()}
    assert result == {
        "/projects/dummy_project": None,
        "/projects/dummy_project/subjects/dummy_sub1": None,
        "/projects/dummy_project/subjects/dummy_sub1/experiments/dummy1": {"id": 1, "label": "dummy1"},
        "/projects/dummy_project/subjects/dummy_sub1/experiments/dummy2": {"error": "failed", "label": "dummy2"},
    }
    # Check if there are 4 entries in states, remove one and check again
    assert (len(states)) == 4
    del states["/projects/dummy_project"]
    assert (len(states)) == 3

    # Check if file is rewriten properly
    assert re.match(FILE_CONTENTS_STEP_3, logfile.read_text())
