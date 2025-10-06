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

from random import lognormvariate
from resource_management import *
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.expect import expect
from resource_management.libraries.functions.get_architecture import get_architecture
from resource_management.libraries.functions.stack_features import (
    check_stack_feature,
    get_stack_feature_version,
)
import os
import status_params
from resource_management.libraries.functions.setup_ranger_plugin_xml import (
    generate_ranger_service_config,
)
from resource_management.libraries.functions.setup_ranger_plugin_xml import (
    get_audit_configs,
)
from ambari_commons.constants import AMBARI_SUDO_BINARY
import sys
from resource_management.core.logger import Logger
from resource_management.libraries.functions import default
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions import conf_select, stack_select
from resource_management.libraries.functions.get_not_managed_resources import (
    get_not_managed_resources,
)


sudo = AMBARI_SUDO_BINARY

# server configurations
config = Script.get_config()
Logger.info("Default system config:" + str(config))

service_packagedir = os.path.realpath(__file__).split("/scripts")[0]
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

architecture = get_architecture()

# Stack info
stack_version_unformatted = str(config["clusterLevelParams"]["stack_version"])
stack_version_formatted = format_stack_version(stack_version_unformatted)
stack_root = Script.get_stack_root()
stack_name = default("/hostLevelParams/stack_name", None)
component_directory = status_params.component_directory
user_group = config["configurations"]["cluster-env"]["user_group"]
seatunnel_home = format("{stack_root}/current/{component_directory}")
seatunnel_conf_dir = format("{stack_root}/current/{component_directory}/config")

ambari_server_hostname = config["ambariLevelParams"]["ambari_server_host"]
current_host_name = config["agentLevelParams"]["hostname"]

# seatunnel Configurations
seatunnel_log_dir_prefix = config["configurations"]["seatunnel-env"][
    "seatunnel_log_dir_prefix"
]
seatunnel_pid_dir_prefix = config["configurations"]["seatunnel-env"][
    "seatunnel_pid_dir_prefix"
]
seatunnel_user = config["configurations"]["seatunnel-env"]["seatunnel_user"]
root_user = "root"


user = seatunnel_user
seatunnel_pid_dir = format("{seatunnel_pid_dir_prefix}/{user}")
seatunnel_log_dir = format("{seatunnel_log_dir_prefix}/{user}")

seatunnel_server_pid_file = format("{seatunnel_pid_dir}/seatunnel-{user}-server.pid")
seatunnel_master_pid_file = format("{seatunnel_pid_dir}/seatunnel-{user}-master.pid")
seatunnel_worker_pid_file = format("{seatunnel_pid_dir}/seatunnel-{user}-worker.pid")


java_home = config["ambariLevelParams"]["java_home"]
java64_home = config["ambariLevelParams"]["java_home"]
java_version = expect("/ambariLevelParams/java_version", int)
java_exec = format("{java_home}/bin/java")

# node hostname
hostname = config["agentLevelParams"]["hostname"]

# seatunnel_server_hosts
seatunnel_server_hosts = config["clusterHostInfo"]["seatunnel_server_hosts"]
seatunnel_port = default("/configurations/seatunnel-hazelcast/hazelcast.port", None)

# seatunnel_marster_hosts
seatunnel_master_hosts = config["clusterHostInfo"]["seatunnel_master_hosts"]
seatunnel_master_port = default(
    "/configurations/seatunnel-hazelcast-master/hazelcast.master.port", "5801"
)

# seatunnel_worker_hosts
seatunnel_worker_hosts = config["clusterHostInfo"]["seatunnel_worker_hosts"]
seatunnel_worker_port = default(
    "/configurations/seatunnel-hazelcast-worker/hazelcast.worker.port", "5802"
)

# get comma separated lists of seatunnel_server_hosts
index = 0
seatunnel_members = []
seatunnel_master_members = []
seatunnel_worker_members = []
for host in seatunnel_master_hosts:
    seatunnel_master_host_port = host
    if seatunnel_master_port is not None:
        seatunnel_master_host_port = host + ":" + str(seatunnel_master_port)
    seatunnel_master_members.append(seatunnel_master_host_port)
    seatunnel_members.append(seatunnel_master_host_port)


