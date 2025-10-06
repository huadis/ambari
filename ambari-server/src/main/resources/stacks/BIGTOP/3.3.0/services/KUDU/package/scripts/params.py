#!/usr/bin/env python3
from resource_management import *
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.expect import expect

from ambari_commons.constants import AMBARI_SUDO_BINARY
from resource_management.libraries.functions.stack_features import check_stack_feature
from resource_management.libraries.functions.stack_features import get_stack_feature_version
import status_params
import os, socket
from resource_management.libraries.functions.stack_features import get_stack_feature_version
from resource_management.libraries.functions.setup_ranger_plugin_xml import get_audit_configs, generate_ranger_service_config
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions.get_not_managed_resources import get_not_managed_resources


script_dir = os.path.dirname(os.path.realpath(__file__))
files_dir = os.path.join(os.path.dirname(script_dir), 'files')

sudo = AMBARI_SUDO_BINARY

# server configurations
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()
stack_root = Script.get_stack_root()
stack_name = default("/hostLevelParams/stack_name", None)
stack_version_buildnum = default("/commandParams/version", None)
version = default("/commandParams/version", None)
component_directory = status_params.component_directory
component_directory = status_params.component_directory
cluster_name = config['clusterName']

#users
kudu_user = config['configurations']['kudu-env']['kudu_user']
user_group = config['configurations']['cluster-env']['user_group']

kudu_home = format("{stack_root}/current/{component_directory}")

kudu_env = config['configurations']['kudu-env']
kudu_log_dir = kudu_env['kudu_log_dir']
kudu_pid_dir = kudu_env['kudu_pid_dir']

kudu_conf_dir = "/etc/kudu/conf"
kudu_bin_home = format("{kudu_home}/bin")
kudu_sbin_home = format("{kudu_home}/bin")

master_env = config['configurations']['kudu-master-env']
tserver_env = config['configurations']['kudu-tserver-env']

master_env_map = {}
master_env_map.update(master_env)

tserver_env_map = {}
tserver_env_map.update(tserver_env)

kudu_master_hosts = ",".join(config['clusterHostInfo']['kudu_master_hosts'])
kudu_master_hosts_num = len(config['clusterHostInfo']['kudu_master_hosts'])

kudu_master_rpc_bind_addresses = master_env['rpc_bind_addresses']
kudu_tserver_rpc_bind_addresses = master_env['rpc_bind_addresses']

current_host_name = socket.gethostname()
hdfs_host = default("/clusterHostInfo/namenode_hosts", [''])[0]

current_host_name = socket.getfqdn()

# Java home path
java_home = config["ambariLevelParams"]["java_home"] if "java_home" in config["ambariLevelParams"] else None
java_exec = format("{java_home}/bin/java")
java_version = expect("/ambariLevelParams/java_version", int)

#Starting cmd
start_master_script = 'start_master.sh.j2' 
start_master_path = format("{tmp_dir}/start_master_script")
start_tserver_script = 'start_tserver.sh.j2' 
start_tserver_path = format("{tmp_dir}/start_tserver_script")

# security related
security_enabled = config['configurations']['cluster-env']['security_enabled']
realm_name = config['configurations']['kerberos-env']['realm']
kinit_path_local = get_kinit_path(default('/configurations/kerberos-env/executable_search_paths', None))


# security params
if security_enabled:
  master_env_map['rpc_authentication'] = kudu_env['rpc_authentication']
  master_env_map['rpc_encryption'] = kudu_env['rpc_encryption']
  master_env_map['keytab_file'] = kudu_env['keytab_file']
  master_env_map['webserver_enabled'] = kudu_env['webserver_enabled']
  master_env_map['user_acl'] = kudu_env['user_acl']
  master_env_map['superuser_acl'] = kudu_env['superuser_acl']

  tserver_env_map['rpc_authentication'] = kudu_env['rpc_authentication']
  tserver_env_map['rpc_encryption'] = kudu_env['rpc_encryption']
  tserver_env_map['keytab_file'] = kudu_env['keytab_file']
  tserver_env_map['webserver_enabled'] = kudu_env['webserver_enabled']
  tserver_env_map['user_acl'] = kudu_env['user_acl']
  tserver_env_map['superuser_acl'] = kudu_env['superuser_acl']

_hostname_lowercase = config['agentLevelParams']['hostname'].lower()
master_jaas_princ = kudu_env['principal_name'].replace('_HOST',_hostname_lowercase)
master_keytab_path = kudu_env['keytab_file']
 



# ranger kudu plugin section start

# get the correct version to use for checking stack features
version_for_stack_feature_checks = get_stack_feature_version(config)

stack_supports_ranger_kerberos = check_stack_feature(StackFeature.RANGER_KERBEROS_SUPPORT, version_for_stack_feature_checks)
stack_supports_ranger_audit_db = check_stack_feature(StackFeature.RANGER_AUDIT_DB_SUPPORT, version_for_stack_feature_checks)


