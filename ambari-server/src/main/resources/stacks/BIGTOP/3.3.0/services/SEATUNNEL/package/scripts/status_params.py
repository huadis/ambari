#!/usr/bin/env python
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

from ambari_commons.os_check import OSCheck
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions import format
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.version import format_stack_version
from resource_management.libraries.script.script import Script

# a map of the Ambari role to the component name
# for use with <stack-root>/current/<component>
# TODO: add the map to the current with the actual
SERVER_ROLE_DIRECTORY_MAP = {
    "SEATUNNEL_HOME": "seatunnel-client",
}

component_directory = Script.get_component_from_role(
    SERVER_ROLE_DIRECTORY_MAP, "SEATUNNEL_HOME"
)

config = Script.get_config()


stack_version_unformatted = str(config["clusterLevelParams"]["stack_version"])
stack_version_formatted = format_stack_version(stack_version_unformatted)
stack_root = Script.get_stack_root()

seatunnel_config_dir = "/etc/seatunnel/conf"

stack_name = default("/clusterLevelParams/stack_name", None)