for host in seatunnel_worker_hosts:
    seatunnel_worker_host_port = host
    if seatunnel_worker_port is not None:
        seatunnel_worker_host_port = host + ":" + str(seatunnel_worker_port)
    seatunnel_worker_members.append(seatunnel_worker_host_port)
    seatunnel_members.append(seatunnel_worker_host_port)


seatunnel_engine_backup_count = config["configurations"]["seatunnel-seatunnel"][
    "seatunnel.engine.backup-count"
]
seatunnel_slot_service_dynamic_slot = config["configurations"]["seatunnel-seatunnel"][
    "seatunnel.slot-service.dynamic-slot"
]
seatunnel_slot_service_slot_num = config["configurations"]["seatunnel-seatunnel"][
    "seatunnel.slot-service.slot-num"
]

# seatunnel.fs.defaultFS
seatunnel_fs_defaultFS = config["configurations"]["seatunnel-env"][
    "seatunnel.fs.defaultFS"
]
seatunnel_fs_hdfs_path = config["configurations"]["seatunnel-env"][
    "seatunnel.fs.hdfs.path"
]
seatunnel_fs_hdfs_type = config["configurations"]["seatunnel-env"]["seatunnel.fs.type"]

# configurations of HDFS
namenode_hosts = default("/clusterHostInfo/namenode_hosts", [])
namenode_hosts.sort()
namenode_address = None
if "dfs.namenode.rpc-address" in config["configurations"]["hdfs-site"]:
    namenode_rpcaddress = config["configurations"]["hdfs-site"][
        "dfs.namenode.rpc-address"
    ]
    namenode_address = format("hdfs://{namenode_rpcaddress}")
else:
    namenode_address = config["configurations"]["core-site"]["fs.defaultFS"]
# To judge whether the namenode HA mode
logical_name = ""
dfs_ha_enabled = False
dfs_ha_nameservices = default("/configurations/hdfs-site/dfs.nameservices", None)
dfs_ha_namenode_ids = default(
    format("/configurations/hdfs-site/dfs.ha.namenodes.{dfs_ha_nameservices}"), None
)
dfs_ha_namemodes_ids_list = []
if dfs_ha_namenode_ids:
    dfs_ha_namemodes_ids_list = dfs_ha_namenode_ids.split(",")
    dfs_ha_namenode_ids_array_len = len(dfs_ha_namemodes_ids_list)
    if dfs_ha_namenode_ids_array_len > 1:
        dfs_ha_enabled = True
if dfs_ha_enabled:
    namenode_address = format("hdfs://{dfs_ha_nameservices}")
    logical_name = dfs_ha_nameservices
else:
    dfs_namenode_http_address = config["configurations"]["hdfs-site"][
        "dfs.namenode.http-address"
    ]
    webhdfs_url = format("http://" + dfs_namenode_http_address + "/webhdfs/v1")
Logger.info("namenode_address:" + namenode_address)

if seatunnel_fs_hdfs_type.lower() == "hdfs":
    # seatunnel_fs_defaultFS = namenode_address + seatunnel_fs_hdfs_path
    seatunnel_fs_defaultFS = namenode_address


# hdfs
hdfs_user = config["configurations"]["hadoop-env"]["hdfs_user"]
hdfs_principal_name = config["configurations"]["hadoop-env"]["hdfs_principal_name"]
hdfs_user_keytab = config["configurations"]["hadoop-env"]["hdfs_user_keytab"]
user_group = config["configurations"]["cluster-env"]["user_group"]

hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore"
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
default_fs = config["configurations"]["core-site"]["fs.defaultFS"]
hdfs_site = config["configurations"]["hdfs-site"]
hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore"

dfs_type = default("/clusterLevelParams/dfs_type", "")

