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

import contextlib
import dataclasses
import enum
import logging
from collections.abc import MutableMapping
from datetime import datetime
from pathlib import Path
from typing import Any, Union

import yaml

from .core import XNATBaseObject
from .type_hints import JSONType


def check_result_type(value: Any) -> bool:
    if value is None:
        return True

    if isinstance(value, (int, str, bool)):
        return True

    if isinstance(value, list):
        return all(check_result_type(x) for x in value)

    if isinstance(value, dict):
        if not all(isinstance(x, str) for x in value.keys()):
            return False

        return all(check_result_type(x) for x in value.values())

    return False


class MappingLevel(str, enum.Enum):
    CONNECTION = "connection"
    PROJECT = "project"
    PROJECT_RESOURCE = "project_resource"
    SUBJECT = "subject"
    SUBJECT_RESOURCE = "subject_resource"
    EXPERIMENT = "experiment"
    EXPERIMENT_RESOURCE = "experiment_resource"
    SCAN = "scan"
    SCAN_RESOURCE = "scan_resource"


@dataclasses.dataclass
class StackEntry:
    xnat_object: XNATBaseObject
    level: MappingLevel
    success: bool = True


@dataclasses.dataclass
class MappingState:
    uri: str
    success: bool
    result: JSONType
    date: str = datetime.now().isoformat()
    requested: bool = False


class MappingObjectStates(MutableMapping):
    def __init__(self, logger: logging.Logger, filename: Union[str, Path] = None):
        if isinstance(filename, str):
            filename = Path(filename)

        self.filename = filename
        self.logger = logger
        self.states: dict[str, MappingState] = {}
        if self.filename and self.filename.is_file():
            state = yaml.safe_load(self.filename.read_text())
            if state:
                self.states = {x["uri"]: MappingState(**x) for x in state}

        self._stack: list[StackEntry] = []

    def __getitem__(self, key):
        return self.states[key]

    def __setitem__(self, key, value: MappingState):
        if key in self.states:
            self.logger.debug(f"Updating key: {key}")
            self.logger.debug(f"Orignal value: {self.states[key]}")
            self.logger.debug(f"New     value: {value}")
            self.states[key] = value
            self._rewrite_file()
        else:
            self.states[key] = value
            self._append_to_file(key)

    def __delitem__(self, key):
        self.logger.debug(f"Deleting key: {key}")
        self.states.__delitem__(key)
        self._rewrite_file()

    def __iter__(self):
        return iter(self.states)

    def __len__(self):
        return len(self.states)

    def _dump_states(self):
        return [dataclasses.asdict(v) for v in self.states.values()]

    def _rewrite_file(self):
        self.logger.debug(f"ReWriting: {self.filename}")
        if self.filename:
            states = self._dump_states()
            self.filename.write_text(yaml.dump(states, indent=2))

    def _append_to_file(self, key):
        if self.filename:
            self.logger.debug(f"Add key: {key} to filename: {self.filename}")
            with open(self.filename, "a") as fo:
                state = dataclasses.asdict(self.states[key])
                fo.write(yaml.dump([state], indent=2))

    @contextlib.contextmanager
    def descend(self, xnat_object: XNATBaseObject, level: MappingLevel):
        entry = StackEntry(xnat_object=xnat_object, level=level)
        self._stack.append(entry)
        yield self
        removed = self._stack.pop()

        if removed.success:
            self.success(removed.xnat_object, None)
        else:
            self.failed(removed.xnat_object)

    def succeeded(self, obj):
        state = self.get(obj.fulluri, None)

        if state is None:
            return False

        return state.success

    def success(self, obj, result, requested: bool = False):
        self[obj.fulluri] = MappingState(uri=obj.fulluri, success=True, result=result, requested=requested)

    def failed(self, obj, result=None, requested: bool = False):
        # Mark this stack as failed, including parents
        for item in self._stack:
            item.success = False

        self[obj.fulluri] = MappingState(uri=obj.fulluri, success=False, result=result, requested=requested)
