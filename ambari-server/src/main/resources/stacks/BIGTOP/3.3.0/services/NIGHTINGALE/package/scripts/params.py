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

import socket
import os
from urllib.parse import urlparse

from ambari_commons.constants import AMBARI_SUDO_BINARY
from resource_management import *
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.constants import StackFeature
from resource_management.libraries.functions import conf_select, stack_select
from resource_management.libraries.functions.version import (
    format_stack_version,
    get_major_version,
)
from resource_management.libraries.functions.copy_tarball import (
    get_sysprep_skip_copy_tarballs_hdfs,
)
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.functions.get_not_managed_resources import (
    get_not_managed_resources,
)
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.copy_tarball import get_current_version
from resource_management.libraries.functions.stack_features import (
    check_stack_feature,
    get_stack_feature_version,
)
from resource_management.libraries.functions import StackFeature


config = Script.get_config()

java_home = config["ambariLevelParams"]["java_home"]
ambari_java_home = default("/ambariLevelParams/ambari_java_home", None)
# not supporting 32 bit jdk.

stack_root = Script.get_stack_root()

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()
sudo = AMBARI_SUDO_BINARY
fqdn = socket.getfqdn().lower()

retryAble = default("/commandParams/command_retry_enabled", False)

cluster_name = config["clusterName"]
stack_name = default("/clusterLevelParams/stack_name", None)
stack_root = Script.get_stack_root()
# 3.2
stack_version_unformatted = config["clusterLevelParams"]["stack_version"]
# 3.2.0.0
stack_version_formatted = format_stack_version(stack_version_unformatted)
# 3.2
major_stack_version = get_major_version(stack_version_formatted)

# 3.2.1.0-001
effective_version = get_current_version(service="GLUTEN")

sysprep_skip_copy_tarballs_hdfs = get_sysprep_skip_copy_tarballs_hdfs()

# New Cluster Stack Version that is defined during the RESTART of a Stack Upgrade
version = default("/commandParams/version", None)
user_group = config["configurations"]["cluster-env"]["user_group"]


############### nightingale ####################
component_directory = "nightingale"
nightingale_home = format("{stack_root}/current/{component_directory}")
nightingale_conf_dir = format("{stack_root}/current/{component_directory}/etc")

nightingale_conf = config["configurations"]["nightingale"]

nightingale_group = config["configurations"]["nightingale-env"]["nightingale_group"]
nightingale_user = config["configurations"]["nightingale-env"]["nightingale_user"]

nightingale_log_dir = config["configurations"]["nightingale-env"]["nightingale_log_dir"]
nightingale_pid_dir = config["configurations"]["nightingale-env"]["nightingale_pid_dir"]
nightingale_pid_file = f"{nightingale_pid_dir}/nightingale.pid"

nightingale_pid_cmd = (
    "echo `ps -A -o pid,command | grep -v  grep | grep n9e | awk '{print $1; exit}'`> "
    + nightingale_pid_file
)

nightingale_test_cmd = (
    "ps -A -o pid,command | grep -v  grep | grep n9e | awk '{print $1; exit}'"
)
# list for array section headers in toml config
array_headers = ["Pushgw.Writers", "writers"]

database_type = config["configurations"]["nightingale-env"]["nightingale.database.type"]
database_password = config["configurations"]["nightingale-env"][
    "nightingale.database.password"
]
database_name = config["configurations"]["nightingale-env"]["nightingale.database.name"]
database_host = config["configurations"]["nightingale-env"]["nightingale.database.host"]
database_port = config["configurations"]["nightingale-env"]["nightingale.database.port"]
database_username = config["configurations"]["nightingale-env"][
    "nightingale.database.username"
]


nightingale_init_sql_path = f"{nightingale_home}/a-n9e-for-Postgres.sql"
nightingale_port = nightingale_conf["HTTP.Port"]

# postgres: host=%s port=%s user=%s dbname=%s password=%s sslmode=%s
# postgres: DSN="host=127.0.0.1 port=5432 user=root dbname=n9e_v6 password=1234 sslmode=disable"
# sqlite: DSN="/path/to/filename.db"
# DSN = "root:1234@tcp(127.0.0.1:3306)/n9e_v6?charset=utf8mb4&parseTime=True&loc=Local&allowNativePasswords=true"
if "mysql" == database_type:
    sql_client = "mysql"
    nightingale_database_url = f"{database_username}:{database_password}@tcp({database_host}:{database_port})/{database_name}?charset=utf8mb4&parseTime=True&loc=Local&allowNativePasswords=true"
    # mysql -h hostname -P port -u username -p'password' dinky_database_name < /path/to/file.sql

    init_sql = f"{sql_client} -h {database_host} -P {database_port}  -u {database_username} -p'{database_password}'  {database_name}  < {nightingale_init_sql_path}"
else:
    sql_client = "psql"
    nightingale_database_url = f"host={database_host} port={database_port} user={database_username} dbname={database_name} password={database_password} sslmode=disable"
    init_sql = f"PGPASSWORD={database_password} {sql_client} -h {database_host} -p {database_port}  -U {database_username}  -d {database_name}  < {nightingale_init_sql_path}"


############### categraf ####################
categraf_component_directory = "categraf"
categraf_home = format("{stack_root}/current/{categraf_component_directory}")
categraf_conf_dir = format("{stack_root}/current/{categraf_component_directory}/conf")

categraf_conf = config["configurations"]["categraf"]

categraf_group = config["configurations"]["categraf-env"]["categraf_group"]
categraf_user = config["configurations"]["categraf-env"]["categraf_user"]

categraf_log_dir = config["configurations"]["categraf-env"]["categraf_log_dir"]
categraf_pid_dir = config["configurations"]["categraf-env"]["categraf_pid_dir"]
categraf_pid_file = f"{categraf_pid_dir}/categraf.pid"

categraf_pid_cmd = (
    "echo `ps -A -o pid,command | grep -v  grep | grep categraf | awk '{print $1; exit}'`> "
    + categraf_pid_file
)

categraf_test_cmd = (
    "ps -A -o pid,command | grep -v  grep | grep categraf | awk '{print $1; exit}'"
)


nightingale_server_hosts = config["clusterHostInfo"]["nightingale_server_hosts"]
nightingale_server_host0 = nightingale_server_hosts[0]
heartbeat_url = f"http://{nightingale_server_host0}:{nightingale_port}/v1/n9e/heartbeat"


############### prometheus ####################
if "victoriametrics" in config["configurations"]:
    victoriametrics_server_host = config["clusterHostInfo"][
        "victoriametrics_server_hosts"
    ][0]
    victoriametrics_server_port = config["configurations"]["victoriametrics"]["port"]
    writer_url = f"http://{victoriametrics_server_host}:{victoriametrics_server_port}/api/v1/write"
    auth_user = config["configurations"]["victoriametrics"]["http_user_name"]
    auth_pwd = config["configurations"]["victoriametrics"]["http_user_password"]
else:
    writer_url = ""
    auth_user = ""
    auth_pwd = ""

hostname = config["agentLevelParams"]["hostname"]
stack_name = default("/hostLevelParams/stack_name", None)
stack_version = config["hostLevelParams"]["stack_version"]
host_name = config["agentLevelParams"]["hostname"]
smoke_user = config["configurations"]["cluster-env"]["smokeuser"]
