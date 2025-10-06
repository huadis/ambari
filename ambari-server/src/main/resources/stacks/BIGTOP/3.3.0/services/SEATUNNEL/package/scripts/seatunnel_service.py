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

from resource_management import *
import os
import time
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
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


def seatunnel_service(name, action="start_server"):  # 'start' or 'stop' or 'status'
    # initializing the op command variables
    import params

    master_pid = get_user_call_output.get_user_call_output(
        format("head -n 1 {seatunnel_master_pid_file}"),
        user=params.seatunnel_user,
        is_checked_call=False,
    )[1]
    master_process_id_exists_command = format(
        "ls {seatunnel_master_pid_file} >/dev/null 2>&1 && ps -p {master_pid} >/dev/null 2>&1"
    )

    worker_pid = get_user_call_output.get_user_call_output(
        format("head -n 1 {seatunnel_worker_pid_file}"),
        user=params.seatunnel_user,
        is_checked_call=False,
    )[1]
    worker_process_id_exists_command = format(
        "ls {seatunnel_worker_pid_file} >/dev/null 2>&1 && ps -p {worker_pid} >/dev/null 2>&1"
    )

    web_pid = get_user_call_output.get_user_call_output(
        format("head -n 1 {seatunnel_web_pid_file}"),
        user=params.seatunnel_user,
        is_checked_call=False,
    )[1]
    process_web_id_exists_command = format(
        "ls {seatunnel_web_pid_file} >/dev/null 2>&1 && ps -p {web_pid} >/dev/null 2>&1"
    )

    if action == "master_start":
        # cmd = format("cd {seatunnel_home};./bin/seatunnel-cluster.sh 2>&1 & ")
        cmd = format("cd {seatunnel_home};./bin/seatunnel-cluster.sh -r master 2>&1 & ")
        Execute(cmd, user=params.seatunnel_user, logoutput=True)
        time.sleep(10)

        tryTimes = 5
        while tryTimes > 0:
            Execute(
                "ps -ef | grep java | grep 'org.apache.seatunnel.core.starter.seatunnel.SeaTunnelServer' | grep 'master' | awk '{{print $2}}' > {0}".format(
                    params.seatunnel_master_pid_file
                ),
                user=params.seatunnel_user,
            )
            master_pid = get_user_call_output.get_user_call_output(
                format("head -n 1 {seatunnel_master_pid_file}"),
                user=params.seatunnel_user,
                is_checked_call=False,
            )[1]
            Logger.info(format("start seatunnel master, master_pid : {master_pid} "))
            if master_pid != "":
                Execute(
                    "first_line=$(head -n 1 {0} ) ; echo $first_line >  {0} ".format(
                        params.seatunnel_master_pid_file
                    ),
                    user=params.seatunnel_user,
                )
                break
            else:
                Logger.info("waiting for seatunnel master start...")
                time.sleep(30)
                tryTimes = tryTimes - 1
        if tryTimes == 0:
            Logger.error("start error,pls check logs.")

        time.sleep(1)

    elif action == "master_stop":
        wait_time = 5
        Logger.info(format("stop seatunnel master, master_pid : {master_pid} "))
        daemon_kill_cmd = format("{sudo} kill {master_pid}")
        daemon_hard_kill_cmd = format("{sudo} kill -9 {master_pid}")

        # kill cmd
        Execute(
            daemon_kill_cmd, not_if=format("! ({master_process_id_exists_command})")
        )

        # kill -9 cmd
        Execute(
            daemon_hard_kill_cmd,
            not_if=format(
                "! ({master_process_id_exists_command}) || ( sleep {wait_time} && ! ({master_process_id_exists_command}) )"
            ),
            ignore_failures=True,
        )

        try:
            # check if stopped the process, else fail the task
            Execute(
                format("! ({master_process_id_exists_command})"), tries=20, try_sleep=3
            )
        except:
            show_logs(params.seatunnel_log_dir, params.seatunnel_user)
            raise

        File(params.seatunnel_master_pid_file, action="delete")

    if action == "worker_start":
        # cmd = format("cd {seatunnel_home};./bin/seatunnel-cluster.sh 2>&1 & ")
        cmd = format("cd {seatunnel_home};./bin/seatunnel-cluster.sh -r worker 2>&1 & ")
        Execute(cmd, user=params.seatunnel_user, logoutput=True)
        time.sleep(10)

        tryTimes = 5
        while tryTimes > 0:
            Execute(
                "ps -ef | grep java | grep 'org.apache.seatunnel.core.starter.seatunnel.SeaTunnelServer' | grep 'worker' | awk '{{print $2}}' > {0}".format(
                    params.seatunnel_worker_pid_file
                ),
                user=params.seatunnel_user,
            )
            worker_pid = get_user_call_output.get_user_call_output(
                format("head -n 1 {seatunnel_worker_pid_file}"),
                user=params.seatunnel_user,
                is_checked_call=False,
            )[1]
            Logger.info(format("start seatunnel worker, worker_pid : {worker_pid} "))
            if worker_pid != "":
                Execute(
                    "first_line=$(head -n 1 {0} ) ; echo $first_line >  {0} ".format(
                        params.seatunnel_worker_pid_file
                    ),
                    user=params.seatunnel_user,
                )
                break
            else:
                Logger.info("waiting for seatunnel worker start...")
                time.sleep(30)
                tryTimes = tryTimes - 1
        if tryTimes == 0:
            Logger.error("start error,pls check logs.")

        time.sleep(1)

    elif action == "worker_stop":
        wait_time = 5
        Logger.info(format("stop seatunnel worker, worker_pid : {worker_pid} "))
        daemon_kill_cmd = format("{sudo} kill {worker_pid}")
        daemon_hard_kill_cmd = format("{sudo} kill -9 {worker_pid}")

        # kill cmd
        Execute(
            daemon_kill_cmd, not_if=format("! ({worker_process_id_exists_command})")
        )

        # kill -9 cmd
        Execute(
            daemon_hard_kill_cmd,
            not_if=format(
                "! ({worker_process_id_exists_command}) || ( sleep {wait_time} && ! ({worker_process_id_exists_command}) )"
            ),
            ignore_failures=True,
        )

        try:
            # check if stopped the process, else fail the task
            Execute(
                format("! ({worker_process_id_exists_command})"), tries=20, try_sleep=3
            )
        except:
            show_logs(params.seatunnel_log_dir, params.seatunnel_user)
            raise

        File(params.seatunnel_worker_pid_file, action="delete")

    if action == "web_start":
        webExecEnv = {
            "SEATUNNEL_HOME": "/usr/bigtop/current/seatunnel",
            "JAVA_HOME": params.java_home,
        }
        cmd = format(
            "cd {seatunnel_web_home};./bin/seatunnel-backend-daemon.sh start 2>&1 & "
        )
        Execute(cmd, user=params.seatunnel_user, logoutput=True, environment=webExecEnv)
        time.sleep(10)

        tryTimes = 5
        while tryTimes > 0:
            Execute(
                "ps -ef | grep java | grep 'org.apache.seatunnel.app.SeatunnelApplication' | awk '{{print $2}}' > {0}".format(
                    params.seatunnel_web_pid_file
                ),
                user=params.seatunnel_user,
            )
            web_pid = get_user_call_output.get_user_call_output(
                format("head -n 1 {seatunnel_web_pid_file}"),
                user=params.seatunnel_user,
                is_checked_call=False,
            )[1]
            Logger.info(format("start seatunnel web, pid : {web_pid} "))
            if web_pid != "":
                Execute(
                    "first_line=$(head -n 1 {0} ) ; echo $first_line >  {0} ".format(
                        params.seatunnel_web_pid_file
                    ),
                    user=params.seatunnel_user,
                )
                break
            else:
                Logger.info("waiting for seatunnel web start...")
                time.sleep(30)
                tryTimes = tryTimes - 1
        if tryTimes == 0:
            Logger.error("start error,pls check logs.")

        time.sleep(1)

    elif action == "web_stop":
        wait_time = 5
        Logger.info(format("stop seatunnel web, pid : {web_pid} "))
        daemon_kill_cmd = format("{sudo} kill {web_pid}")
        daemon_hard_kill_cmd = format("{sudo} kill -9 {web_pid}")

        # kill cmd
        Execute(daemon_kill_cmd, not_if=format("! ({process_web_id_exists_command})"))

        # kill -9 cmd
        Execute(
            daemon_hard_kill_cmd,
            not_if=format(
                "! ({process_web_id_exists_command}) || ( sleep {wait_time} && ! ({process_web_id_exists_command}) )"
            ),
            ignore_failures=True,
        )

        try:
            # check if stopped the process, else fail the task
            Execute(
                format("! ({process_web_id_exists_command})"), tries=20, try_sleep=3
            )
        except:
            show_logs(params.seatunnel_log_dir, params.seatunnel_user)
            raise

        File(params.seatunnel_web_pid_file, action="delete")

    else:
        Logger.info(format("unknown command type: :{action}"))
