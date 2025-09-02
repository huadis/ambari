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


# server configurations
config = Script.get_config()

stack_root = Script.get_stack_root()
stack_version_unformatted = config["clusterLevelParams"]["stack_version"]
stack_version_formatted_major = format_stack_version(stack_version_unformatted)
major_stack_version = get_major_version(stack_version_formatted_major)

dinky_home = os.path.join(stack_root, "current", "dinky-server")

dinky_server_port = config['configurations']['dinky-application-server']['server.port']
dinky_user = config['configurations']['dinky-application-server']["dinky.user"]
dinky_group = config['configurations']['dinky-application-server']["dinky.group"]
dinky_pid_dir = config['configurations']['dinky-application-server']["dinky.pid.dir"]
dinky_pid_filename = "dinky.pid"
dinky_log_dir = config['configurations']['dinky-application-server']["dinky.log.dir"]

start_script_name = "auto.sh"
start_script_template_file = start_script_name + ".j2"
dinky_bin_dir = dinky_home + "/bin/"
dinky_conf_dir = dinky_home + "/config"

dinky_init_mysql_sqlfile_name = dinky_home + "/sql/dinky-mysql.sql"
dinky_init_pgsql_sqlfile_name = dinky_home + "/sql/dinky-pg.sql"
dinky_application_config_file = "application.yml"
dinky_application_config_template_file = dinky_application_config_file + ".j2"
dinky_application_mysql_config_file = "application-mysql.yml"
dinky_application_mysql_config_template_file = dinky_application_mysql_config_file + ".j2"
dinky_application_pgsql_config_file = "application-pgsql.yml"
dinky_application_pgsql_config_template_file = dinky_application_pgsql_config_file + ".j2"

dinky_database_config = {'dinky_database_type': config['configurations']['dinky-application-server']['spring.datasource.database.type'],
                         'dinky_database_username': config['configurations']['dinky-application-server']['spring.datasource.database.username'],
                         'dinky_database_password': config['configurations']['dinky-application-server']['spring.datasource.database.password']}

if 'mysql' == dinky_database_config['dinky_database_type']:
    dinky_database_config['dinky_database_driver'] = 'com.mysql.jdbc.Driver'
    dinky_database_config['dinky_database_url'] = 'jdbc:mysql://' + config['configurations']['dinky-application-server']['spring.datasource.database.host'] \
                                                  + ':' + config['configurations']['dinky-application-server']['spring.datasource.database.port'] \
                                                  + '/' + config['configurations']['dinky-application-server']['spring.datasource.database.name'] \
                                                  + '?useUnicode=true&characterEncoding=UTF-8'
else:
    dinky_database_config['dinky_database_driver'] = 'org.postgresql.Driver'
    dinky_database_config['dinky_database_url'] = 'jdbc:postgresql://' + config['configurations']['dinky-application-server']['spring.datasource.database.host'] \
                                                  + ':' + config['configurations']['dinky-application-server']['spring.datasource.database.port'] \
                                                  + '/' + config['configurations']['dinky-application-server']['spring.datasource.database.name'] \
                                                  + '?stringtype=unspecified'


dinky_flink_major_version = config['configurations']['dinky-application-server']['flink.major.version']
