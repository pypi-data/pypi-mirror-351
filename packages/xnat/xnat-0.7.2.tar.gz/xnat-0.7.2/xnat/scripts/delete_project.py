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

from requests.exceptions import ReadTimeout

from xnat.exceptions import XNATResponseError


def read_description():
    print("Enter/Paste your the project description. Ctrl-D or Ctrl-Z ( windows ) to save it.")
    project_description = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        project_description.append(line)
    project_description = "\r\n".join(project_description).strip()
    return project_description


def delete_object(xnat_object, dry_run_false):
    object_type = str(type(xnat_object)).split(".")[-1]
    if "ProjectData" in object_type or "ScanData" in object_type:
        object_label = xnat_object.id
    else:
        object_label = xnat_object.label
    print(f"Deleting '{object_label}' ({object_type})")
    try:
        if dry_run_false:
            xnat_object.delete()
            print(f"Deleted object: {object_label}")
        else:
            print(f"[DRYRUN] delete object: {object_label}")
    except (XNATResponseError, ReadTimeout):
        print(f"Error deleting object: {object_label}")
