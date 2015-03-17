# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
""" BVT tests for Service offerings"""

#Import Local Modules
from marvin.codes import FAILED
from marvin.cloudstackTestCase import cloudstackTestCase
from marvin.cloudstackAPI import changeServiceForVirtualMachine,updateServiceOffering
from marvin.lib.utils import (isAlmostEqual,
                                          cleanup_resources,
                                          random_gen)
from marvin.lib.base import (ServiceOffering,
                                         Account,
                                         VirtualMachine)
from marvin.lib.common import (list_service_offering,
                                           list_virtual_machines,
                                           get_domain,
                                           get_zone,
                                           get_template)
from nose.plugins.attrib import attr


_multiprocess_shared_ = True


class TestCreateServiceOffering(cloudstackTestCase):
    def setUp(self):
        self.apiclient = self.testClient.getApiClient()
        self.dbclient = self.testClient.getDbConnection()
        self.cleanup = []
        self.services = self.testClient.getParsedTestDataConfig()

    def tearDown(self):
        try:
            #Clean up, terminate the created templates
            cleanup_resources(self.apiclient, self.cleanup)

        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)

        return

    @attr(tags=["advanced", "advancedns", "smoke", "basic", "eip", "sg"])
    def test_01_create_service_offering(self):
        """Test to create service offering"""

        # Validate the following:
        # 1. createServiceOfferings should return a valid information for newly created offering
        # 2. The Cloud Database contains the valid information

        service_offering = ServiceOffering.create(
            self.apiclient,
            self.services["service_offerings"]
        )
        self.cleanup.append(service_offering)

        self.debug("Created service offering with ID: %s" % service_offering.id)

        list_service_response = list_service_offering(
            self.apiclient,
            id=service_offering.id
        )
        self.assertEqual(
            isinstance(list_service_response, list),
            True,
            "Check list response returns a valid list"
        )

        self.assertNotEqual(
            len(list_service_response),
            0,
            "Check Service offering is created"
        )

        self.assertEqual(
            list_service_response[0].cpunumber,
            self.services["service_offerings"]["cpunumber"],
            "Check server id in createServiceOffering"
        )
        self.assertEqual(
            list_service_response[0].cpuspeed,
            self.services["service_offerings"]["cpuspeed"],
            "Check cpuspeed in createServiceOffering"
        )
        self.assertEqual(
            list_service_response[0].displaytext,
            self.services["service_offerings"]["displaytext"],
            "Check server displaytext in createServiceOfferings"
        )
        self.assertEqual(
            list_service_response[0].memory,
            self.services["service_offerings"]["memory"],
            "Check memory in createServiceOffering"
        )
        self.assertEqual(
            list_service_response[0].name,
            self.services["service_offerings"]["name"],
            "Check name in createServiceOffering"
        )
        return


