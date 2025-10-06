#!/usr/bin/python
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
from resource_management import *
from resource_management.core import sudo
from resource_management.libraries.functions import check_process_status
import time
from categraf import categraf
from categraf_service import categraf_service


class CategrafClient(Script):
    def install(self, env):
        self.install_packages(env)

    def configure(self, env, upgrade_type=None, config_dir=None):
        import params

        env.set_params(params)
        self.initialize(env)
        categraf(name="server")

    def initialize(self, env):
        import params

        env.set_params(params)
        categraf_setup_marker = os.path.join(params.categraf_conf_dir, "categraf_setup")
        cmd_install = (f"{params.categraf_home}/categraf", "--install")
        if not os.path.exists(categraf_setup_marker):
            try:
                Execute(cmd_install, sudo=True)
                Logger.info(f"categraf init finished, cmd: {cmd_install}")
                File(
                    categraf_setup_marker,
                    owner=params.categraf_user,
                    group=params.categraf_group,
                    mode=0o640,
                )
            except Exception as e:
                Logger.exception(
                    "There was an exception when  ALTER SYSTEM ADD FOLLOWER: " + str(e)
                )

    def start(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        self.configure(env)
        categraf_service("server", action="start")

    def stop(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        categraf_service("server", action="stop")

    def status(self, env):
        import status_params

        env.set_params(status_params)
        check_process_status(status_params.categraf_pid_file)

    def get_user(self):
        import params

        return params.categraf_user

    def get_pid_files(self):
        import params

        return [params.categraf_pid_file]


if __name__ == "__main__":
    CategrafClient().execute()
