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

from seatunnel import seatunnel
from seatunnel_service import seatunnel_service
from resource_management import *
from resource_management import *
from resource_management.libraries.functions import check_process_status


class SeatunnelMaster(Script):
    def install(self, env):
        import params

        env.set_params(params)
        # configure the correct package name(metainfo.xml) so that stack-select can find it
        self.install_packages(env)
        Logger.info("install seatunnel master successfully!")

    def configure(self, env):
        import params

        env.set_params(params)
        seatunnel(name="seatunnel_master")
        Logger.info("configure seatunnel master successfully!")

    def start(self, env):
        import params

        env.set_params(params)
        self.configure(env)  # for security reason
        seatunnel_service("seatunnel", action="master_start")
        Logger.info("start seatunnel master successfully!")

    def stop(self, env):
        import params

        env.set_params(params)
        seatunnel_service("seatunnel", action="master_stop")
        Logger.info("stop seatunnel master successfully!")

    def restart(self, env):
        self.stop(env)
        self.start(env)

    def status(self, env):
        import params

        check_process_status(params.seatunnel_master_pid_file)

    def get_pid_files(self):
        import params

        return [params.seatunnel_master_pid_file]


if __name__ == "__main__":
    SeatunnelMaster().execute()
