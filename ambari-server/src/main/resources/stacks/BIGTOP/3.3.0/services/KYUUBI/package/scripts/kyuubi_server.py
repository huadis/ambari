#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Licensed to the Apache Software Foundation (ASF) under one or more
contributor license agreements.  See the NOTICE file distributed with
this work for additional information regarding copyright ownership.
The ASF licenses this file to You under the Apache License, Version 2.0
(the "License"); you may not use this file except in compliance with
the License.  You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from resource_management import *
from resource_management.core.resources.system import File
from resource_management.core.logger import Logger
from resource_management.libraries.functions.check_process_status import \
    check_process_status
from kyuubi_utils import *
import pwd,grp
import os


class KyuubiServer(Script):

    def install(self, env):
        import params

        env.set_params(params)

        self.install_packages(env)

    def stop(self, env):
        import params
        env.set_params(params)

        Logger.info('Stopping Kyuubi server')
        Execute(get_stop_kyuubi_server_cmd(), user=params.kyuubi_user)

        Logger.info('Kyuubi server stopped')

    def start(self, env):
        import params
        env.set_params(params)

        Logger.info('Updating Kyuubi configuration')
        self.configure(env)

        Logger.info('Starting Kyuubi server')
        Execute(get_restart_kyuubi_server_cmd(), user=params.kyuubi_user)

        Logger.info('Kyuubi server successfully started')

    def status(self, env):
        import params
        env.set_params(params)
        pid_file = get_kyuubi_server_pid_file_path()
        check_process_status(pid_file)

    def configure(self, env):
        Logger.info('Configuring Kyuubi')
        import params
        env.set_params(params)
        kyuubi_conf_dir = os.path.join(params.KYUUBI_HOME, 'conf')

        File(os.path.join(kyuubi_conf_dir, 'kyuubi-defaults.conf'),
             content=Template("kyuubi-defaults.conf.j2"),
             owner=params.kyuubi_user,
             group=params.kyuubi_group
             )

        File(os.path.join(kyuubi_conf_dir, 'kyuubi-env.sh'),
             content=params.kyuubi_env,
             owner=params.kyuubi_user,
             group=params.kyuubi_group
             )

        File(os.path.join(kyuubi_conf_dir, 'log4j2.xml'),
             content=params.kyuubi_log4j2,
             owner=params.kyuubi_user,
             group=params.kyuubi_group
             )


if __name__ == '__main__':
    KyuubiServer().execute()
