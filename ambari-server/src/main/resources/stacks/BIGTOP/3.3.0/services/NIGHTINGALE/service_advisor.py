#!/usr/bin/env ambari-python-wrap
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

import imp
import os
import socket
import traceback

from resource_management.core.logger import Logger

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STACKS_DIR = os.path.join(SCRIPT_DIR, "../../../../../stacks/")
PARENT_FILE = os.path.join(STACKS_DIR, "service_advisor.py")

try:
    if "BASE_SERVICE_ADVISOR" in os.environ:
        PARENT_FILE = os.environ["BASE_SERVICE_ADVISOR"]
    with open(PARENT_FILE, "rb") as fp:
        service_advisor = imp.load_module(
            "service_advisor", fp, PARENT_FILE, (".py", "rb", imp.PY_SOURCE)
        )
except Exception as e:
    traceback.print_exc()
    print("Failed to load parent")


class NightingaleServiceAdvisor(service_advisor.ServiceAdvisor):
    def __init__(self, *args, **kwargs):
        self.as_super = super(NightingaleServiceAdvisor, self)
        self.as_super.__init__(*args, **kwargs)

        self.initialize_logger("NightingaleServiceAdvisor")

        # Always call these methods
        self.modifyMastersWithMultipleInstances()
        self.modifyCardinalitiesDict()
        self.modifyHeapSizeProperties()
        self.modifyNotValuableComponents()
        self.modifyComponentsNotPreferableOnServer()
        self.modifyComponentLayoutSchemes()

    def modifyMastersWithMultipleInstances(self):
        """
        Modify the set of masters with multiple instances.
        Must be overriden in child class.
        """
        # Nothing to do
        pass

    def modifyCardinalitiesDict(self):
        """
        Modify the dictionary of cardinalities.
        Must be overriden in child class.
        """
        # Nothing to do
        pass

    def modifyHeapSizeProperties(self):
        """
        Modify the dictionary of heap size properties.
        Must be overriden in child class.
        """
        pass

    def modifyNotValuableComponents(self):
        """
        Modify the set of components whose host assignment is based on other services.
        Must be overriden in child class.
        """
        # Nothing to do
        pass

    def modifyComponentsNotPreferableOnServer(self):
        """
        Modify the set of components that are not preferable on the server.
        Must be overriden in child class.
        """
        # Nothing to do
        pass

    def modifyComponentLayoutSchemes(self):
        """
        Modify layout scheme dictionaries for components.
        The scheme dictionary basically maps the number of hosts to
        host index where component should exist.
        Must be overriden in child class.
        """
        pass

    def getServiceComponentLayoutValidations(self, services, hosts):
        """
        Get a list of errors.
        Must be overriden in child class.
        """

        return self.getServiceComponentCardinalityValidations(
            services, hosts, "SUPERSET"
        )

    def getServiceConfigurationRecommendations(
        self, configurations, clusterData, services, hosts
    ):
        recommender = NightingaleRecommender()
        recommender.recommendNightingaleConfigurationsFromHDP30(
            configurations, clusterData, services, hosts
        )

    def getServiceConfigurationsValidationItems(
        self, configurations, recommendedDefaults, services, hosts
    ):
        """
        Entry point.
        Validate configurations for the service. Return a list of errors.
        The code for this function should be the same for each Service Advisor.
        """
        return []


class NightingaleRecommender(service_advisor.ServiceAdvisor):
    """
    Nightingale Recommender suggests properties when adding the service for the first time or modifying configs via the UI.
    """

    def __init__(self, *args, **kwargs):
        self.as_super = super(NightingaleRecommender, self)
        self.as_super.__init__(*args, **kwargs)

    def recommendNightingaleConfigurationsFromHDP30(
        self, configurations, clusterData, services, hosts
    ):
        pass
