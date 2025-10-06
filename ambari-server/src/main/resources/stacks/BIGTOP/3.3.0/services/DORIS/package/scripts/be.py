import time

import grp
import pwd
import os

from resource_management import *
from doris import doris
from doris_service import doris_service


class BE(Script):
    def install(self, env):
        import params

        env.set_params(params)
        # configure the correct package name(metainfo.xml) so that stack-select can find it
        self.install_packages(env)
        # self.configure(env)
        Logger.info("install doris be server successfully!")

    def configure(self, env, isInstall=False):
        import params
        import status_params

        env.set_params(params)
        env.set_params(status_params)
        doris(name="doris_be")
        Logger.info("configure doris be server successfully!")

    def stop(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        doris_service("doris", action="be_stop")
        Logger.info("doris fe server stop successfully!")

    def start(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        doris_service("doris", action="be_start")
        Logger.info("doris fe server start successfully!")

    def status(self, env):
        import status_params

        check_process_status(status_params.doris_be_pid_file)

    def decommission(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        doris_service("doris", action="be_decommission_fe")
        Logger.info("doris be decommission finished!")

    def readd(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        doris_service("doris", action="be_add_fe")
        Logger.info("doris be add operateion finished!")


if __name__ == "__main__":
    BE().execute()
