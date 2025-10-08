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


def dolphin_env():
    import params
    Directory(
        params.dolphin_common_map["data.basedir.path"],
        mode=0o777,
        owner=params.dolphin_user,
        group=params.dolphin_group,
        create_parents=True,
    )

    File(
        format(params.dolphin_env_path),
        mode=0o755,
        content=InlineTemplate(params.dolphin_env_content),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        format(params.dolphin_env_path),
        mode=0o755,
        content=InlineTemplate(params.dolphin_env_content),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    # alert-server
    File(
        os.path.join(params.dolphin_alert_server_conf_dir, "application.yaml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-alert-server-application"][
                "content"
            ]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_alert_server_conf_dir, "common.properties"),
        mode=0o755,
        content=Template("common.properties.j2"),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_alert_server_conf_dir, "logback-spring.xml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-alert-server-logback-spring"][
                "content"
            ]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    # api-server
    File(
        os.path.join(params.dolphin_api_server_conf_dir, "application.yaml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-api-server-application"]["content"]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_api_server_conf_dir, "common.properties"),
        mode=0o755,
        content=Template("common.properties.j2"),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_api_server_conf_dir, "logback-spring.xml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-api-server-logback-spring"][
                "content"
            ]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    # mastr server
    File(
        os.path.join(params.dolphin_master_server_conf_dir, "application.yaml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-master-server-application"][
                "content"
            ]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_master_server_conf_dir, "common.properties"),
        mode=0o755,
        content=Template("common.properties.j2"),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_master_server_conf_dir, "logback-spring.xml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-master-server-logback-spring"][
                "content"
            ]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    # worker server
    File(
        os.path.join(params.dolphin_worker_server_conf_dir, "application.yaml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-worker-server-application"][
                "content"
            ]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_worker_server_conf_dir, "common.properties"),
        mode=0o755,
        content=Template("common.properties.j2"),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    File(
        os.path.join(params.dolphin_worker_server_conf_dir, "logback-spring.xml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-worker-server-logback-spring"][
                "content"
            ]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    # tools
    File(
        os.path.join(params.dolphin_tools_conf_dir, "application.yaml"),
        content=InlineTemplate(
            params.config["configurations"]["dolphin-tools-application"]["content"]
        ),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    # tools
    File(
        os.path.join(params.dolphin_tools_conf_dir, "common.properties"),
        mode=0o755,
        content=Template("common.properties.j2"),
        owner=params.dolphin_user,
        group=params.dolphin_group,
    )

    # Configuration needed to support NN HA
    XmlConfig(
        "hdfs-site.xml",
        conf_dir=params.dolphin_alert_server_conf_dir,
        configurations=params.config["configurations"]["hdfs-site"],
        configuration_attributes=params.config["configurationAttributes"]["hdfs-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )

    XmlConfig(
        "core-site.xml",
        conf_dir=params.dolphin_alert_server_conf_dir,
        configurations=params.config["configurations"]["core-site"],
        configuration_attributes=params.config["configurationAttributes"]["core-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )
    XmlConfig(
        "hdfs-site.xml",
        conf_dir=params.dolphin_api_server_conf_dir,
        configurations=params.config["configurations"]["hdfs-site"],
        configuration_attributes=params.config["configurationAttributes"]["hdfs-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )

    XmlConfig(
        "core-site.xml",
        conf_dir=params.dolphin_api_server_conf_dir,
        configurations=params.config["configurations"]["core-site"],
        configuration_attributes=params.config["configurationAttributes"]["core-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )
    XmlConfig(
        "hdfs-site.xml",
        conf_dir=params.dolphin_master_server_conf_dir,
        configurations=params.config["configurations"]["hdfs-site"],
        configuration_attributes=params.config["configurationAttributes"]["hdfs-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )

    XmlConfig(
        "core-site.xml",
        conf_dir=params.dolphin_master_server_conf_dir,
        configurations=params.config["configurations"]["core-site"],
        configuration_attributes=params.config["configurationAttributes"]["core-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )
    XmlConfig(
        "hdfs-site.xml",
        conf_dir=params.dolphin_worker_server_conf_dir,
        configurations=params.config["configurations"]["hdfs-site"],
        configuration_attributes=params.config["configurationAttributes"]["hdfs-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )

    XmlConfig(
        "core-site.xml",
        conf_dir=params.dolphin_worker_server_conf_dir,
        configurations=params.config["configurations"]["core-site"],
        configuration_attributes=params.config["configurationAttributes"]["core-site"],
        owner=params.dolphin_user,
        group=params.dolphin_user,
        mode=0o644,
    )

    if params.resource_storage_type == "HDFS":
        # Create hdfs Dir
        params.HdfsResource(
            params.resource_storage_upload_base_path,
            type="directory",
            action="create_on_execute",
            owner=params.dolphin_user,
            mode=0o777,
        )
        params.HdfsResource(None, action="execute")
