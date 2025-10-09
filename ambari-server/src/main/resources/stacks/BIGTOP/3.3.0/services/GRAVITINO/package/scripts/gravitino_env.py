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

from resource_management import *


def gravitino_env():
    import params

    File(
        format(params.gravitino_env_path),
        mode=0o755,
        content=InlineTemplate(params.gravitino_env_content),
        owner=params.gravitino_user,
        group=params.gravitino_group,
    )

    File(format(params.gravitino_conf_dir + "/" + params.gravitino_conf_name),
         mode=0o755,
         content=Template(params.gravitino_conf_template_name),
         owner=params.gravitino_user,
         group=params.gravitino_group
         )

    File(format(params.gravitino_bin_dir + "/" + params.gravitino_sh_name),
         mode=0o755,
         content=Template(params.gravitino_sh_template_name),
         owner=params.gravitino_user,
         group=params.gravitino_group
         )
