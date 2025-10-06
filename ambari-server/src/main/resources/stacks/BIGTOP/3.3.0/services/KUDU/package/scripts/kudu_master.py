#!/usr/bin/env python3
from resource_management import *
import os
from kudu_service import kudu_service
from kudu import kudu
from setup_ranger_kudu import setup_ranger_kudu

class KuduMaster(Script):
    def install(self, env):
        import params
        self.install_packages(env)
        self.configure(env)

    def configure(self, env):
        import params
        env.set_params(params)
        kudu(name = 'master')

    def start(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        self.configure(env)
        setup_ranger_kudu(upgrade_type=upgrade_type, service_name="kudu-master")
        kudu_service('master', action='start', upgrade_type=upgrade_type)

    def stop(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        kudu_service('master', action='stop', upgrade_type=upgrade_type)

    def status(self, env):
        import status_params
        env.set_params(status_params)
        check_process_status(status_params.kudu_master_pid)

if __name__ == "__main__":
    KuduMaster().execute()
