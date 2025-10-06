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

import sys
from resource_management import *
from resource_management.core.logger import Logger
from resource_management.libraries.functions import default
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions import conf_select, stack_select
from resource_management.libraries.functions.get_not_managed_resources import (
    get_not_managed_resources,
)
import importlib


Logger.initialize_logger()
# server configurations
config = Script.get_config()

# conf_dir = "/etc/"
dolphin_home = "/usr/bigtop/current/dolphinscheduler"
# dolphin_conf_dir = dolphin_home + "/conf"
# dolphin_log_dir = dolphin_home + "/logs"
dolphin_bin_dir = dolphin_home + "/bin"

# dolphin_pidfile_dir = "/var/run/dolphinscheduler"


rmHosts = default("/clusterHostInfo/rm_host", [])

# dolphin-env
dolphin_env_map = {}
dolphin_env_map.update(config["configurations"]["dolphin-env"])

# which user to install and admin dolphin scheduler
dolphin_user = dolphin_env_map["dolphin.user"]
dolphin_group = dolphin_env_map["dolphin.group"]

# dolphinscheduler conf
dolphin_alert_server_conf_dir = dolphin_home + "/alert-server/conf"
dolphin_api_server_conf_dir = dolphin_home + "/api-server/conf"
dolphin_master_server_conf_dir = dolphin_home + "/master-server/conf"
dolphin_worker_server_conf_dir = dolphin_home + "/worker-server/conf"
dolphin_tools_conf_dir = dolphin_home + "/tools/conf"


# .dolphinscheduler_env.sh
dolphin_env_path = dolphin_home + "/bin/env/dolphinscheduler_env.sh"
dolphin_env_content = dolphin_env_map["dolphinscheduler-env-content"]


# database config
dolphin_database_config = {}
dolphin_database_config["dolphin_database_type"] = dolphin_env_map[
    "dolphin.database.type"
]
dolphin_database_config["dolphin_database_username"] = dolphin_env_map[
    "dolphin.database.username"
]
dolphin_database_config["dolphin_database_password"] = dolphin_env_map[
    "dolphin.database.password"
]
if "mysql" == dolphin_database_config["dolphin_database_type"]:
    dolphin_database_config["dolphin_database_driver"] = "com.mysql.jdbc.Driver"
    dolphin_database_config["dolphin_database_url"] = (
        "jdbc:mysql://"
        + dolphin_env_map["dolphin.database.host"]
        + ":"
        + dolphin_env_map["dolphin.database.port"]
        + "/dolphinscheduler?useUnicode=true&characterEncoding=UTF-8"
    )
elif "postgresql" == dolphin_database_config["dolphin_database_type"]:
    dolphin_database_config["dolphin_database_driver"] = "org.postgresql.Driver"
    dolphin_database_config["dolphin_database_url"] = (
        "jdbc:postgresql://"
        + dolphin_env_map["dolphin.database.host"]
        + ":"
        + dolphin_env_map["dolphin.database.port"]
        + "/dolphinscheduler"
    )
elif "opengauss" == dolphin_database_config["dolphin_database_type"]:
    dolphin_database_config["dolphin_database_driver"] = "org.opengauss.Driver"
    dolphin_database_config["dolphin_database_url"] = (
        "jdbc:opengauss://"
        + dolphin_env_map["dolphin.database.host"]
        + ":"
        + dolphin_env_map["dolphin.database.port"]
        + "/dolphinscheduler"
    )

# alert-server/conf/application.yaml
dolphin_alert_server_application_map = {}
dolphin_alert_server_application_map.update(
    config["configurations"]["dolphin-alert-server-application"]
)

# api-server/conf/application.yaml
dolphin_api_server_application_map = {}
dolphin_api_server_application_map.update(
    config["configurations"]["dolphin-api-server-application"]
)

# api-server/conf/application.yaml
dolphin_master_server_application_map = {}
dolphin_master_server_application_map.update(
    config["configurations"]["dolphin-master-server-application"]
)

# worker-server/conf/application.yaml
dolphin_worker_server_application_map = {}
dolphin_worker_server_application_map.update(
    config["configurations"]["dolphin-worker-server-application"]
)


# Cluster Zookeeper quorum
zookeeper_quorum = None

Logger.info("zookeeper_server_hosts:")
Logger.info(str(len(default("/clusterHostInfo/zookeeper_server_hosts", []))))

if not len(default("/clusterHostInfo/zookeeper_server_hosts", [])) == 0:
    if (
        "zoo.cfg" in config["configurations"]
        and "clientPort" in config["configurations"]["zoo.cfg"]
    ):
        zookeeper_clientPort = config["configurations"]["zoo.cfg"]["clientPort"]
    else:
        zookeeper_clientPort = "2181"
    zookeeper_quorum = (":" + zookeeper_clientPort + ",").join(
        config["clusterHostInfo"]["zookeeper_server_hosts"]
    )
    # last port config
    zookeeper_quorum += ":" + zookeeper_clientPort

Logger.info("zookeeper_quorum:" + zookeeper_quorum)

java_home = config["ambariLevelParams"]["java_home"]
ambari_java_home = default("/ambariLevelParams/ambari_java_home", None)
# not supporting 32 bit jdk.
java64_home = java_home


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
    zk_principal = config["configurations"]["zookeeper-env"][
        "zookeeper_principal_name"
    ].replace("_HOST", _hostname_lowercase)
    zk_keytab = config["configurations"]["zookeeper-env"]["zookeeper_principal_name"]


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


# common.properties
dolphin_common_map = {}
dolphin_common_map.update(config["configurations"]["dolphin-common"])

if (
    "yarn-site" in config["configurations"]
    and "yarn.resourcemanager.webapp.address" in config["configurations"]["yarn-site"]
):
    yarn_resourcemanager_webapp_address = config["configurations"]["yarn-site"][
        "yarn.resourcemanager.webapp.address"
    ]
    yarn_application_status_address = (
        "http://" + yarn_resourcemanager_webapp_address + "/ws/v1/cluster/apps/%s"
    )
    dolphin_common_map["yarn.application.status.address"] = (
        yarn_application_status_address
    )

rmHosts = default("/clusterHostInfo/rm_host", [])
if len(rmHosts) > 1:
    dolphin_common_map["yarn.resourcemanager.ha.rm.ids"] = ",".join(rmHosts)
else:
    dolphin_common_map["yarn.resourcemanager.ha.rm.ids"] = ""

dolphin_common_map_tmp = config["configurations"]["dolphin-common"]
data_basedir_path = dolphin_common_map_tmp["data.basedir.path"]
dolphin_common_map["dolphinscheduler.env.path"] = dolphin_env_path

dolphin_common_map["resource.hdfs.fs.defaultFS"] = namenode_address

Logger.info("namenode_address:" + namenode_address)
# Logger.info('namenode_address2:' + config['configurations']['dolphin-common']['resource.hdfs.fs.defaultFS'])

# resource.storage
resource_storage_type = config["configurations"]["dolphin-common"][
    "resource.storage.type"
]
resource_storage_upload_base_path = config["configurations"]["dolphin-common"][
    "resource.storage.upload.base.path"
]


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

dolphinExecEnv = {"JAVA_HOME": java_home, "HADOOP_CONF_DIR": hadoop_conf_dir}
