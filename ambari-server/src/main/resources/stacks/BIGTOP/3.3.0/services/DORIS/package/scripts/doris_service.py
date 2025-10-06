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

import time
import socket
from resource_management import *
import os
import socket  # for gethostname
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
from resource_management.core import sudo


def doris_service(name, action=""):  # 'start' or 'stop' or 'status'
    # initializing the op command variables
    import params
    import status_params

    hostname = params.hostname
    doris_environment = {"JAVA_HOME": params.java_home}
    # "cd {doris_home} ;nohup ./doris --daemon start scm  > {doris_log_dir}/doris.log 2>&1 & echo $! > {doris_pid_file}")

    if params.security_enabled:
        Execute(params.doris_user_kinit_cmd, user=params.doris_user)

    if action == "fe_start":
        if not os.path.exists(params.fe_meta_dir):
            Execute("mkdir -p {0}".format(params.fe_meta_dir), user=params.doris_user)
            Execute(
                "chown -R {0}:{1} {2}".format(
                    params.doris_user, params.doris_group, params.fe_meta_dir
                ),
                user=params.doris_user,
            )

        if os.path.exists(status_params.doris_fe_pid_file):
            Execute(
                "rm -rf {0}".format(status_params.doris_fe_pid_file),
                user=params.doris_user,
            )

        if os.path.exists("{0}/fe.pid".format(params.doris_fe_bin_path)):
            Execute(
                "rm -rf {0}/fe.pid".format(params.doris_fe_bin_path),
                user=params.doris_user,
            )

        # judy flag file
        doris_fe_flag = "{0}/fe.flag".format(params.doris_fe_bin_path)
        if not os.path.exists(doris_fe_flag):
            # default first as fe master
            if params.doris_fe_host and params.doris_fe_host == params.hostname.lower():
                Logger.info("{0} is default master".format(params.hostname))
                Execute(
                    "{0}/start_fe.sh --daemon".format(params.doris_fe_bin_path),
                    user=params.doris_user,
                    environment=doris_environment,
                )
                time.sleep(10)
                if params.fe_root_password != "":
                    Execute(
                        "mysql -h {0} -P {1} -u root -e \"SET PASSWORD FOR 'root' = PASSWORD('{2}');\"".format(
                            params.doris_fe_host,
                            params.fe_query_port,
                            params.fe_root_password,
                        ),
                        user=params.doris_user,
                    )
                    Logger.info("Apache Doris root password has been set.")
            else:
                leader_fe_host = params.get_leader_fe_host()
                Execute(
                    "{0}/start_fe.sh --helper {1}:{2} --daemon".format(
                        params.doris_fe_bin_path,
                        leader_fe_host,
                        params.fe_edit_log_port,
                    ),
                    user=params.doris_user,
                    environment=doris_environment,
                )

                try:
                    hostname = params.hostname
                    hostip = socket.gethostbyname(hostname)
                    Execute(
                        "echo \"ALTER SYSTEM ADD FOLLOWER '{0}:{1}'; \" > /tmp/doris_add_fe_follower.sql &&  mysql -h {3} -P {4}  -u root {5} < /tmp/doris_add_fe_follower.sql ".format(
                            hostip,
                            params.fe_edit_log_port,
                            params.doris_client_bin_path,
                            leader_fe_host,
                            params.fe_query_port,
                            params.fe_root_password_sql,
                        ),
                        user=params.doris_user,
                    )

                    Logger.info(
                        "doris fe {0} add to cluster {1}.".format(
                            hostname, params.doris_fe_host
                        )
                    )

                except Exception as exception:
                    Logger.exception(
                        "There was an exception when  ALTER SYSTEM ADD FOLLOWER: "
                        + str(exception)
                    )

            # create flag
            File(
                os.path.join(params.doris_fe_bin_path, "fe.flag"),
                owner=params.doris_user,
                group=params.doris_group,
                content=hostname,
                mode=0o644,
            )
        else:
            Execute(
                "{0}/start_fe.sh --daemon".format(params.doris_fe_bin_path),
                user=params.doris_user,
                environment=doris_environment,
            )
            time.sleep(10)

        # generate pid,multiple judyment
        tryTimes = 5
        while tryTimes > 0:
            Execute(
                "ps -ef | grep org.apache.doris.PaloFe | grep -v grep | awk '{{print $2}}' > {0}".format(
                    status_params.doris_fe_pid_file
                ),
                user=params.doris_user,
            )
            if sudo.read_file(status_params.doris_fe_pid_file) == b"":
                Execute(
                    "ps -ef | grep org.apache.doris.DorisFE | grep -v grep | awk '{{print $2}}' > {0}".format(
                        status_params.doris_fe_pid_file
                    ),
                    user=params.doris_user,
                )
            if sudo.read_file(status_params.doris_fe_pid_file) != b"":
                break
            else:
                Logger.info("waiting for fe start...")
                time.sleep(60)
                tryTimes = tryTimes - 1
        if tryTimes == 0:
            Logger.error("start error,pls check logs.")
        time.sleep(1)

        Logger.info("doris fe start.")

    elif action == "fe_stop":
        if (
            os.path.exists(status_params.doris_fe_pid_file)
            and sudo.read_file(status_params.doris_fe_pid_file) != b""
        ):
            Execute(
                "cat {0} > {1}/fe.pid".format(
                    status_params.doris_fe_pid_file, params.doris_fe_bin_path
                ),
                user=params.doris_user,
            )

        pidfile = "{0}/fe.pid".format(params.doris_fe_bin_path)
        if os.path.exists(pidfile) and params.check_process_exists(pidfile):
            Execute(
                "{0}/stop_fe.sh".format(params.doris_fe_bin_path),
                user=params.doris_user,
                environment=doris_environment,
            )

        Execute(
            "rm -rf {0}".format(status_params.doris_fe_pid_file), user=params.doris_user
        )
        Logger.info("doris fe stop.")

    elif action == "fe_observer_start":
        if not os.path.exists(params.fe_meta_dir):
            Execute("mkdir -p {0}".format(params.fe_meta_dir), user=params.doris_user)
            Execute(
                "chown -R {0}:{1} {2}".format(
                    params.doris_user, params.doris_group, params.fe_meta_dir
                ),
                user=params.doris_user,
            )

        if os.path.exists(status_params.doris_fe_pid_file):
            Execute(
                "rm -rf {0}".format(status_params.doris_fe_pid_file),
                user=params.doris_user,
            )

        if os.path.exists("{0}/fe.pid".format(params.doris_fe_bin_path)):
            Execute(
                "rm -rf {0}/fe.pid".format(params.doris_fe_bin_path),
                user=params.doris_user,
            )

        # judy flag file
        doris_fe_flag = "{0}/fe.flag".format(params.doris_fe_bin_path)
        leader_fe_host = params.get_leader_fe_host()
        if leader_fe_host != "" and not os.path.exists(doris_fe_flag):
            Execute(
                "{0}/start_fe.sh --helper {1}:{2} --daemon".format(
                    params.doris_fe_bin_path, leader_fe_host, params.fe_edit_log_port
                ),
                user=params.doris_user,
                environment=doris_environment,
            )
            try:
                hostname = params.hostname
                hostip = socket.gethostbyname(hostname)
                # ALTER SYSTEM ADD FOLLOWER "follower_host:edit_log_port";
                Execute(
                    "echo \"ALTER SYSTEM ADD OBSERVER  '{0}:{1}'; \" > /tmp/doris_add_fe_observer.sql &&  mysql -h {3} -P {4}  -u root {5} < /tmp/doris_add_fe_observer.sql ".format(
                        hostip,
                        params.fe_edit_log_port,
                        params.doris_client_bin_path,
                        leader_fe_host,
                        params.fe_query_port,
                        params.fe_root_password_sql,
                    ),
                    user=params.doris_user,
                )
                Logger.info(
                    "doris fe {0} add to cluster {1}.".format(
                        hostname, params.doris_fe_host
                    )
                )
            except Exception as exception:
                Logger.exception(
                    "There was an exception when  ALTER SYSTEM ADD OBSERVER: "
                    + str(exception)
                )

            # create flag
            File(
                os.path.join(params.doris_fe_bin_path, "fe.flag"),
                owner=params.doris_user,
                group=params.doris_group,
                content=hostname,
                mode=0o644,
            )
        else:
            Execute(
                "{0}/start_fe.sh --daemon".format(params.doris_fe_bin_path),
                user=params.doris_user,
                environment=doris_environment,
            )
            time.sleep(10)

        # generate pid
        tryTimes = 5
        while tryTimes > 0:
            Execute(
                "ps -ef | grep org.apache.doris.PaloFe | grep -v grep | awk '{{print $2}}' > {0}".format(
                    status_params.doris_fe_pid_file
                ),
                user=params.doris_user,
            )
            if sudo.read_file(status_params.doris_fe_pid_file) == b"":
                Execute(
                    "ps -ef | grep org.apache.doris.DorisFE | grep -v grep | awk '{{print $2}}' > {0}".format(
                        status_params.doris_fe_pid_file
                    ),
                    user=params.doris_user,
                )
            if sudo.read_file(status_params.doris_fe_pid_file) != b"":
                break
            else:
                Logger.info("waiting for fe observer start...")
                time.sleep(60)
                tryTimes = tryTimes - 1
        if tryTimes == 0:
            Logger.error("start error,pls check logs.")
        time.sleep(1)

        Logger.info("doris fe observer start.")

    elif action == "fe_observer_stop":
        if (
            os.path.exists(status_params.doris_fe_pid_file)
            and sudo.read_file(status_params.doris_fe_pid_file) != b""
        ):
            Execute(
                "cat {0} > {1}/fe.pid".format(
                    status_params.doris_fe_pid_file, params.doris_fe_bin_path
                ),
                user=params.doris_user,
            )

        pidfile = "{0}/fe.pid".format(params.doris_fe_bin_path)
        if os.path.exists(pidfile) and params.check_process_exists(pidfile):
            Execute(
                "{0}/stop_fe.sh".format(params.doris_fe_bin_path),
                user=params.doris_user,
                environment=doris_environment,
            )
        Execute(
            "rm -rf {0}".format(status_params.doris_fe_pid_file), user=params.doris_user
        )
        Logger.info("doris fe observer stop.")

    elif action == "be_start":
        # sed -i '/Please disable swap memory/,/exit 1/{/exit 1/d;}' ./usr/bigtop/3.3.0/usr/lib/doris-be/bin/start_be.sh
        Execute(
            f"sed -i '/Please disable swap memory/,/exit 1/{{/exit 1/d;}}' {params.doris_be_bin_path}/start_be.sh",
            user="root",
        )

        # start be
        # data dir
        dirs = []
        for i in params.storage_root_path.split(";"):
            dirs.append(i.split(",")[0].strip())
        dirs = [i for i in dirs if i != ""]
        for dir in dirs:
            if not os.path.exists(dir):
                Execute(format("{{sudo}} mkdir -p {0}".format(dir)))
                Execute(
                    format(
                        "{{sudo}} chown -R {0}:{1} {2}".format(
                            params.doris_user, params.doris_group, dir
                        )
                    )
                )

        # spill dir
        be_spill_dir = params.spill_storage_root_path
        if not os.path.exists(be_spill_dir):
            Execute(format("{{sudo}} mkdir -p {0}".format(be_spill_dir)))
            Execute(
                format(
                    "{{sudo}} chown -R {0}:{1} {2}".format(
                        params.doris_user, params.doris_group, be_spill_dir
                    )
                )
            )

        Execute(
            "rm -rf {0}".format(status_params.doris_be_pid_file), user=params.doris_user
        )
        Execute(
            "rm -rf {0}/be.pid".format(params.doris_be_bin_path), user=params.doris_user
        )
        # Start Doris BE Server
        Execute(
            "{0}/start_be.sh --daemon".format(params.doris_be_bin_path),
            user=params.doris_user,
        )
        time.sleep(10)

        tryTimes = 5
        while tryTimes > 0:
            Execute(
                "ps -ef | grep doris-be/lib/doris_be | grep -v grep | awk '{{print $2}}' > {0}".format(
                    status_params.doris_be_pid_file
                ),
                user=params.doris_user,
            )
            if sudo.read_file(status_params.doris_be_pid_file) != b"":
                break
            else:
                Logger.info("waiting for be start...")
                time.sleep(60)
                tryTimes = tryTimes - 1
        if tryTimes == 0:
            Logger.error("start error,pls check logs.")

        time.sleep(1)

        # add be to fe
        doris_service("doris", action="be_add_fe")

        Logger.info("doris be start.")

    elif action == "be_stop":
        # Stop Doris BE Server
        if (
            os.path.exists(status_params.doris_be_pid_file)
            and sudo.read_file(status_params.doris_be_pid_file) != b""
        ):
            Execute(
                "cat {0} > {1}/be.pid".format(
                    status_params.doris_be_pid_file, params.doris_be_bin_path
                ),
                user=params.doris_user,
            )

        pidfile = "{0}/be.pid".format(params.doris_be_bin_path)
        if os.path.exists(pidfile) and params.check_process_exists(pidfile):
            Execute(
                "{0}/stop_be.sh".format(params.doris_be_bin_path),
                user=params.doris_user,
            )

        Execute(
            "rm -rf {0}".format(status_params.doris_be_pid_file), user=params.doris_user
        )

        Logger.info("doris be stop.")

    elif action == "be_add_fe":
        # add be to fe
        leader_fe_host = params.get_leader_fe_host()
        Logger.info(" leader_fe_host : {0}".format(leader_fe_host))
        if leader_fe_host != "":
            try:
                Execute(
                    "echo \"ALTER SYSTEM ADD BACKEND '{0}:{1}'; \" > /tmp/doris_add_be.sql && mysql -h {3} -P {4}  -u root {5} < /tmp/doris_add_be.sql ".format(
                        params.hostname,
                        params.be_heartbeat_service_port,
                        params.doris_client_bin_path,
                        leader_fe_host,
                        params.fe_query_port,
                        params.fe_root_password_sql,
                    ),
                    user=params.doris_user,
                )

                Logger.info(
                    "doris be {0} add to fe {1}.".format(
                        params.hostname, params.doris_fe_host
                    )
                )
            except Exception as exception:
                Logger.exception(
                    "There was an exception when  ALTER SYSTEM ADD BACKEND: "
                    + str(exception)
                )
        else:
            Logger.error("doris fe not exists !")
            raise Exception("doris fe not exists !")

    elif action == "be_decommission_fe":
        # delete be from fe  DECOMMISSION
        leader_fe_host = params.get_leader_fe_host()
        Logger.info(" leader_fe_host : {0}".format(leader_fe_host))
        if leader_fe_host:
            Execute(
                "echo \"ALTER SYSTEM DECOMMISSION BACKEND '{0}:{1}'; \" > /tmp/doris_drop_be.sql &&  mysql -h {3} -P {4}  -u root {5} < /tmp/doris_drop_be.sql ".format(
                    params.hostname,
                    params.be_heartbeat_service_port,
                    params.doris_client_bin_path,
                    leader_fe_host,
                    params.fe_query_port,
                    params.fe_root_password_sql,
                ),
                user=params.doris_user,
            )

            Logger.info(
                "doris be {0} delete from fe {1}.".format(
                    params.hostname, params.doris_fe_host
                )
            )
        else:
            Logger.error("doris fe not exists !")
            raise Exception("doris fe not exists !")

    elif action == "broker_start":
        Execute(
            "rm -rf {0}".format(status_params.doris_broker_pid_file),
            user=params.doris_user,
        )
        Execute(
            "rm -rf {0}/apache_hdfs_broker.pid".format(params.doris_broker_bin_path),
            user=params.doris_user,
        )

        leader_fe_host = params.get_leader_fe_host()
        Logger.info(" leader_fe_host : {0}".format(leader_fe_host))
        if leader_fe_host != "":
            Execute(
                "{0}/start_broker.sh --daemon".format(params.doris_broker_bin_path),
                user=params.doris_user,
                environment=doris_environment,
            )
            time.sleep(10)
            try:
                # ALTER SYSTEM ADD FOLLOWER "follower_host:edit_log_port";
                Execute(
                    "echo \"ALTER SYSTEM ADD BROKER broker_name  '{0}:{1}'; \" > /tmp/doris_add_broker.sql &&  mysql -h {3} -P {4}  -u root {5} < /tmp/doris_add_broker.sql ".format(
                        params.hostname,
                        params.broker_ipc_port,
                        params.doris_client_bin_path,
                        leader_fe_host,
                        params.fe_query_port,
                        params.fe_root_password_sql,
                    ),
                    user=params.doris_user,
                )
                Logger.info(
                    "doris hdfs broker {0} add to fe {1}.".format(
                        params.hostname, params.doris_fe_host
                    )
                )
            except Exception as exception:
                Logger.exception(
                    "There was an exception when  ALTER SYSTEM ADD BROKER: "
                    + str(exception)
                )

        tryTimes = 5
        while tryTimes > 0:
            Execute(
                "ps -ef | grep org.apache.doris.broker.hdfs.BrokerBootstrap | grep -v grep | awk '{{print $2}}' > {0}".format(
                    status_params.doris_broker_pid_file
                ),
                user=params.doris_user,
            )
            if sudo.read_file(status_params.doris_broker_pid_file) != b"":
                break
            else:
                Logger.info("waiting for apache_hdfs_broker start...")
                time.sleep(60)
                tryTimes = tryTimes - 1
        if tryTimes == 0:
            Logger.error("start error,pls check logs.")
        time.sleep(1)

        Logger.info("doris broker start.")

    elif action == "broker_stop":
        if (
            os.path.exists(status_params.doris_broker_pid_file)
            and sudo.read_file(status_params.doris_broker_pid_file) != b""
        ):
            Execute(
                "cat {0} > {1}/apache_hdfs_broker.pid".format(
                    status_params.doris_broker_pid_file, params.doris_broker_bin_path
                ),
                user=params.doris_user,
            )
        # apache_hdfs_broker.pid
        pidfile = "{0}/apache_hdfs_broker.pid".format(params.doris_broker_bin_path)
        if os.path.exists(pidfile) and params.check_process_exists(pidfile):
            Execute(
                "{0}/stop_broker.sh".format(params.doris_broker_bin_path),
                user=params.doris_user,
                environment=doris_environment,
            )

        Execute(
            "rm -rf {0}".format(status_params.doris_broker_pid_file),
            user=params.doris_user,
        )

        Logger.info("doris broker stop.")

    else:
        Logger.info(format("unknown command type: :{action}"))
