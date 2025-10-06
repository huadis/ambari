#!/usr/bin/env python
import socket
import os

from resource_management import *
from ambari_commons.constants import AMBARI_SUDO_BINARY
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.expect import expect
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.stack_features import (
    get_stack_feature_version,
)
import status_params

script_dir = os.path.dirname(os.path.realpath(__file__))

sudo = AMBARI_SUDO_BINARY

config = Script.get_config()
tmp_dir = Script.get_tmp_dir()
stack_root = Script.get_stack_root()
stack_name = default("/hostLevelParams/stack_name", None)
stack_version_buildnum = default("/commandParams/version", None)
component_directory = status_params.component_directory
cluster_name = config["clusterName"]

impala_env = config["configurations"]["impala-env"]
impala_log_dir = impala_env["impala_log_dir"]
impala_pid_dir = impala_env["impala_pid_dir"]
impala_scratch_dir = impala_env["impala_scratch_dir"]
impala_log_file = os.path.join(impala_log_dir, "impala-setup.log")
impala_catalog_host = config["clusterHostInfo"]["impala_catalog_hosts"][0]
impala_state_store_host = config["clusterHostInfo"]["impala_state_store_hosts"][0]

impala_home = format("{stack_root}/current/{component_directory}")
impala_conf_dir = "/etc/impala/conf"
impala_bin_home = format("{impala_home}/bin")

# users
impala_user = config["configurations"]["impala-env"]["impala_user"]
user_group = config["configurations"]["cluster-env"]["user_group"]
hdfs_user = config["configurations"]["hadoop-env"]["hdfs_user"]
hive_user = config["configurations"]["hive-env"]["hive_user"]

hive_metastore_warehouse_dir = config["configurations"]["hive-site"][
    "hive.metastore.warehouse.dir"
]

enable_ranger = impala_env["enable_ranger"]

current_host_name = socket.getfqdn()

# Java home path
java_home = (
    config["ambariLevelParams"]["java_home"]
    if "java_home" in config["ambariLevelParams"]
    else None
)
java_exec = format("{java_home}/bin/java")
java_version = expect("/ambariLevelParams/java_version", int)

# security related
security_enabled = config["configurations"]["cluster-env"]["security_enabled"]
realm_name = config["configurations"]["kerberos-env"]["realm"]
kinit_path_local = get_kinit_path(
    default("/configurations/kerberos-env/executable_search_paths", None)
)


hdfs_host = default("/clusterHostInfo/namenode_hosts", [""])[0]
if not hdfs_host:
    hdfs_host = default("/clusterHostInfo/namenode_host", [""])[0]
hive_host = default("/clusterHostInfo/hive_metastore_host", [""])[0]
# kudu_master_hosts = ",".join(config['clusterHostInfo']['kudu_master_hosts'])
# kudu_master_host_num = len(config['clusterHostInfo']['kudu_master_hosts'])

kudu_master_hosts = ""
kudu_master_host_num = 0
if "kudu_master_hosts" in config["clusterHostInfo"]:
    kudu_master_hosts_list = config["clusterHostInfo"]["kudu_master_hosts"]
    # print("*****-----****")
    # print(kudu_master_hosts_list)
    kudu_master_host_num = len(kudu_master_hosts_list)
    if kudu_master_host_num > 0:
        kudu_master_hosts = ",".join(kudu_master_hosts_list)


scp_conf_dir = "/etc/impala/conf"
scp_conf_from = {
    "hdfs": {
        "host": hdfs_host,
        "files": [
            "/etc/hadoop/conf/core-site.xml",
            "/etc/hadoop/conf/hdfs-site.xml" "/etc/hive/conf/hive-site.xml",
        ],
    }
}


# core-site
core_site_configurations = config["configurations"]["core-site"]
core_site_attributes = config["configurationAttributes"]["core-site"]

# hdfs-site
hdfs_site_configurations = config["configurations"]["hdfs-site"]
hdfs_site_attributes = config["configurationAttributes"]["hdfs-site"]

# hive-site
hive_site_configurations = config["configurations"]["hive-site"]
hive_site_attributes = config["configurationAttributes"]["hive-site"]

ranger_hive_audit_configurations = config["configurations"]["ranger-hive-audit"]
ranger_hive_audit_attributes = config["configurationAttributes"]["ranger-hive-audit"]

ranger_hive_security_configurations = config["configurations"]["ranger-hive-security"]
ranger_hive_security_attributes = config["configurationAttributes"][
    "ranger-hive-security"
]


# get the correct version to use for checking stack features
version_for_stack_feature_checks = get_stack_feature_version(config)
# get ranger hive properties if enable_ranger_hive is True
enable_ranger_hive = (
    config["configurations"]["hive-env"]["hive_security_authorization"].lower()
    == "ranger"
)
# ranger support xml_configuration flag, instead of depending on ranger xml_configurations_supported/ranger-env, using stack feature
xml_configurations_supported = check_stack_feature(
    StackFeature.RANGER_XML_CONFIGURATION, version_for_stack_feature_checks
)

if enable_ranger_hive:
    # get ranger policy url
    policymgr_mgr_url = config["configurations"]["admin-properties"][
        "policymgr_external_url"
    ]
    if xml_configurations_supported:
        policymgr_mgr_url = config["configurations"]["ranger-hive-security"][
            "ranger.plugin.hive.policy.rest.url"
        ]

    if not is_empty(policymgr_mgr_url) and policymgr_mgr_url.endswith("/"):
        policymgr_mgr_url = policymgr_mgr_url.rstrip("/")

    # ranger audit db user
    xa_audit_db_user = default(
        "/configurations/admin-properties/audit_db_user", "rangerlogger"
    )

    # ranger hive service name
    repo_name = str(config["clusterName"]) + "_hive"
    repo_name_value = config["configurations"]["ranger-hive-security"][
        "ranger.plugin.hive.service.name"
    ]
    if not is_empty(repo_name_value) and repo_name_value != "{{repo_name}}":
        repo_name = repo_name_value

    ranger_plugin_hive_policy_cachedir = format(
        format(
            default(
                "/configurations/ranger-hive-security/ranger.plugin.hive.policy.cache.dir",
                "/etc/ranger/{repo_name}/policycache",
            )
        )
    )


impala_template = config["configurations"]["impala-env"]["content"]

# Starting cmd
start_impala_script = "startImpala.sh.j2"

start_impala_path = format("{tmp_dir}/start_impala_script")

# ADMISSION_CONTROL
impala_fairscheduler_template = config["configurations"]["fair-scheduler"]["content"]
impala_llamaSite_configurations = config["configurations"]["llama-site"]
hive_llamaSite_attributes = config["configurationAttributes"]["llama-site"]
