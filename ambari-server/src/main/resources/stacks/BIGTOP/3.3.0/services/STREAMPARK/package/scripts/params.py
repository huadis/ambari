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

streampark_home = os.path.join(stack_root, "current", "streampark-server")

streampark_server_port = config['configurations']['streampark-application']['server.port']
streampark_user = config['configurations']['streampark-application']["streampark_user"]
user_group = config["configurations"]["cluster-env"]["user_group"]
streampark_pid_dir = config['configurations']['streampark-application']["streampark_pid_dir"]
streampark_pid_filename = "streampark.pid"
streampark_log_dir = config['configurations']['streampark-application']["streampark_log_dir"]

start_script_name = "streampark.sh"
start_script_template_file = start_script_name + ".j2"
streampark_bin_dir = streampark_home + "/bin/"
streampark_conf_dir = streampark_home + "/conf"

streampark_application_config_file = "config.yaml"
streampark_application_config_template_file = streampark_application_config_file + ".j2"

streampark_database_config = {'streampark_database_type': 'mysql',
                              'streampark_database_username': config['configurations']['streampark-application']['spring.datasource.database.username'],
                              'streampark_database_password': config['configurations']['streampark-application']['spring.datasource.database.password'],
                              'streampark_database_url': 'jdbc:mysql://' + config['configurations']['streampark-application']['spring.datasource.database.host'] \
                                                     + ':' + config['configurations']['streampark-application']['spring.datasource.database.port'] \
                                                     + '/' + config['configurations']['streampark-application']['spring.datasource.database.name'] \
                                                     + '?useUnicode=true&characterEncoding=UTF-8'}
