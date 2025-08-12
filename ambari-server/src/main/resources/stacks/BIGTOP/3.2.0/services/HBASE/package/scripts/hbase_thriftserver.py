#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements. See the NOTICE file
distributed with this work for additional information
regarding copyright ownership. The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import sys
from resource_management import *
from resource_management.libraries.functions.security_commons import build_expectations, \
    cached_kinit_executor, get_params_from_filesystem, validate_security_config_properties, \
    FILE_TYPE_XML
from hbase import hbase
from hbase_service import hbase_service
import upgrade
from setup_ranger_hbase import setup_ranger_hbase
from ambari_commons import OSCheck, OSConst
from ambari_commons.os_family_impl import OsFamilyImpl
from resource_management.libraries.functions.check_process_status import check_process_status

class HbaseThrift(Script):

    def install(self, env):
        import params
        env.set_params(params)
        self.install_packages(env)
        pass

    def configure(self, env):
        import params
        env.set_params(params)
        pass

    def start(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        self.configure(env)
        hbase_service('thrift', action = 'start')

    def stop(self, env, upgrade_type=None):
        import params
        env.set_params(params)
        hbase_service('thrift', action = 'stop')

    def status(self, env):
        import status_params
        env.set_params(status_params)
        hbase_thrift_pid_file = format("{pid_dir}/hbase-{hbase_user}-thrift.pid")
        check_process_status(hbase_thrift_pid_file)

    def get_component_name(self):
        return "hbase-thriftserver"

if __name__ == "__main__":
    HbaseThrift().execute()
