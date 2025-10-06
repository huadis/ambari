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
import subprocess
from resource_management.libraries.functions.setup_ranger_plugin_xml import (
    generate_ranger_service_config,
)
from resource_management.libraries.functions.setup_ranger_plugin_xml import (
    get_audit_configs,
)
import time
import re
from ambari_commons.constants import AMBARI_SUDO_BINARY
from resource_management.libraries.functions import get_kinit_path
from resource_management.libraries.resources.hdfs_resource import HdfsResource
from resource_management.libraries.functions import conf_select, stack_select
from resource_management.libraries.functions.get_not_managed_resources import (
    get_not_managed_resources,
)
import shlex


sudo = AMBARI_SUDO_BINARY

retryAble = default("/commandParams/command_retry_enabled", False)

# New Cluster Stack Version that is defined during the RESTART of a Stack Upgrade
version = default("/commandParams/version", None)

service_packagedir = os.path.realpath(__file__).split("/scripts")[0]
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

architecture = get_architecture()

# Env
hostname = config["agentLevelParams"]["hostname"]

java_home = config["ambariLevelParams"]["java_home"]
java_version = expect("/ambariLevelParams/java_version", int)
java_exec = format("{java_home}/bin/java")

# Stack info
stack_version_unformatted = str(config["clusterLevelParams"]["stack_version"])
stack_version_formatted = format_stack_version(stack_version_unformatted)
stack_root = Script.get_stack_root()
stack_name = default("/hostLevelParams/stack_name", None)
user_group = config["configurations"]["cluster-env"]["user_group"]
doris_home_current = format("{stack_root}/current")

# User & Group
doris_user = config["configurations"]["doris-env"]["doris_user"]
doris_group = config["configurations"]["doris-env"]["doris_group"]

# Bin Dir
# fe bin dir
doris_fe_home = doris_home_current + "/doris-fe"
doris_fe_bin_path = doris_home_current + "/doris-fe/bin"
# be bin dir
doris_be_bin_path = doris_home_current + "/doris-be/bin"
doris_be_lib_path = doris_home_current + "/doris-be/lib"
# broker bin dir
doris_broker_bin_path = doris_home_current + "/doris-hdfs_broker/bin"
# doris client bin dir
doris_client_bin_path = doris_home_current + "/doris-client/bin"

# Conf file path
doris_fe_conf_dir = doris_home_current + "/doris-fe/conf"
doris_be_conf_dir = doris_home_current + "/doris-be/conf"
doris_broker_conf_dir = doris_home_current + "/doris-hdfs_broker/conf"
fe_log_default_dir = "/var/log/doris/fe"
be_log_default_dir = "/var/log/doris/be"

# FE configuration parameters
fe_log_dir = config["configurations"]["doris-fe-conf"]["fe_log_dir"]
fe_temp_dir = config["configurations"]["doris-fe-conf"]["fe_temp_dir"]
java_opts_for_jdk_9 = config["configurations"]["doris-fe-conf"]["java9_opts"]
java8_option = config["configurations"]["doris-fe-conf"]["java8_option"]
fe_sys_log_level = config["configurations"]["doris-fe-conf"]["sys_log_level"]
fe_meta_dir = config["configurations"]["doris-fe-conf"]["fe_meta_dir"]
http_port = config["configurations"]["doris-fe-conf"]["http_port"]
rpc_port = config["configurations"]["doris-fe-conf"]["rpc_port"]
query_port = config["configurations"]["doris-fe-conf"]["query_port"]
fe_query_port = config["configurations"]["doris-fe-conf"]["query_port"]
edit_log_port = config["configurations"]["doris-fe-conf"]["edit_log_port"]
fe_edit_log_port = config["configurations"]["doris-fe-conf"]["edit_log_port"]
qe_max_connection = config["configurations"]["doris-fe-conf"]["qe_max_connection"]
mysql_service_nio_enabled = config["configurations"]["doris-fe-conf"][
    "mysql_service_nio_enabled"
]
enable_batch_delete_by_default = config["configurations"]["doris-fe-conf"][
    "enable_batch_delete_by_default"
]
disable_storage_medium_check = config["configurations"]["doris-fe-conf"][
    "disable_storage_medium_check"
]
default_storage_medium = config["configurations"]["doris-fe-conf"][
    "default_storage_medium"
]
enable_materialized_view = config["configurations"]["doris-fe-conf"][
    "enable_materialized_view"
]
dynamic_partition_enable = config["configurations"]["doris-fe-conf"][
    "dynamic_partition_enable"
]
max_conn_per_user = config["configurations"]["doris-fe-conf"]["max_conn_per_user"]
qe_query_timeout_second = config["configurations"]["doris-fe-conf"][
    "qe_query_timeout_second"
]
fe_root_password = config["configurations"]["doris-fe-conf"]["fe_root_password"]
fe_admin_password = config["configurations"]["doris-fe-conf"]["fe_admin_password"]