class TestServiceOfferings(cloudstackTestCase):
    def setUp(self):
        self.apiclient = self.testClient.getApiClient()
        self.dbclient = self.testClient.getDbConnection()
        self.cleanup = []

    def tearDown(self):
        try:
            #Clean up, terminate the created templates
            cleanup_resources(self.apiclient, self.cleanup)

        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)

        return

    @classmethod
    def setUpClass(cls):
        testClient = super(TestServiceOfferings, cls).getClsTestClient()
        cls.apiclient = testClient.getApiClient()
        cls.services = testClient.getParsedTestDataConfig()

        #Adding storage type as 'local' otherwise it won't work because default is 'shared'.
        cls.services["service_offerings"]["small"]['storagetype'] = 'local'
        cls.services["service_offerings"]["medium"]['storagetype'] = 'local'
        cls.services['ostype'] = 'CentOS 5.6 (64-bit)'

        domain = get_domain(cls.apiclient)
        cls.zone = get_zone(cls.apiclient, testClient.getZoneForTests())
        cls.services['mode'] = cls.zone.networktype

        cls.service_offering_1 = ServiceOffering.create(
            cls.apiclient,
            cls.services["service_offerings"]
        )
        cls.service_offering_2 = ServiceOffering.create(
            cls.apiclient,
            cls.services["service_offerings"]
        )
        template = get_template(
                            cls.apiclient,
                            cls.zone.id,
                            cls.services["ostype"]
                            )
        if template == FAILED:
            assert False, "get_template() failed to return template with description %s" % cls.services["ostype"]

        # Set Zones and disk offerings
        cls.services["small"]["zoneid"] = cls.zone.id
        cls.services["small"]["template"] = template.id

        cls.services["medium"]["zoneid"] = cls.zone.id
        cls.services["medium"]["template"] = template.id

        # Create VMs, NAT Rules etc
        cls.account = Account.create(
                            cls.apiclient,
                            cls.services["account"],
                            domainid=domain.id
                            )

        cls.small_offering = ServiceOffering.create(
                                    cls.apiclient,
                                    cls.services["service_offerings"]["small"]
                                    )

        cls.medium_offering = ServiceOffering.create(
                                    cls.apiclient,
                                    cls.services["service_offerings"]["medium"]
                                    )
        cls.medium_virtual_machine = VirtualMachine.create(
                                       cls.apiclient,
                                       cls.services["medium"],
                                       accountid=cls.account.name,
                                       domainid=cls.account.domainid,
                                       serviceofferingid=cls.medium_offering.id,
                                       mode=cls.services["mode"]
                                    )
        cls._cleanup = [
                        cls.small_offering,
                        cls.medium_offering,
                        cls.account
                        ]
        return

    @classmethod
    def tearDownClass(cls):
        try:
            cls.apiclient = super(TestServiceOfferings, cls).getClsTestClient().getApiClient()
            #Clean up, terminate the created templates
            cleanup_resources(cls.apiclient, cls._cleanup)

        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    @attr(tags=["advanced", "advancedns", "smoke", "basic", "eip", "sg"])
    def test_02_edit_service_offering(self):
        """Test to update existing service offering"""

        # Validate the following:
        # 1. updateServiceOffering should return
        #    a valid information for newly created offering

        #Generate new name & displaytext from random data
        random_displaytext = random_gen()
        random_name = random_gen()

        self.debug("Updating service offering with ID: %s" %
                   self.service_offering_1.id)

        cmd = updateServiceOffering.updateServiceOfferingCmd()
        #Add parameters for API call
        cmd.id = self.service_offering_1.id
        cmd.displaytext = random_displaytext
        cmd.name = random_name
        self.apiclient.updateServiceOffering(cmd)

        list_service_response = list_service_offering(
            self.apiclient,
            id=self.service_offering_1.id
        )
        self.assertEqual(
            isinstance(list_service_response, list),
            True,
            "Check list response returns a valid list"
        )

        self.assertNotEqual(
            len(list_service_response),
            0,
            "Check Service offering is updated"
        )

        self.assertEqual(
            list_service_response[0].displaytext,
            random_displaytext,
            "Check server displaytext in updateServiceOffering"
        )
        self.assertEqual(
            list_service_response[0].name,
            random_name,
            "Check server name in updateServiceOffering"
        )

        return

    @attr(tags=["advanced", "advancedns", "smoke", "basic", "eip", "sg"])
    def test_03_delete_service_offering(self):
        """Test to delete service offering"""

        # Validate the following:
        # 1. deleteServiceOffering should return
        #    a valid information for newly created offering

        self.debug("Deleting service offering with ID: %s" %
                   self.service_offering_2.id)

        self.service_offering_2.delete(self.apiclient)

        list_service_response = list_service_offering(
            self.apiclient,
            id=self.service_offering_2.id
        )

        self.assertEqual(
            list_service_response,
            None,
            "Check if service offering exists in listDiskOfferings"
        )

        return