# ranger kudu plugin enabled property
enable_ranger_kudu = default("/configurations/ranger-kudu-plugin-properties/ranger-kudu-plugin-enabled", "No")
enable_ranger_kudu = True if enable_ranger_kudu.lower() == 'yes' else False

if enable_ranger_kudu :
  master_env_map['ranger_config_path'] = kudu_conf_dir
  master_env_map['ranger_java_path'] = java_home + '/bin/java'
  master_env_map['ranger_jar_path'] = '/usr/bigtop/current/kudu/bin/kudu-subprocess.jar'
  master_env_map['trusted_user_acl'] =  kudu_env['trusted_user_acl']
  tserver_env_map['tserver_enforce_access_control'] = 'true'


# to get db connector jar
jdk_location = config['ambariLevelParams']['jdk_location']

# ranger host
ranger_admin_hosts = default("/clusterHostInfo/ranger_admin_hosts", [])
has_ranger_admin = not len(ranger_admin_hosts) == 0 

# ranger support xml_configuration flag, instead of depending on ranger xml_configurations_supported/ranger-env introduced, using stack feature
xml_configurations_supported = check_stack_feature(StackFeature.RANGER_XML_CONFIGURATION, version_for_stack_feature_checks)

# ranger kudu properties
if enable_ranger_kudu:
  # get ranger policy url
  policymgr_mgr_url = config['configurations']['admin-properties']['policymgr_external_url']
  Logger.info("--1---")
  Logger.info(policymgr_mgr_url)
  # if xml_configurations_supported:
  #   policymgr_mgr_url = config['configurations']['ranger-kudu-security']['ranger.plugin.kudu.policy.rest.url']
  #   if is_empty(policymgr_mgr_url):
  #     policymgr_mgr_url = config['configurations']['admin-properties']['policymgr_external_url']

  if not is_empty(policymgr_mgr_url) and policymgr_mgr_url.endswith('/'):
    policymgr_mgr_url = policymgr_mgr_url.rstrip('/')

  # ranger audit db user
  xa_audit_db_user = default('/configurations/admin-properties/audit_db_user', 'rangerlogger')

  # ranger kudu service/repository name
  repo_name = str(config['clusterName']) + '_kudu'
  repo_name_value = config['configurations']['ranger-kudu-security']['ranger.plugin.kudu.service.name']
  if not is_empty(repo_name_value) and repo_name_value != "{{repo_name}}":
    repo_name = repo_name_value

  common_name_for_certificate = config['configurations']['ranger-kudu-plugin-properties']['common.name.for.certificate']
  repo_config_username = config['configurations']['ranger-kudu-plugin-properties']['REPOSITORY_CONFIG_USERNAME']
  ranger_plugin_properties = config['configurations']['ranger-kudu-plugin-properties']
  policy_user = config['configurations']['ranger-kudu-plugin-properties']['policy_user']
  repo_config_password = config['configurations']['ranger-kudu-plugin-properties']['REPOSITORY_CONFIG_PASSWORD']

  # ranger-env config
  ranger_env = config['configurations']['ranger-env']

  # create ranger-env config having external ranger credential properties
  if not has_ranger_admin and enable_ranger_kudu:
    external_admin_username = default('/configurations/ranger-kudu-plugin-properties/external_admin_username', 'admin')
    external_admin_password = default('/configurations/ranger-kudu-plugin-properties/external_admin_password', 'admin')
    external_ranger_admin_username = default('/configurations/ranger-kudu-plugin-properties/external_ranger_admin_username', 'amb_ranger_admin')
    external_ranger_admin_password = default('/configurations/ranger-kudu-plugin-properties/external_ranger_admin_password', 'amb_ranger_admin')
    ranger_env = {}
    ranger_env['admin_username'] = external_admin_username
    ranger_env['admin_password'] = external_admin_password
    ranger_env['ranger_admin_username'] = external_ranger_admin_username
    ranger_env['ranger_admin_password'] = external_ranger_admin_password

  xa_audit_db_password = ''
  if not is_empty(config['configurations']['admin-properties']['audit_db_password']) and stack_supports_ranger_audit_db and has_ranger_admin:
    xa_audit_db_password = config['configurations']['admin-properties']['audit_db_password']

  downloaded_custom_connector = None
  previous_jdbc_jar_name = None
  driver_curl_source = None
  driver_curl_target = None
  previous_jdbc_jar = None

  if has_ranger_admin and stack_supports_ranger_audit_db:
    xa_audit_db_flavor = config['configurations']['admin-properties']['DB_FLAVOR']
    jdbc_jar_name, previous_jdbc_jar_name, audit_jdbc_url, jdbc_driver = get_audit_configs(config)

    downloaded_custom_connector = format("{exec_tmp_dir}/{jdbc_jar_name}") if stack_supports_ranger_audit_db else None
    driver_curl_source = format("{jdk_location}/{jdbc_jar_name}") if stack_supports_ranger_audit_db else None
    driver_curl_target = format("{stack_root}/current/{component_directory}/lib/{jdbc_jar_name}") if stack_supports_ranger_audit_db else None
    previous_jdbc_jar = format("{stack_root}/current/{component_directory}/lib/{previous_jdbc_jar_name}") if stack_supports_ranger_audit_db else None
    sql_connector_jar = ''

  if security_enabled:
    master_principal = config['configurations']['kudu-site']['kudu.master.kerberos.principal']

  kudu_ranger_plugin_config = {
    # 'username': repo_config_username,
    # 'password': repo_config_password,
    # 'hadoop.security.authentication': sql_connector_jar,
    # 'kudu.security.authentication': sql_connector_jar,
    # 'kudu.zookeeper.property.clientPort': sql_connector_jar,
    # 'kudu.zookeeper.quorum': sql_connector_jar,
    # 'zookeeper.znode.parent': sql_connector_jar,
    # 'commonNameForCertificate': common_name_for_certificate,
    # 'kudu.master.kerberos.principal': master_principal if security_enabled else ''
  }

  # if security_enabled:
  kudu_ranger_plugin_config['policy.download.auth.users'] = kudu_user
  kudu_ranger_plugin_config['tag.download.auth.users'] = kudu_user
  kudu_ranger_plugin_config['policy.grantrevoke.auth.users'] = kudu_user

  kudu_ranger_plugin_config['setup.additional.default.policies'] = "true"
  kudu_ranger_plugin_config['default-policy.1.name'] = "Service Check User Policy for Kudu"
  kudu_ranger_plugin_config['default-policy.1.resource.database'] = "*"
  kudu_ranger_plugin_config['default-policy.1.resource.table'] = "*"
  kudu_ranger_plugin_config['default-policy.1.resource.column'] = "*"
  kudu_ranger_plugin_config['default-policy.1.policyItem.1.users'] = policy_user+",kudu,impala,hive"
  kudu_ranger_plugin_config['default-policy.1.policyItem.1.accessTypes'] = "all"

  custom_ranger_service_config = generate_ranger_service_config(ranger_plugin_properties)
  if len(custom_ranger_service_config) > 0:
    kudu_ranger_plugin_config.update(custom_ranger_service_config)

  kudu_ranger_plugin_repo = {
    'isEnabled': 'true',
    'configs': kudu_ranger_plugin_config,
    'description': 'kudu repo',
    'name': repo_name,
    'type': 'kudu'
  }

  ranger_kudu_principal = None
  ranger_kudu_keytab = None
  if stack_supports_ranger_kerberos and security_enabled :
    ranger_kudu_principal = master_jaas_princ
    ranger_kudu_keytab = master_keytab_path

  xa_audit_db_is_enabled = False
  if xml_configurations_supported and stack_supports_ranger_audit_db:
    xa_audit_db_is_enabled = config['configurations']['ranger-kudu-audit']['xasecure.audit.destination.db']

  xa_audit_hdfs_is_enabled = config['configurations']['ranger-kudu-audit']['xasecure.audit.destination.hdfs'] if xml_configurations_supported else False
  ssl_keystore_password = config['configurations']['ranger-kudu-policymgr-ssl']['xasecure.policymgr.clientssl.keystore.password'] if xml_configurations_supported else None
  ssl_truststore_password = config['configurations']['ranger-kudu-policymgr-ssl']['xasecure.policymgr.clientssl.truststore.password'] if xml_configurations_supported else None
  credential_file = format('/etc/ranger/{repo_name}/cred.jceks')

  # for SQLA explicitly disable audit to DB for Ranger
  if has_ranger_admin and stack_supports_ranger_audit_db and xa_audit_db_flavor.lower() == 'sqla':
    xa_audit_db_is_enabled = False