# BE configuration parameters
be_log_dir = config["configurations"]["doris-be-conf"]["be_log_dir"]
PPROF_TMPDIR = config["configurations"]["doris-be-conf"]["PPROF_TMPDIR"]
be_sys_log_level = config["configurations"]["doris-be-conf"]["sys_log_level"]
be_data_path = config["configurations"]["doris-be-conf"]["be_data_path"]
be_port = config["configurations"]["doris-be-conf"]["be_port"]
be_rpc_port = config["configurations"]["doris-be-conf"]["be_rpc_port"]
webserver_port = config["configurations"]["doris-be-conf"]["webserver_port"]
heartbeat_service_port = config["configurations"]["doris-be-conf"][
    "heartbeat_service_port"
]
be_heartbeat_service_port = config["configurations"]["doris-be-conf"][
    "heartbeat_service_port"
]
brpc_port = config["configurations"]["doris-be-conf"]["brpc_port"]
storage_root_path = config["configurations"]["doris-be-conf"]["storage_root_path"]
spill_storage_root_path = config["configurations"]["doris-be-conf"][
    "spill_storage_root_path"
]


# Broker configuration parameters
broker_ipc_port = config["configurations"]["doris-hdfs-broker-conf"]["broker_ipc_port"]
client_expire_seconds = config["configurations"]["doris-hdfs-broker-conf"][
    "client_expire_seconds"
]


# DORIS_FE
doris_fe_hosts_list = config["clusterHostInfo"]["doris_fe_hosts"]
doris_fe_hosts_list.sort()
if len(doris_fe_hosts_list) > 0:
    doris_fe_host = doris_fe_hosts_list[0]
# DORIS_FE_OBSERVER
doris_fe_observer_hosts_list = config["clusterHostInfo"]["doris_fe_observer_hosts"]

fe_root_password_sql = ""
if fe_root_password != "":
    fe_root_password_sql = "-p{0}".format(fe_root_password)


