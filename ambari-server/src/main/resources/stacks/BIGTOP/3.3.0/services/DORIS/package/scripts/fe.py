import time

import grp
import pwd
import os
import socket

from resource_management import *
from doris import doris
from doris_service import doris_service
from setup_ranger_doris import setup_ranger_doris


class FE(Script):
    def install(self, env):
        import params

        env.set_params(params)
        # configure the correct package name(metainfo.xml) so that stack-select can find it
        fe_hostname = params.hostname
        Logger.info(fe_hostname)
        print((params.doris_fe_observer_hosts_list))
        if (
            len(params.doris_fe_observer_hosts_list) > 0
            and fe_hostname in params.doris_fe_observer_hosts_list
        ):
            Logger.info("FE  can not install with FE  OBSERVERin the same host !")
            raise Exception("FE can not install with FE  OBSERVER in the same host !")
        else:
            self.install_packages(env)
            # self.configure(env)
            Logger.info("install doris fe server successfully!")

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
        doris_service("doris", action="fe_stop")
        Logger.info("doris fe server stop successfully!")

    def start(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        setup_ranger_doris(upgrade_type=None, service_name="doris_fe")
        doris_service("doris", action="fe_start")
        Logger.info("doris fe server start successfully!")

    def status(self, env):
        import status_params

        check_process_status(status_params.doris_fe_pid_file)


if __name__ == "__main__":
    FE().execute()
