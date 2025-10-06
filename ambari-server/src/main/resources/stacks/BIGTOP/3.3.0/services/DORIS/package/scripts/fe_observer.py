import time

import grp
import pwd
import os
import socket

from resource_management import *
from doris import doris
from doris_service import doris_service
from setup_ranger_doris import setup_ranger_doris


class FE_OBSERVER(Script):
    def install(self, env):
        import params

        env.set_params(params)
        # configure the correct package name(metainfo.xml) so that stack-select can find it
        fe_observer_hostname = socket.gethostname()
        Logger.info(fe_observer_hostname)
        print(params.doris_fe_hosts_list)
        if (
            len(params.doris_fe_hosts_list) > 0
            and fe_observer_hostname in params.doris_fe_hosts_list
        ):
            Logger.info("FE OBSERVER can not install with FE in the same host !")
            raise Exception("FE OBSERVER can not install with FE in the same host !")
        else:
            self.install_packages(env)
            # self.configure(env)
            Logger.info("install doris fe observer server successfully!")

    def configure(self, env, isInstall=False):
        import params
        import status_params

        env.set_params(params)
        env.set_params(status_params)
        doris(name="doris_fe")
        Logger.info("configure doris fe server successfully!")

    def stop(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        doris_service("doris", action="fe_observer_stop")
        Logger.info("doris fe server stop successfully!")

    def start(self, env):
        import params, status_params

        fe_observer_hostname = socket.gethostname()
        Logger.info(fe_observer_hostname)
        print(params.doris_fe_hosts_list)
        if (
            len(params.doris_fe_hosts_list) > 0
            and fe_observer_hostname in params.doris_fe_hosts_list
        ):
            Logger.info("FE OBSERVER can not install with FE in the same host !")
            raise Exception("FE OBSERVER can not install with FE in the same host !")

        self.configure(env)
        env.set_params(params)
        setup_ranger_doris(upgrade_type=None, service_name="doris_fe_observer")
        doris_service("doris", action="fe_observer_start")
        Logger.info("doris fe server  observer start successfully!")

    def status(self, env):
        import status_params

        check_process_status(status_params.doris_fe_pid_file)


if __name__ == "__main__":
    FE_OBSERVER().execute()