# get fe master host
def get_leader_fe_host():
    doris_fe_hosts_list = config["clusterHostInfo"]["doris_fe_hosts"]
    if len(doris_fe_hosts_list) == 0:
        raise Exception("can not get fe list , pls install fe first!")
    for fe_host in doris_fe_hosts_list:
        # mysql -h datanode01 -P 9030  -u root  < /tmp/doris_get_fe_master.sql  | sed 's/\t/,/g' | grep 'FOLLOWER,true' | cut -d',' -f3
        get_fe_leader_cmd = """
echo "SHOW PROC '/frontends';" | mysql -h {host} -P {port} -u root {password} --skip-column-names |
grep -v "^mysql: \[Warning\]" | 
sed 's/\\t/,/g' | grep 'FOLLOWER,true' | cut -d',' -f3
    """.format(
            host=shlex.quote(fe_host),
            port=shlex.quote(str(query_port)),
            password=shlex.quote(fe_root_password_sql),
        ).strip()
        get_fe_leader_cmd_v2 = """
echo "SHOW PROC '/frontends';" | mysql -h {host} -P {port} -u root {password} --skip-column-names |
grep -v "^mysql: \[Warning\]" | 
sed 's/\\t/,/g' | grep 'FOLLOWER,true' | cut -d',' -f2
""".format(
            host=shlex.quote(fe_host),
            port=shlex.quote(str(query_port)),
            password=shlex.quote(fe_root_password_sql),
        ).strip()
        trytimes = 5
        while trytimes > 0:
            try:
                Logger.info(
                    f"try to connect fe host {fe_host}  to get leader... get_fe_leader_cmd: {get_fe_leader_cmd}"
                )
                result = os.popen(get_fe_leader_cmd).read()
            except Exception as exception:
                Logger.error(
                    "exec cmd fail : {0} {1}".format(get_fe_leader_cmd, exception)
                )
                result = ""
            if result != "":
                if re.match(r"^\d+$", result):
                    Logger.info(result + "is port,change to get_fe_leader_cmd_v2")
                    get_fe_leader_cmd = get_fe_leader_cmd_v2
                    trytimes = 5
                else:
                    Logger.info("current leader fe host is : {0}".format(result))
                    break
            else:
                time.sleep(60)
            trytimes = trytimes - 1

        if result != "":
            break

    leader_fe_host = result.replace("\n", "")
    if leader_fe_host == "":
        Logger.error("exec cmd fail : {0}".format(get_fe_leader_cmd))
        raise Exception("can not get leader fe, pls check it!")

    Logger.info(leader_fe_host)
    return leader_fe_host


def check_process_exists(pid_file):
    from resource_management.core import sudo

    if not pid_file or not os.path.isfile(pid_file):
        Logger.info("Pid file {0} is empty or does not exist".format(str(pid_file)))
        raise ComponentIsNotRunning()

    try:
        pid = int(sudo.read_file(pid_file).decode().strip())
    except:
        Logger.info(
            "Pid file {0} does not exist or does not contain a process id number".format(
                pid_file
            )
        )
        raise ComponentIsNotRunning()

    try:
        sudo.kill(pid, 0)
        return True
    except OSError:
        Logger.info(
            "Process with pid {0} is not running. Stale pid file" " at {1}".format(
                pid, pid_file
            )
        )
        return False


# kerberos
security_enabled = config["configurations"]["cluster-env"]["security_enabled"]
kinit_path_local = ""
doris_user_keytab = ""
doris_user_principal_name = ""
doris_user_kinit_cmd = ""
if security_enabled:
    kinit_path_local = get_kinit_path(
        default("/configurations/kerberos-env/executable_search_paths", None)
    )
    doris_user_keytab = config["configurations"]["doris-env"]["doris_user_keytab"]
    doris_user_principal_name = config["configurations"]["doris-env"][
        "doris_user_principal"
    ]
    doris_user_kinit_cmd = format(
        "{kinit_path_local} -kt {doris_user_keytab} {doris_user_principal_name};"
    )


access_controller_type = "default"

# get the correct version to use for checking stack features
version_for_stack_feature_checks = get_stack_feature_version(config)

stack_supports_ranger_kerberos = check_stack_feature(
    StackFeature.RANGER_KERBEROS_SUPPORT, version_for_stack_feature_checks
)
stack_supports_ranger_audit_db = check_stack_feature(
    StackFeature.RANGER_AUDIT_DB_SUPPORT, version_for_stack_feature_checks
)


# ranger doris plugin section start


# to get db connector jar
jdk_location = config["ambariLevelParams"]["jdk_location"]

# ranger host
ranger_admin_hosts = default("/clusterHostInfo/ranger_admin_hosts", [])
has_ranger_admin = not len(ranger_admin_hosts) == 0

# ranger support xml_configuration flag, instead of depending on ranger xml_configurations_supported/ranger-env introduced, using stack feature
xml_configurations_supported = check_stack_feature(
    StackFeature.RANGER_XML_CONFIGURATION, version_for_stack_feature_checks
)