# need this to capture cluster name from where ranger kudu plugin is enabled
cluster_name = config['clusterName']

# ranger kudu plugin section end


retryAble = default("/commandParams/command_retry_enabled", False)


# hadoop default parameters
hadoop_bin_dir = stack_select.get_hadoop_dir("bin")
hadoop_conf_dir = conf_select.get_hadoop_conf_dir()
#for create_hdfs_directory
hostname = config['agentLevelParams']['hostname']
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']

hdfs_site = config['configurations']['hdfs-site']
default_fs = config['configurations']['core-site']['fs.defaultFS']

dfs_type = default("/clusterLevelParams/dfs_type", "")

import functools
#create partial functions with common arguments for every HdfsResource call
#to create/delete hdfs directory/file/copyfromlocal we need to call params.HdfsResource in code
HdfsResource = functools.partial(
  HdfsResource,
  user=hdfs_user,
  hdfs_resource_ignore_file = "/var/lib/ambari-agent/data/.hdfs_resource_ignore",
  security_enabled = security_enabled,
  keytab = hdfs_user_keytab,
  kinit_path_local = kinit_path_local,
  hadoop_bin_dir = hadoop_bin_dir,
  hadoop_conf_dir = hadoop_conf_dir,
  principal_name = hdfs_principal_name,
  hdfs_site = hdfs_site,
  default_fs = default_fs,
  immutable_paths = get_not_managed_resources(),
  dfs_type = dfs_type
)

