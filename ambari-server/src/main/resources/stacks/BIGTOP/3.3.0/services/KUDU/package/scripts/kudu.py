#!/usr/bin/env python3
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import os
from ambari_commons.os_family_impl import OsFamilyFuncImpl, OsFamilyImpl
from resource_management import *


@OsFamilyFuncImpl(os_family=OsFamilyImpl.DEFAULT)
def kudu(name=None):
    import params

    Directory(params.kudu_log_dir,
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
              )

    Directory(params.kudu_pid_dir,
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
            )

    
    if name == 'master':
      Directory(params.config['configurations']['kudu-master-env']['fs_data_dirs'],
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
            )
      Directory(params.config['configurations']['kudu-master-env']['fs_metadata_dir'],
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
            )
      Directory(params.config['configurations']['kudu-master-env']['fs_wal_dir'],
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
            )
      File("/etc/kudu/conf/master.gflagfile",
             content=Template("kudu_master.j2"),
             mode=0o644
             )
      
      File(params.start_master_path,
            owner=params.kudu_user,
            group=params.user_group,
            mode=0o755,
            content=Template(format('{start_master_script}'))
          )
   
    if name == 'tserver':
      Directory(params.config['configurations']['kudu-tserver-env']['fs_data_dirs'],
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
            )
      Directory(params.config['configurations']['kudu-tserver-env']['fs_metadata_dir'],
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
            )
      Directory(params.config['configurations']['kudu-tserver-env']['fs_wal_dir'],
              owner=params.kudu_user,
              create_parents=True,
              group=params.user_group,
              mode=0o775
            )
      File("/etc/kudu/conf/tserver.gflagfile",
             content=Template("kudu_tserver.j2"),
             owner=params.kudu_user,
             group=params.user_group,
             mode=0o644
             )
      File(params.start_tserver_path,
            owner=params.kudu_user,
            group=params.user_group,
            mode=0o755,
            content=Template(format('{start_tserver_script}'))
          )

 