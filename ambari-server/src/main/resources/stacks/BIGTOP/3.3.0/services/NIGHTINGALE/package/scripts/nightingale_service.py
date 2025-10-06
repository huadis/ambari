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

# Python Imports
import os
import time

# Ambari Commons & Resource Management Imports
from ambari_commons.constants import UPGRADE_TYPE_ROLLING
from resource_management.core import shell
from resource_management.core import utils
from resource_management.core.exceptions import ComponentIsNotRunning, Fail
from resource_management.core.logger import Logger
from resource_management.core.resources.system import File, Execute
from resource_management.core.shell import as_user, quote_bash_args
from resource_management.libraries.functions import get_user_call_output
from resource_management.libraries.functions import StackFeature
from resource_management.libraries.functions.check_process_status import (
    check_process_status,
)
from resource_management.libraries.functions.decorator import retry
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.show_logs import show_logs
from resource_management.libraries.functions.stack_features import check_stack_feature


def nightingale_service(name, action="start", upgrade_type=None):
    import params
    import status_params

    wait_time = 5
    if name == "server":
        pid_file = params.nightingale_pid_file
        cmd_start = f"cd {params.nightingale_home};nohup ./n9e > {params.nightingale_log_dir}/nightingale.log 2>&1 < /dev/null &"

    pid = get_user_call_output.get_user_call_output(
        format("cat {pid_file}"), user=params.nightingale_user, is_checked_call=False
    )[1]
    process_id_exists_command = format(
        "ls {pid_file} >/dev/null 2>&1 && ps -p {pid} >/dev/null 2>&1"
    )

    if action == "start":
        daemon_cmd = cmd_start

        try:
            Execute(
                daemon_cmd,
                user=params.nightingale_user,
                path=params.nightingale_home,
                not_if=process_id_exists_command,
            )
            Execute(params.nightingale_pid_cmd, user=params.nightingale_user)
        except:
            show_logs(params.spark_log_dir, user=params.spark_user)
            raise

    elif action == "stop":
        Logger.info(format("stop nightingale server, pid : {pid} "))
        daemon_kill_cmd = format("{sudo} kill {pid}")
        daemon_hard_kill_cmd = format("{sudo} kill -9 {pid}")

        # kill cmd
        Execute(daemon_kill_cmd, not_if=format("! ({process_id_exists_command})"))

        # kill -9 cmd
        Execute(
            daemon_hard_kill_cmd,
            not_if=format(
                "! ({process_id_exists_command}) || ( sleep {wait_time} && ! ({process_id_exists_command}) )"
            ),
            ignore_failures=True,
        )

        try:
            # check if stopped the process, else fail the task
            Execute(format("! ({process_id_exists_command})"), tries=20, try_sleep=3)
        except:
            show_logs(params.nightingale_log_dir, params.nightingale_user)
            raise

        File(pid_file, action="delete")
