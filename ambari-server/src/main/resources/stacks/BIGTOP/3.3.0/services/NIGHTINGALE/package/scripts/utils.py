#!/usr/bin/env python3
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from resource_management.core.source import StaticFile, Template, InlineTemplate


def dict_to_toml_string(input_dict, array_headers=None):
    if array_headers is None:
        array_headers = set()
    toml_lines = []
    section_lines = {}
    for key, value in input_dict.items():
        # Split the key by '.' to handle nested structures
        keys = key.split(".")
        if len(keys) > 1:
            section = ".".join(
                keys[:-1]
            )  # Use all but the last element for the section
            if section not in section_lines:
                section_lines[section] = []

            # Determine how to represent the value
            if isinstance(value, str):
                # Check if the value is a boolean or a number in string form
                if value.lower() in ["true", "false"]:
                    value_repr = value.lower()
                elif is_number(value):
                    value_repr = value
                elif value.startswith("[") and value.endswith("]"):
                    value_repr = value
                else:
                    value_repr = repr(value)
            else:
                value_repr = value
            value_repr = InlineTemplate(value_repr).get_content()
            section_lines[section].append(f"{keys[-1]} = {value_repr}")

    for section, lines in section_lines.items():
        # Check if the section should be an array
        if section in array_headers:
            toml_lines.append(f"[[{section}]]")
        else:
            toml_lines.append(f"[{section}]")
        toml_lines.extend(lines)

    return "\n".join(toml_lines)


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
