import time

import grp
import pwd
import os

from resource_management import *
from doris import doris
from doris_service import doris_service


class Broker(Script):
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
        doris(name="doris_broker")
        Logger.info("configure doris fe server successfully!")

    def start(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        doris_service("doris", action="broker_start")
        Logger.info("start doris broker server start successfully!")

    def stop(self, env):
        import params, status_params

        self.configure(env)
        env.set_params(params)
        doris_service("doris", action="broker_stop")
        Logger.info("start doris broker server stop successfully!")

    def status(self, env):
        import status_params

        check_process_status(status_params.doris_broker_pid_file)


if __name__ == "__main__":
    Broker().execute()
