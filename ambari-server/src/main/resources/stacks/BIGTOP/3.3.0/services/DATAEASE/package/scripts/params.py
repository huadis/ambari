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
ambari_server_hostname = config['clusterHostInfo']['ambari_server_host'][0]

dataease_home = os.path.join(stack_root, "current", "dataease-server")

dataease_server_port = config['configurations']['dataease-application']['server.port']
dataease_context = config['configurations']['dataease-application']['dataease.context']
dataease_user = config['configurations']['dataease-application']["dataease_user"]
user_group = config["configurations"]["cluster-env"]["user_group"]
dataease_pid_dir = config['configurations']['dataease-application']["dataease_pid_dir"]
dataease_pid_filename = "dataease.pid"
dataease_log_dir = config['configurations']['dataease-application']["dataease_log_dir"]

start_script_name = "app.sh"
start_script_template_file = start_script_name + ".j2"
dataease_bin_dir = dataease_home + "/bin/"
dataease_conf_dir = dataease_home + "/config"

dataease_application_config_file = "application.yml"
dataease_application_config_template_file = dataease_application_config_file + ".j2"

dataease_database_config = {'dataease_database_username': config['configurations']['dataease-application']['spring.datasource.database.username'],
                            'dataease_database_password': config['configurations']['dataease-application']['spring.datasource.database.password'],
                            'dataease_database_url': 'jdbc:mysql://' + config['configurations']['dataease-application']['spring.datasource.database.host'] \
                                                     + ':' + config['configurations']['dataease-application']['spring.datasource.database.port'] \
                                                     + '/' + config['configurations']['dataease-application']['spring.datasource.database.name'] \
                                                     + '?useUnicode=true&characterEncoding=UTF-8'}
