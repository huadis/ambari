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
def seatunnel(name=None):
    import params

    Directory(
        params.seatunnel_log_dir_prefix,
        owner=params.seatunnel_user,
        create_parents=True,
        group=params.user_group,
        mode=0o775,
    )

    Directory(
        params.seatunnel_pid_dir_prefix,
        owner=params.seatunnel_user,
        create_parents=True,
        group=params.user_group,
        mode=0o775,
    )

    Directory(
        params.seatunnel_log_dir,
        owner=params.seatunnel_user,
        create_parents=True,
        group=params.user_group,
        mode=0o755,
    )

    Directory(
        params.seatunnel_pid_dir,
        owner=params.seatunnel_user,
        create_parents=True,
        group=params.user_group,
        mode=0o755,
    )

    if name == "seatunnel_web":
        Directory(
            params.seatunnel_web_bin_dir,
            owner=params.seatunnel_user,
            create_parents=True,
            group=params.user_group,
            mode=0o775,
        )

        File(
            os.path.join(params.seatunnel_web_conf_dir, "application.yml"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-web-application"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )
        File(
            os.path.join(params.seatunnel_web_conf_dir, "hazelcast-client.yaml"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-hazelcast-client"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )
        File(
            os.path.join(params.seatunnel_web_conf_dir, "plugin-mapping.properties"),
            content=InlineTemplate(
                params.config["configurations"]["plugin-mapping-properties"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )
    else:
        File(
            os.path.join(params.seatunnel_conf_dir, "hazelcast-client.yaml"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-hazelcast-client"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )
        File(
            os.path.join(params.seatunnel_home, "connectors/plugin-mapping.properties"),
            content=InlineTemplate(
                params.config["configurations"]["plugin-mapping-properties"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "hazelcast.yaml"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-hazelcast"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "jvm_client_options"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-jvm_client_options"][
                    "content"
                ]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "jvm_options"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-jvm_options"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "log4j2.properties"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-log4j2"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "log4j2_client.properties"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-log4j2_client"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "plugin_config"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-plugin_config"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "seatunnel.yaml"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-seatunnel"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        File(
            os.path.join(params.seatunnel_conf_dir, "seatunnel-env.sh"),
            content=InlineTemplate(
                params.config["configurations"]["seatunnel-env"]["content"]
            ),
            owner=params.seatunnel_user,
            group=params.user_group,
            mode=0o755,
        )

        if name == "seatunnel_master":
            File(
                os.path.join(params.seatunnel_conf_dir, "hazelcast-master.yaml"),
                content=InlineTemplate(
                    params.config["configurations"]["seatunnel-hazelcast-master"][
                        "content"
                    ]
                ),
                owner=params.seatunnel_user,
                group=params.user_group,
                mode=0o755,
            )
            File(
                os.path.join(params.seatunnel_conf_dir, "jvm_master_options"),
                content=InlineTemplate(
                    params.config["configurations"]["seatunnel-jvm_master_options"][
                        "content"
                    ]
                ),
                owner=params.seatunnel_user,
                group=params.user_group,
                mode=0o755,
            )
            if params.seatunnel_fs_hdfs_type.lower() == "hdfs":
                # Create hdfs Dir
                params.HdfsResource(
                    params.seatunnel_fs_hdfs_path,
                    type="directory",
                    action="create_on_execute",
                    owner=params.seatunnel_user,
                    mode=0o777,
                )
                params.HdfsResource(None, action="execute")

        if name == "seatunnel_worker":
            File(
                os.path.join(params.seatunnel_conf_dir, "hazelcast-worker.yaml"),
                content=InlineTemplate(
                    params.config["configurations"]["seatunnel-hazelcast-worker"][
                        "content"
                    ]
                ),
                owner=params.seatunnel_user,
                group=params.user_group,
                mode=0o755,
            )
            File(
                os.path.join(params.seatunnel_conf_dir, "jvm_worker_options"),
                content=InlineTemplate(
                    params.config["configurations"]["seatunnel-jvm_worker_options"][
                        "content"
                    ]
                ),
                owner=params.seatunnel_user,
                group=params.user_group,
                mode=0o755,
            )
