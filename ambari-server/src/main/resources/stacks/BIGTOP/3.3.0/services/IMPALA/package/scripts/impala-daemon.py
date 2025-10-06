from resource_management import *
from impala_service import impala_service
from impala import impala


class ImpalaDaemon(Script):
    def install(self, env):
        import params

        self.install_packages(env)
        self.configure(env)

    def configure(self, env):
        import params

        env.set_params(params)
        impala(name="impalad")

    def start(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        self.configure(env)
        impala_service("impalad", action="start", upgrade_type=upgrade_type)

    def stop(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        impala_service("impalad", action="stop", upgrade_type=upgrade_type)

    def status(self, env):
        import status_params

        env.set_params(status_params)
        check_process_status(status_params.impala_impalad_pid)


if __name__ == "__main__":
    ImpalaDaemon().execute()