# configurations of security
kinit_path_local = get_kinit_path(
    default("/configurations/kerberos-env/executable_search_paths", None)
)
security_enabled = config["configurations"]["cluster-env"]["security_enabled"]
if security_enabled:
    _hostname_lowercase = config["agentLevelParams"]["hostname"].lower()
    HTTP_principal = config["configurations"]["hdfs-site"][
        "dfs.web.authentication.kerberos.principal"
    ]
    HTTP_keytab = config["configurations"]["hdfs-site"][
        "dfs.web.authentication.kerberos.keytab"
    ]
    kinit_path = kinit_path_local

import functools

# create partial functions with common arguments for every HdfsResource call
# to create/delete hdfs directory/file/copyfromlocal we need to call params.HdfsResource in code
HdfsResource = functools.partial(
    HdfsResource,
    user=hdfs_user,
    hdfs_resource_ignore_file=hdfs_resource_ignore_file,
    security_enabled=security_enabled,
    keytab=hdfs_user_keytab,
    kinit_path_local=kinit_path_local,
    hadoop_bin_dir=hadoop_bin_dir,
    hadoop_conf_dir=hadoop_conf_dir,
    principal_name=hdfs_principal_name,
    hdfs_site=hdfs_site,
    default_fs=default_fs,
    immutable_paths=get_not_managed_resources(),
    dfs_type=dfs_type,
)

seatunnel_principal_name = config["configurations"]["seatunnel-env"][
    "seatunnel_user_principal_name"
]
seatunnel_user_keytab = config["configurations"]["seatunnel-env"][
    "seatunnel_user_keytab"
]

# seatunnel web database config
seatunnel_web_database_config = {}
seatunnel_web_database_config["seatunnel_web_database_type"] = config["configurations"][
    "seatunnel-web-application"
]["seatunnel.web.database.type"]
seatunnel_web_database_config["seatunnel_web_database_host"] = config["configurations"][
    "seatunnel-web-application"
]["seatunnel.web.database.host"]
seatunnel_web_database_config["seatunnel_web_database_port"] = config["configurations"][
    "seatunnel-web-application"
]["seatunnel.web.database.port"]
seatunnel_web_database_config["seatunnel_web_database_dbname"] = config[
    "configurations"
]["seatunnel-web-application"]["seatunnel.web.database.dbname"]
seatunnel_web_database_config["seatunnel_web_database_username"] = config[
    "configurations"
]["seatunnel-web-application"]["seatunnel.web.database.username"]
seatunnel_web_database_config["seatunnel_web_database_password"] = config[
    "configurations"
]["seatunnel-web-application"]["seatunnel.web.database.password"]
seatunnel_web_database_config["seatunnel_web_database_args"] = config["configurations"][
    "seatunnel-web-application"
]["seatunnel.web.database.args"]
if "mysql" == seatunnel_web_database_config["seatunnel_web_database_type"]:
    seatunnel_web_database_config["seatunnel_web_database_driver"] = (
        "com.mysql.jdbc.Driver"
    )
    seatunnel_web_database_config["seatunnel_web_database_url"] = (
        "jdbc:mysql://"
        + seatunnel_web_database_config["seatunnel_web_database_host"]
        + ":"
        + seatunnel_web_database_config["seatunnel_web_database_port"]
        + "/"
        + seatunnel_web_database_config["seatunnel_web_database_dbname"]
        + "?"
        + seatunnel_web_database_config["seatunnel_web_database_args"]
    )
#  + '?useUnicode=true&characterEncoding=UTF-8'
else:
    seatunnel_web_database_config["seatunnel_web_database_driver"] = "not config"
    seatunnel_web_database_config["seatunnel_web_database_url"] = "not config"


seatunnel_web_home = format("{stack_root}/current/seatunnel-web")
seatunnel_web_conf_dir = format("{stack_root}/current/seatunnel-web/conf")
seatunnel_web_bin_dir = format("{stack_root}/current/seatunnel-web/bin")
seatunnel_web_pid_file = format("{seatunnel_pid_dir}/seatunnel-{user}-web.pid")
