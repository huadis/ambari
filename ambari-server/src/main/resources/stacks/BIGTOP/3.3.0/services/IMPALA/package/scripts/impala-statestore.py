from resource_management import *
from impala_service import impala_service
from impala import impala


class ImpalaStateStore(Script):
    def install(self, env):
        import params

        self.install_packages(env)
        self.configure(env)

    def configure(self, env):
        import params

        env.set_params(params)
        impala(name="statestored")

    def start(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        self.configure(env)
        impala_service("statestored", action="start", upgrade_type=upgrade_type)

    def stop(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        impala_service("statestored", action="stop", upgrade_type=upgrade_type)

    def status(self, env):
        import status_params

        env.set_params(status_params)
        check_process_status(status_params.impala_statestored_pid)


if __name__ == "__main__":
    ImpalaStateStore().execute()