# ranger doris plugin enabled property
enable_ranger_doris = default(
    "/configurations/ranger-doris-plugin-properties/ranger-doris-plugin-enabled", "No"
)
# Logger.info("/configurations/ranger-doris-plugin-properties/ranger-doris-plugin-enabled")
# Logger.info(enable_ranger_doris)
enable_ranger_doris = True if enable_ranger_doris.lower() == "yes" else False
# Logger.info(enable_ranger_doris)

policymgr_mgr_url = config["configurations"]["admin-properties"][
    "policymgr_external_url"
]

# ranger doris properties
if enable_ranger_doris:
    # get ranger policy url
    policymgr_mgr_url = config["configurations"]["admin-properties"][
        "policymgr_external_url"
    ]
    Logger.info(policymgr_mgr_url)
    # can't get vaelue,temp enable it
    # if xml_configurations_supported:
    #  policymgr_mgr_url = config['configurations']['ranger-doris-security']['ranger.plugin.doris.policy.rest.url']

    if not is_empty(policymgr_mgr_url) and policymgr_mgr_url.endswith("/"):
        policymgr_mgr_url = policymgr_mgr_url.rstrip("/")

    # ranger audit db user
    xa_audit_db_user = default(
        "/configurations/admin-properties/audit_db_user", "rangerlogger"
    )

    # ranger doris service/repository name
    repo_name = str(config["clusterName"]) + "_doris"
    repo_name_value = config["configurations"]["ranger-doris-security"][
        "ranger.plugin.doris.service.name"
    ]
    if not is_empty(repo_name_value) and repo_name_value != "{{repo_name}}":
        repo_name = repo_name_value

    common_name_for_certificate = config["configurations"][
        "ranger-doris-plugin-properties"
    ]["common.name.for.certificate"]
    repo_config_username = config["configurations"]["ranger-doris-plugin-properties"][
        "REPOSITORY_CONFIG_USERNAME"
    ]
    ranger_plugin_properties = config["configurations"][
        "ranger-doris-plugin-properties"
    ]
    policy_user = config["configurations"]["ranger-doris-plugin-properties"][
        "policy_user"
    ]
    repo_config_password = config["configurations"]["ranger-doris-plugin-properties"][
        "REPOSITORY_CONFIG_PASSWORD"
    ]

    # ranger-env config
    ranger_env = config["configurations"]["ranger-env"]

    # create ranger-env config having external ranger credential properties
    if not has_ranger_admin and enable_ranger_doris:
        external_admin_username = default(
            "/configurations/ranger-doris-plugin-properties/external_admin_username",
            "admin",
        )
        external_admin_password = default(
            "/configurations/ranger-doris-plugin-properties/external_admin_password",
            "admin",
        )
        external_ranger_admin_username = default(
            "/configurations/ranger-doris-plugin-properties/external_ranger_admin_username",
            "amb_ranger_admin",
        )
        external_ranger_admin_password = default(
            "/configurations/ranger-doris-plugin-properties/external_ranger_admin_password",
            "amb_ranger_admin",
        )
        ranger_env = {}
        ranger_env["admin_username"] = external_admin_username
        ranger_env["admin_password"] = external_admin_password
        ranger_env["ranger_admin_username"] = external_ranger_admin_username
        ranger_env["ranger_admin_password"] = external_ranger_admin_password

    xa_audit_db_password = ""
    if (
        not is_empty(config["configurations"]["admin-properties"]["audit_db_password"])
        and stack_supports_ranger_audit_db
        and has_ranger_admin
    ):
        xa_audit_db_password = config["configurations"]["admin-properties"][
            "audit_db_password"
        ]

    downloaded_custom_connector = None
    previous_jdbc_jar_name = None
    driver_curl_source = None
    driver_curl_target = None
    previous_jdbc_jar = None

    if has_ranger_admin and stack_supports_ranger_audit_db:
        xa_audit_db_flavor = config["configurations"]["admin-properties"]["DB_FLAVOR"]
        jdbc_jar_name, previous_jdbc_jar_name, audit_jdbc_url, jdbc_driver = (
            get_audit_configs(config)
        )

        downloaded_custom_connector = (
            format("{exec_tmp_dir}/{jdbc_jar_name}")
            if stack_supports_ranger_audit_db
            else None
        )
        driver_curl_source = (
            format("{jdk_location}/{jdbc_jar_name}")
            if stack_supports_ranger_audit_db
            else None
        )
        driver_curl_target = (
            format("{stack_root}/current/{component_directory}/lib/{jdbc_jar_name}")
            if stack_supports_ranger_audit_db
            else None
        )
        previous_jdbc_jar = (
            format(
                "{stack_root}/current/{component_directory}/lib/{previous_jdbc_jar_name}"
            )
            if stack_supports_ranger_audit_db
            else None
        )
        sql_connector_jar = ""

    # warning: username/passsword should be doris's username/password,now the value is ranger's,pls modify after setup
    # 'jdbc.url': 'jdbc:mysql://172.21.0.101:9030?useSSL=false',
    doris_ranger_plugin_config = {
        "username": repo_config_username,
        "password": repo_config_password,
        "jdbc.driver_class": "com.mysql.cj.jdbc.Driver",
        "jdbc.url": format("jdbc:mysql://{doris_fe_host}:{fe_query_port}?useSSL=false"),
        "resource.lookup.timeout.value.in.ms": "10000",
    }

    doris_ranger_plugin_config["policy.download.auth.users"] = doris_user
    doris_ranger_plugin_config["tag.download.auth.users"] = doris_user
    doris_ranger_plugin_config["policy.grantrevoke.auth.users"] = doris_user

    custom_ranger_service_config = generate_ranger_service_config(
        ranger_plugin_properties
    )
    if len(custom_ranger_service_config) > 0:
        doris_ranger_plugin_config.update(custom_ranger_service_config)

    doris_ranger_plugin_repo = {
        "isEnabled": "true",
        "configs": doris_ranger_plugin_config,
        "description": "doris repo",
        "name": repo_name,
        "type": "doris",
    }

    xa_audit_db_is_enabled = False
    if xml_configurations_supported and stack_supports_ranger_audit_db:
        xa_audit_db_is_enabled = config["configurations"]["ranger-doris-audit"][
            "xasecure.audit.destination.db"
        ]

    xa_audit_hdfs_is_enabled = (
        config["configurations"]["ranger-doris-audit"][
            "xasecure.audit.destination.hdfs"
        ]
        if xml_configurations_supported
        else False
    )
    ssl_keystore_password = (
        config["configurations"]["ranger-doris-policymgr-ssl"][
            "xasecure.policymgr.clientssl.keystore.password"
        ]
        if xml_configurations_supported
        else None
    )
    ssl_truststore_password = (
        config["configurations"]["ranger-doris-policymgr-ssl"][
            "xasecure.policymgr.clientssl.truststore.password"
        ]
        if xml_configurations_supported
        else None
    )
    credential_file = format("/etc/ranger/{repo_name}/cred.jceks")

    # for SQLA explicitly disable audit to DB for Ranger
    if (
        has_ranger_admin
        and stack_supports_ranger_audit_db
        and xa_audit_db_flavor.lower() == "sqla"
    ):
        xa_audit_db_is_enabled = False

    # set doris fe conf
    access_controller_type = "ranger-doris"

# need this to capture cluster name from where ranger doris plugin is enabled
cluster_name = config["clusterName"]

# ranger doris plugin section end


dfs_type = default("/clusterLevelParams/dfs_type", "")
hdfs_user = config["configurations"]["hadoop-env"]["hdfs_user"]
hdfs_principal_name = config["configurations"]["hadoop-env"]["hdfs_principal_name"]
hdfs_user_keytab = config["configurations"]["hadoop-env"]["hdfs_user_keytab"]
user_group = config["configurations"]["cluster-env"]["user_group"]
hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore"
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
default_fs = config["configurations"]["core-site"]["fs.defaultFS"]
hdfs_site = config["configurations"]["hdfs-site"]

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
