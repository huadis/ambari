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

import os

from resource_management import *


# server configurations
config = Script.get_config()

stack_root = Script.get_stack_root()
stack_version_unformatted = config["clusterLevelParams"]["stack_version"]
stack_version_formatted_major = format_stack_version(stack_version_unformatted)
major_stack_version = get_major_version(stack_version_formatted_major)

gravitino_home = os.path.join(stack_root, "current", "gravitino-server")

gravitino_env_map = {}
gravitino_env_map.update(config["configurations"]["gravitino-env"])
gravitino_env_content = gravitino_env_map["env-content"]
gravitino_env_path = gravitino_home + "/conf/gravitino-env.sh"

gravitino_log4j_map = {}
gravitino_log4j_map.update(config["configurations"]["gravitino-log4j"])
gravitino_log4j_content = gravitino_log4j_map["log4j-content"]
gravitino_log4j_path = gravitino_home + "/conf/log4j2.properties"

gravitino_pid_dir = "/var/run/gravitino"
gravitino_pid_filename = "gravitino.pid"
gravitino_log_dir = "/var/log/gravitino"

gravitino_user = gravitino_env_map["gravitino.user"]
gravitino_group = gravitino_env_map["gravitino.group"]

gravitino_conf_map = {}
gravitino_conf_map.update(config["configurations"]["gravitino-httpserver"])
gravitino_conf_map.update(config["configurations"]["gravitino-storage"])
gravitino_conf_map.update(config["configurations"]["gravitino-cache"])

gravitino_conf_name = "gravitino.conf"
gravitino_conf_template_name = gravitino_conf_name + ".j2"
gravitino_conf_dir = gravitino_home + "/conf"
gravitino_sh_name = "gravitino.sh"
gravitino_sh_template_name = gravitino_sh_name + ".j2"
gravitino_bin_dir = gravitino_home + "/bin"

gravitino_tools_config_name = "config.yaml"
gravitino_tools_config_template_name = gravitino_tools_config_name + ".j2"
gravitino_tools_config_path = gravitino_home + "/tools/" + gravitino_tools_config_name

gravitino_database_config = {'gravitino_database_type': 'mysql',
                              'gravitino_database_username': gravitino_conf_map['gravitino.entity.store.relational.jdbcUser'],
                              'gravitino_database_password': gravitino_conf_map['gravitino.entity.store.relational.jdbcPassword'],
                              'gravitino_database_url': gravitino_conf_map['gravitino.entity.store.relational.jdbcUrl']}
