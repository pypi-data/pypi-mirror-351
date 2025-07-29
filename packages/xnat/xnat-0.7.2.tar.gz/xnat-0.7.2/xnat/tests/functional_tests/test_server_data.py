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

pytestmark = [pytest.mark.functional_test, pytest.mark.server_test]


def test_connect(test_server_url):
    from xnat import connect

    with connect(test_server_url) as connection:
        print(f"Connected to {test_server_url}, running version {connection.xnat_version}")


def test_list_projects(test_server_connection):
    print(f"Projects on {test_server_connection.uri}: {test_server_connection.projects}")
