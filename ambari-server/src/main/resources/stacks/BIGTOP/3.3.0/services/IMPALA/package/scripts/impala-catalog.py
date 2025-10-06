from resource_management import *
from impala_service import impala_service
from impala import impala


class ImpalaCatalog(Script):
    def install(self, env):
        import params

        self.install_packages(env)
        self.configure(env)

    def configure(self, env):
        import params

        env.set_params(params)
        impala(name="catalogd")

    def start(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        self.configure(env)
        impala_service("catalogd", action="start", upgrade_type=upgrade_type)

    def stop(self, env, upgrade_type=None):
        import params

        env.set_params(params)
        impala_service("catalogd", action="stop", upgrade_type=upgrade_type)

    def status(self, env):
        import status_params

        env.set_params(status_params)
        check_process_status(status_params.impala_catalogd_pid)


if __name__ == "__main__":
    ImpalaCatalog().execute()
