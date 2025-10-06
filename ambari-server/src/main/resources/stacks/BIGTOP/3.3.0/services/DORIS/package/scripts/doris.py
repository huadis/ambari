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
def doris(name=None):
    import params
    import status_params

    # for test
    Directory(
        "/app/doris",
        owner=params.doris_user,
        create_parents=True,
        group=params.user_group,
        mode=0o775,
    )
    Directory(
        status_params.doris_pid_dir,
        owner=params.doris_user,
        create_parents=True,
        group=params.user_group,
        mode=0o775,
    )

    # gennerate doris be conf releate file
    if name == "doris_fe":
        Directory(
            params.doris_fe_home,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o775,
        )
        Directory(
            params.doris_fe_bin_path,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o775,
        )
        Directory(
            params.fe_meta_dir,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o775,
        )
        Directory(
            params.fe_log_default_dir,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o755,
        )
        Directory(
            params.fe_log_dir,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o755,
        )
        Directory(
            params.fe_temp_dir,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o755,
        )
        File(
            os.path.join(params.doris_fe_conf_dir, "log4j2-spring.xml"),
            content="",
            owner=params.doris_user,
            group=params.user_group,
        )

        File(
            os.path.join(params.doris_fe_conf_dir, "fe.conf"),
            content=InlineTemplate(
                params.config["configurations"]["doris-fe-conf"]["content"]
            ),
            owner=params.doris_user,
            group=params.doris_group,
        )
        # create doris fe ldap.conf
        File(
            os.path.join(params.doris_fe_conf_dir, "ldap.conf"),
            owner=params.doris_user,
            group=params.user_group,
            content=InlineTemplate(
                params.config["configurations"]["doris-fe-ldap-conf"]["content"]
            ),
            mode=0o644,
        )

        if "hdfs-site" in params.config["configurations"]:
            XmlConfig(
                "hdfs-site.xml",
                conf_dir=params.doris_fe_conf_dir,
                configurations=params.config["configurations"]["hdfs-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "hdfs-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )
        if "core-site" in params.config["configurations"]:
            XmlConfig(
                "core-site.xml",
                conf_dir=params.doris_fe_conf_dir,
                configurations=params.config["configurations"]["core-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "core-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )
        if "hive-site" in params.config["configurations"]:
            XmlConfig(
                "hive-site.xml",
                conf_dir=params.doris_fe_conf_dir,
                configurations=params.config["configurations"]["hive-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "hive-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )

    # gennerate doris be conf releate file
    if name == "doris_be":
        File(
            os.path.join(params.doris_be_lib_path, "doris_be"),
            owner=params.doris_user,
            group=params.user_group,
        )
        Directory(
            params.doris_be_bin_path,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o775,
        )

        Directory(
            params.PPROF_TMPDIR,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o755,
        )
        Directory(
            params.be_log_default_dir,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o755,
        )
        Directory(
            params.be_log_dir,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o755,
        )
        File(
            os.path.join(params.doris_be_conf_dir, "be.conf"),
            content=InlineTemplate(
                params.config["configurations"]["doris-be-conf"]["content"]
            ),
            owner=params.doris_user,
            group=params.doris_group,
        )
        # create doris be asan_suppr.conf
        File(
            os.path.join(params.doris_be_conf_dir, "asan_suppr.conf"),
            owner=params.doris_user,
            group=params.user_group,
            content=InlineTemplate(
                params.config["configurations"]["doris-be-asan_suppr-conf"]["content"]
            ),
            mode=0o644,
        )
        # create doris be Isan_suppr.conf
        File(
            os.path.join(params.doris_be_conf_dir, "lsan_suppr.conf"),
            owner=params.doris_user,
            group=params.user_group,
            content=InlineTemplate(
                params.config["configurations"]["doris-be-lsan_suppr-conf"]["content"]
            ),
            mode=0o644,
        )
        # create doris be odbcinst.ini
        File(
            os.path.join(params.doris_be_conf_dir, "odbcinst.ini"),
            owner=params.doris_user,
            group=params.user_group,
            content=InlineTemplate(
                params.config["configurations"]["doris-be-odbcinst-ini"]["content"]
            ),
            mode=0o644,
        )

        if "hdfs-site" in params.config["configurations"]:
            XmlConfig(
                "hdfs-site.xml",
                conf_dir=params.doris_be_conf_dir,
                configurations=params.config["configurations"]["hdfs-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "hdfs-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )
        if "core-site" in params.config["configurations"]:
            XmlConfig(
                "core-site.xml",
                conf_dir=params.doris_be_conf_dir,
                configurations=params.config["configurations"]["core-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "core-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )
        if "hive-site" in params.config["configurations"]:
            XmlConfig(
                "hive-site.xml",
                conf_dir=params.doris_be_conf_dir,
                configurations=params.config["configurations"]["hive-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "hive-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )

    # gennerate doris_broker conf releate file
    if name == "doris_broker":
        Directory(
            params.doris_broker_bin_path,
            owner=params.doris_user,
            create_parents=True,
            group=params.user_group,
            mode=0o775,
        )

        File(
            os.path.join(params.doris_broker_conf_dir, "apache_hdfs_broker.conf"),
            content=InlineTemplate(
                params.config["configurations"]["doris-hdfs-broker-conf"]["content"]
            ),
            owner=params.doris_user,
            group=params.doris_group,
        )
        # create doris broker log4j.properties
        File(
            os.path.join(params.doris_broker_conf_dir, "log4j.properties"),
            owner=params.doris_user,
            group=params.user_group,
            content=InlineTemplate(
                params.config["configurations"]["doris-hdfs-broker-log4j-properties"][
                    "content"
                ]
            ),
            mode=0o644,
        )
        if "hdfs-site" in params.config["configurations"]:
            XmlConfig(
                "hdfs-site.xml",
                conf_dir=params.doris_broker_conf_dir,
                configurations=params.config["configurations"]["hdfs-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "hdfs-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )

        if "core-site" in params.config["configurations"]:
            XmlConfig(
                "core-site.xml",
                conf_dir=params.doris_broker_conf_dir,
                configurations=params.config["configurations"]["core-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "core-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )

        if "hive-site" in params.config["configurations"]:
            XmlConfig(
                "hive-site.xml",
                conf_dir=params.doris_broker_conf_dir,
                configurations=params.config["configurations"]["hive-site"],
                configuration_attributes=params.config["configurationAttributes"][
                    "hive-site"
                ],
                owner=params.doris_user,
                group=params.user_group,
                mode=0o644,
            )
