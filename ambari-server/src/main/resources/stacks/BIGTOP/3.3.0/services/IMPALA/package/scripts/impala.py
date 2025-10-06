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

import os
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
from resource_management import *


@OsFamilyFuncImpl(os_family=OsFamilyImpl.DEFAULT)
def impala(name=None):
    import params

    Directory(
        params.impala_log_dir,
        owner=params.impala_user,
        create_parents=True,
        group=params.user_group,
        mode=0o775,
    )

    Directory(
        params.impala_pid_dir,
        owner=params.impala_user,
        create_parents=True,
        group=params.user_group,
        mode=0o775,
    )

    XmlConfig(
        "core-site.xml",
        conf_dir=params.impala_conf_dir,
        configurations=params.core_site_configurations,
        configuration_attributes=params.core_site_attributes,
        owner=params.impala_user,
        group=params.user_group,
        mode=0o644,
    )
    XmlConfig(
        "hdfs-site.xml",
        conf_dir=params.impala_conf_dir,
        configurations=params.hdfs_site_configurations,
        configuration_attributes=params.hdfs_site_attributes,
        owner=params.impala_user,
        group=params.user_group,
        mode=0o644,
    )
    XmlConfig(
        "hive-site.xml",
        conf_dir=params.impala_conf_dir,
        configurations=params.hive_site_configurations,
        configuration_attributes=params.hive_site_attributes,
        owner=params.impala_user,
        group=params.user_group,
        mode=0o644,
    )

    File(
        os.path.join(params.impala_conf_dir, "impala-env.sh"),
        owner=params.impala_user,
        group=params.user_group,
        content=InlineTemplate(params.impala_template),
        mode=0o755,
    )

    File(
        params.start_impala_path,
        mode=0o755,
        content=Template(format("{start_impala_script}")),
    )

    XmlConfig(
        "llama-site.xml",
        conf_dir=params.impala_conf_dir,
        configurations=params.impala_llamaSite_configurations,
        configuration_attributes=params.hive_llamaSite_attributes,
        owner=params.impala_user,
        group=params.user_group,
        mode=0o644,
    )

    File(
        os.path.join(params.impala_conf_dir, "fair-scheduler.xml"),
        owner=params.impala_user,
        group=params.user_group,
        content=InlineTemplate(params.impala_fairscheduler_template),
        mode=0o755,
    )

    if params.enable_ranger:
        XmlConfig(
            "ranger-hive-audit.xml",
            conf_dir=params.impala_conf_dir,
            configurations=params.ranger_hive_audit_configurations,
            configuration_attributes=params.ranger_hive_audit_attributes,
            owner=params.impala_user,
            group=params.user_group,
            mode=0o644,
        )
        XmlConfig(
            "ranger-hive-security.xml",
            conf_dir=params.impala_conf_dir,
            configurations=params.ranger_hive_security_configurations,
            configuration_attributes=params.ranger_hive_security_attributes,
            owner=params.impala_user,
            group=params.user_group,
            mode=0o644,
        )
        Directory(
            params.ranger_plugin_hive_policy_cachedir,
            create_parents=True,
            cd_access="a",
            owner=params.hive_user,
            group=params.user_group,
            mode=0o775,
        )
