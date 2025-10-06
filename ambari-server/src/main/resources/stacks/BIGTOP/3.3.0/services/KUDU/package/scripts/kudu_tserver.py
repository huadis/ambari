#!/usr/bin/env python3
from resource_management import *
import os
from kudu_service import kudu_service
from kudu import kudu


class KuduTserver(Script):
    def install(self, env):
        import params
        self.install_packages(env)
        self.configure(env)

    def configure(self, env):
        import params
        env.set_params(params)
        kudu(name = 'tserver')

    def start(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        self.configure(env)
        kudu_service('tserver', action='start', upgrade_type=upgrade_type)

    def stop(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        kudu_service('tserver', action='stop', upgrade_type=upgrade_type)

    def status(self, env):
        import status_params
        env.set_params(status_params)
        check_process_status(status_params.kudu_tserver_pid)


if __name__ == "__main__":
    KuduTserver().execute()
