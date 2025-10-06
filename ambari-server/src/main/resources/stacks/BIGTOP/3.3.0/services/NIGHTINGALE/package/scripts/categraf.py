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

import os
import sys
from resource_management.libraries.script.script import Script
from resource_management.libraries.resources.xml_config import XmlConfig
from resource_management.libraries.resources.template_config import TemplateConfig
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions import lzo_utils
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.generate_logfeeder_input_config import (
    generate_logfeeder_input_config,
)
from resource_management.core.source import Template, InlineTemplate
from resource_management.core.resources import Package
from resource_management.core.resources.service import ServiceConfig
from resource_management.core.resources.system import Directory, Execute, File
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
from ambari_commons import OSConst
from resource_management.libraries.functions.constants import StackFeature
from resource_management.libraries.functions.stack_features import check_stack_feature
import json
from utils import *


# name is 'master' or 'regionserver' or 'queryserver' or 'client'
@OsFamilyFuncImpl(os_family=OsFamilyImpl.DEFAULT)
def categraf(name=None):
    import params
    import status_params

    Directory(
        [params.categraf_pid_dir, params.categraf_log_dir],
        owner=params.categraf_user,
        group=params.categraf_group,
        mode=0o775,
        create_parents=True,
    )

    File(
        os.path.join(params.categraf_conf_dir, "config.toml"),
        owner=params.categraf_user,
        group=params.categraf_group,
        content=dict_to_toml_string(params.categraf_conf, params.array_headers),
        mode=0o644,
    )
