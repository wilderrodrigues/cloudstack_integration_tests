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
""" P1 tests for Account
"""
#Import Local Modules
from marvin.cloudstackTestCase import cloudstackTestCase
#from marvin.cloudstackAPI import *
from marvin.lib.utils import (random_gen,
                              cleanup_resources)
from marvin.lib.base import (Domain,
                             Account,
                             ServiceOffering,
                             VirtualMachine,
                             Network,
                             User,
                             NATRule,
                             Template,
                             PublicIPAddress)
from marvin.lib.common import (get_domain,
                               get_zone,
                               get_template,
                               list_accounts,
                               list_virtual_machines,
                               list_service_offering,
                               list_templates,
                               list_users,
                               get_builtin_template_info,
                               wait_for_cleanup)
from nose.plugins.attrib import attr
from marvin.cloudstackException import CloudstackAPIException
import time

class Services:
    """Test Account Services
    """

    def __init__(self):
        self.services = {
                        "domain": {
                                   "name": "Domain",
                                   },
                        "account": {
                                    "email": "test@test.com",
                                    "firstname": "Test",
                                    "lastname": "User",
                                    "username": "test",
                                    # Random characters are appended for unique
                                    # username
                                    "password": "fr3sca",
                         },
                         "user": {
                                    "email": "user@test.com",
                                    "firstname": "User",
                                    "lastname": "User",
                                    "username": "User",
                                    # Random characters are appended for unique
                                    # username
                                    "password": "fr3sca",
                         },
                         "service_offering": {
                                    "name": "Micro Instance",
                                    "displaytext": "Micro Instance",
                                    "cpunumber": 1,
                                    "cpuspeed": 100,
                                    # in MHz
                                    "memory": 96,
                                    'storagetype': 'local'
                                    # In MBs
                        },
                         "virtual_machine": {
                                    "displayname": "Test VM",
                                    "username": "root",
                                    "password": "password",
                                    "ssh_port": 22,
                                    "hypervisor": 'XenServer',
                                    # Hypervisor type should be same as
                                    # hypervisor type of cluster
                                    "privateport": 22,
                                    "publicport": 22,
                                    "protocol": 'TCP',
                         },
                         "template": {
                                "displaytext": "Public Template",
                                "name": "Public template",
                                "ostype": 'CentOS 5.6 (64-bit)',
                                "hypervisor": 'XenServer',
                                "format": 'VHD',
                                "url": "http://178.237.34.126:8099/template/tiny_linux.vhd",
                                "passwordenabled": False
                        },
                        "natrule": {
                                    "publicport": 22,
                                    "privateport": 22,
                                    "protocol": 'TCP',
                        },
                        "service_offering_id": "86d6c534-2f57-11e4-977d-020043e40006",
                        "template_id": "803881d6-2f57-11e4-977d-020043e40006",
                        "ostype": 'CentOS 5.6 (64-bit)',
                        # Cent OS 5.3 (64 bit)
                        "sleep": 60,
                        "timeout": 10,
                    }


class TestAccounts(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        cls.testClient = super(TestAccounts, cls).getClsTestClient()
        cls.api_client = cls.testClient.getApiClient()

        cls.services = Services().services
        cls.zone = get_zone(cls.api_client, cls.testClient.getZoneForTests())
        cls.services['mode'] = cls.zone.networktype
        cls.template = get_template(
                                    cls.api_client,
                                    cls.zone.id,
                                    cls.services["ostype"]
                                    )
        cls.services["virtual_machine"]["zoneid"] = cls.zone.id
        cls.services["virtual_machine"]["template"] = cls.template.id

        cls.service_offering = ServiceOffering.create(
                                                      cls.api_client,
                                                      cls.services["service_offering"]
                                                      )
        cls._cleanup = [cls.service_offering]
        #cls.service_offering = ServiceOffering.create(cls.api_client, cls.services["service_offering"])
        #cls._cleanup = [cls.service_offering]
        #cls._cleanup = []
        return

    @classmethod
    def tearDownClass(cls):
        try:
            #Cleanup resources used
            cleanup_resources(cls.api_client, cls._cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    def setUp(self):
        self.apiclient = self.testClient.getApiClient()
        self.dbclient = self.testClient.getDbConnection()
        self.cleanup = []
        return

    def tearDown(self):
        try:
            #Clean up, terminate the created accounts, domains etc
            cleanup_resources(self.apiclient, self.cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    @attr(tags=["advanced", "basic", "eip", "advancedns", "sg", "selfservice"])
    def test_01_create_account(self):
        """Test Create Account and user for that account
        """

        # Validate the following
        # 1. Create an Account. Verify the account is created.
        # 2. Create User associated with that account. Verify the created user

        # Create an account
        account = Account.create(
                            self.apiclient,
                            self.services["account"]
                            )
        self.debug("Created account: %s" % account.name)
        self._cleanup.append(account)
        list_accounts_response = list_accounts(
                                               self.apiclient,
                                               id=account.id
                                               )
        self.assertEqual(
                         isinstance(list_accounts_response, list),
                         True,
                         "Check list accounts for valid data"
                         )
        self.assertNotEqual(
                            len(list_accounts_response),
                            0,
                            "Check List Account response"
                            )

        account_response = list_accounts_response[0]
        self.assertEqual(
                            account.accounttype,
                            account_response.accounttype,
                            "Check Account Type of Created account"
                            )
        self.assertEqual(
                            account.name,
                            account_response.name,
                            "Check Account Name of Created account"
                            )
        # Create an User associated with account
        user = User.create(
                            self.apiclient,
                            self.services["user"],
                            account=account.name,
                            domainid=account.domainid
                            )
        self.debug("Created user: %s" % user.id)
        list_users_response = list_users(
                                         self.apiclient,
                                         id=user.id
                                      )
        self.assertEqual(
                         isinstance(list_users_response, list),
                         True,
                         "Check list users for valid data"
                         )

        self.assertNotEqual(
                            len(list_users_response),
                            0,
                            "Check List User response"
                            )

        user_response = list_users_response[0]
        self.assertEqual(
                            user.username,
                            user_response.username,
                            "Check username of Created user"
                            )
        self.assertEqual(
                            user.state,
                            user_response.state,
                            "Check state of created user"
                            )
        return

class TestAddVmToSubDomain(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        cls.testClient = super(TestAddVmToSubDomain, cls).getClsTestClient()
        cls.api_client = cls.testClient.getApiClient()

        cls.services = Services().services
        cls.domain = get_domain(cls.api_client)
        cls.zone = get_zone(cls.api_client, cls.testClient.getZoneForTests())
        cls.services['mode'] = cls.zone.networktype
        cls.sub_domain = Domain.create(
                                   cls.api_client,
                                   cls.services["domain"],
                                   parentdomainid=cls.domain.id
                                   )

        # Create account for doamin_1
        cls.account_1 = Account.create(
                            cls.api_client,
                            cls.services["account"],
                            admin=True,
                            domainid=cls.domain.id
                            )

        # Create an account for domain_2
        cls.account_2 = Account.create(
                            cls.api_client,
                            cls.services["account"],
                            admin=True,
                            domainid=cls.sub_domain.id
                            )

        cls.service_offering = ServiceOffering.create(
                                                      cls.api_client,
                                                      cls.services["service_offering"],
                                                      domainid=cls.domain.id
                                                      )
            
        cls._cleanup = [
                        cls.account_2,
                        cls.account_1,
                        cls.sub_domain,
                        cls.service_offering
                        ]
        cls.template = get_template(
                            cls.api_client,
                            cls.zone.id,
                            cls.services["ostype"]
                            )
        cls.services["virtual_machine"]["zoneid"] = cls.zone.id
        cls.vm_1 = VirtualMachine.create(
                                    cls.api_client,
                                    cls.services["virtual_machine"],
                                    templateid=cls.template.id,
                                    accountid=cls.account_1.name,
                                    domainid=cls.account_1.domainid,
                                    serviceofferingid=cls.service_offering.id
                                    )


        print "offering ID", cls.service_offering.id, "template ID", cls.template.id

        cls.vm_2 = VirtualMachine.create(
                                    cls.api_client,
                                    cls.services["virtual_machine"],
                                    templateid=cls.template.id,
                                    accountid=cls.account_2.name,
                                    domainid=cls.account_2.domainid,
                                    serviceofferingid=cls.service_offering.id
                                    )
        return

    @classmethod
    def tearDownClass(cls):
        try:
            #Clean up, terminate the created resources
            cleanup_resources(cls.api_client, cls._cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    def setUp(self):
        self.apiclient = self.testClient.getApiClient()
        self.dbclient = self.testClient.getDbConnection()
        self.cleanup = []
        return

    def tearDown(self):
        try:
            #Clean up, terminate the created resources
            cleanup_resources(self.apiclient, self.cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    @attr(tags=["advanced", "basic", "eip", "advancedns", "sg", "selfservice"])
    def test_01_add_vm_to_subdomain(self):
        """ Test Sub domain allowed to launch VM  when a Domain level zone is created"""

        # Validate the following
        # 1. Verify VM created by Account_1 is in Running state
        # 2. Verify VM created by Account_2 is in Running state

        vm_response = list_virtual_machines(
                                    self.apiclient,
                                    id=self.vm_1.id
                                )
        self.assertEqual(
                            isinstance(vm_response, list),
                            True,
                            "Check List VM for a valid response"
                        )
        self.assertNotEqual(
                            len(vm_response),
                            0,
                            "Check List Template response"
                            )

        for vm in vm_response:
            self.debug("VM ID: %s and state: %s" % (vm.id, vm.state))
            self.assertEqual(
                             vm.state,
                             'Running',
                             "Check State of Virtual machine"
                             )

        vm_response = list_virtual_machines(
                                    self.apiclient,
                                    id=self.vm_2.id
                                )
        self.assertNotEqual(
                            len(vm_response),
                            0,
                            "Check List Template response"
                            )

        for vm in vm_response:
            self.debug("VM ID: %s and state: %s" % (vm.id, vm.state))
            self.assertEqual(
                             vm.state,
                             'Running',
                             "Check State of Virtual machine"
                             )
        return


class TestUserDetails(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        cls.testClient = super(TestUserDetails, cls).getClsTestClient()
        cls.api_client = cls.testClient.getApiClient()

        cls.services = Services().services
        cls.domain = get_domain(cls.api_client)
        cls.zone = get_zone(cls.api_client, cls.testClient.getZoneForTests())
        cls.services['mode'] = cls.zone.networktype
        cls._cleanup = []
        return

    @classmethod
    def tearDownClass(cls):
        try:
            #Cleanup resources used
            cleanup_resources(cls.api_client, cls._cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    def setUp(self):
        self.apiclient = self.testClient.getApiClient()
        self.dbclient = self.testClient.getDbConnection()
        self.cleanup = []
        return

    def tearDown(self):
        try:
            #Clean up, terminate the created network offerings
            cleanup_resources(self.apiclient, self.cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    @attr(tags=[
                "role",
                "accounts",
                "simulator",
                "advanced",
                "advancedns",
                "basic",
                "eip",
                "sg"
                ])
    def test_updateUserDetails(self):
        """Test user update API
        """

        # Steps for test scenario
        # 1. create a user account
        # 2. update the user details (firstname, lastname, user) with
        #    updateUser API
        # 3. listUsers in the account
        # 4. delete the account
        # Validate the following
        # 1. listAccounts should show account created successfully
        # 2. updateUser API should return valid response
        # 3. user should be updated with new details

        self.debug("Creating an user account..")
        self.account = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     domainid=self.domain.id
                                     )
        self._cleanup.append(self.account)

        # Fetching the user details of account
        self.debug(
                   "Fetching user details for account: %s" %
                                            self.account.name)
        users = User.list(
                          self.apiclient,
                          account=self.account.name,
                          domainid=self.account.domainid
                          )
        self.assertEqual(
                         isinstance(users, list),
                         True,
                         "List users should return a valid list for account"
                         )
        user_1 = users[0]
        self.debug("Updating the details of user: %s" % user_1.name)
        firstname = random_gen()
        lastname = random_gen()

        self.debug("New firstname: %s, lastname: %s" % (firstname, lastname))
        User.update(
                    self.apiclient,
                    user_1.id,
                    firstname=firstname,
                    lastname=lastname
                    )

        # Fetching the user details of account
        self.debug(
                   "Fetching user details for user: %s" % user_1.name)
        users = User.list(
                          self.apiclient,
                          id=user_1.id,
                          listall=True
                          )

        self.assertEqual(
                         isinstance(users, list),
                         True,
                         "List users should return a valid list for account"
                         )
        user_1 = users[0]
        self.assertEqual(
                         user_1.firstname,
                         firstname,
                         "User's first name should be updated with new one"
                         )
        self.assertEqual(
                         user_1.lastname,
                         lastname,
                         "User's last name should be updated with new one"
                         )
        return

    @attr(tags=[
                "role",
                "accounts",
                "simulator",
                "advanced",
                "advancedns",
                "basic",
                "eip",
                "sg"
                ])
    def test_updateAdminDetails(self):
        """Test update admin details
        """

        # Steps for test scenario
        # 1. create a admin account
        # 2. update the user details (firstname, lastname, user) with
        #    updateUser API
        # 3. listUsers in the account
        # 4. delete the account
        # Validate the following
        # 1. listAccounts should show account created successfully
        # 2. updateUser API should return valid response
        # 3. user should be updated with new details

        self.debug("Creating a ROOT admin account")
        self.account = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     admin=True,
                                     )
        self._cleanup.append(self.account)

        # Fetching the user details of account
        self.debug(
                   "Fetching user details for account: %s" %
                                            self.account.name)
        users = User.list(
                          self.apiclient,
                          account=self.account.name,
                          domainid=self.account.domainid
                          )
        self.assertEqual(
                         isinstance(users, list),
                         True,
                         "List users should return a valid list for account"
                         )
        user_1 = users[0]
        self.debug("Updating the details of user: %s" % user_1.name)
        firstname = random_gen()
        lastname = random_gen()

        self.debug("New firstname: %s, lastname: %s" % (firstname, lastname))
        User.update(
                    self.apiclient,
                    user_1.id,
                    firstname=firstname,
                    lastname=lastname
                    )

        # Fetching the user details of account
        self.debug(
                   "Fetching user details for user: %s" % user_1.name)
        users = User.list(
                          self.apiclient,
                          id=user_1.id,
                          listall=True
                          )

        self.assertEqual(
                         isinstance(users, list),
                         True,
                         "List users should return a valid list for account"
                         )
        user_1 = users[0]
        self.assertEqual(
                         user_1.firstname,
                         firstname,
                         "User's first name should be updated with new one"
                         )
        self.assertEqual(
                         user_1.lastname,
                         lastname,
                         "User's last name should be updated with new one"
                         )
        return

    @attr(tags=[
                "role",
                "accounts",
                "simulator",
                "advanced",
                "advancedns",
                "basic",
                "eip",
                "sg"
                ])
    def test_updateDomainAdminDetails(self):
        """Test update domain admin details
        """

        # Steps for test scenario
        # 2. update the user details (firstname, lastname, user) with
        #    updateUser API
        # 3. listUsers in the account
        # 4. delete the account
        # Validate the following
        # 1. listAccounts should show account created successfully
        # 2. updateUser API should return valid response
        # 3. user should be updated with new details

        self.debug("Creating a domain admin account")
        self.account = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     admin=True,
                                     domainid=self.domain.id
                                     )
        self._cleanup.append(self.account)

        # Fetching the user details of account
        self.debug(
                   "Fetching user details for account: %s" %
                                            self.account.name)
        users = User.list(
                          self.apiclient,
                          account=self.account.name,
                          domainid=self.account.domainid
                          )
        self.assertEqual(
                         isinstance(users, list),
                         True,
                         "List users should return a valid list for account"
                         )
        user_1 = users[0]
        self.debug("Updating the details of user: %s" % user_1.name)
        firstname = random_gen()
        lastname = random_gen()

        self.debug("New firstname: %s, lastname: %s" % (firstname, lastname))
        User.update(
                    self.apiclient,
                    user_1.id,
                    firstname=firstname,
                    lastname=lastname
                    )

        # Fetching the user details of account
        self.debug(
                   "Fetching user details for user: %s" % user_1.name)
        users = User.list(
                          self.apiclient,
                          id=user_1.id,
                          listall=True
                          )

        self.assertEqual(
                         isinstance(users, list),
                         True,
                         "List users should return a valid list for account"
                         )
        user_1 = users[0]
        self.assertEqual(
                         user_1.firstname,
                         firstname,
                         "User's first name should be updated with new one"
                         )
        self.assertEqual(
                         user_1.lastname,
                         lastname,
                         "User's last name should be updated with new one"
                         )
        return

class TestUserLogin(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        cls.testClient = super(TestUserLogin, cls).getClsTestClient()
        cls.api_client = cls.testClient.getApiClient()

        cls.services = Services().services
        cls.domain = get_domain(cls.api_client)
        cls.zone = get_zone(cls.api_client, cls.testClient.getZoneForTests())
        cls.services['mode'] = cls.zone.networktype
        cls._cleanup = []
        return

    @classmethod
    def tearDownClass(cls):
        try:
            #Cleanup resources used
            cleanup_resources(cls.api_client, cls._cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    def setUp(self):
        self.apiclient = self.testClient.getApiClient()
        self.dbclient = self.testClient.getDbConnection()
        self.cleanup = []
        return

    def tearDown(self):
        try:
            #Clean up, terminate the created network offerings
            cleanup_resources(self.apiclient, self.cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    @attr(tags=["login", "accounts", "simulator", "advanced",
                        "advancedns", "basic", "eip", "sg"])
    def test_LoginApiUuidResponse(self):
        """Test if Login API does not return UUID's
        """

        # Steps for test scenario
        # 1. create a user account
        # 2. login to the user account with given credentials (loginCmd)
        # 3. delete the user account
        # Validate the following
        # 1. listAccounts should return account created
        # 2. loginResponse should have UUID only is response. Assert by
        #    checking database id is not same as response id
        #    Login also succeeds with non NULL sessionId in response

        self.debug("Creating an user account..")
        self.account = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     domainid=self.domain.id
                                     )
        self._cleanup.append(self.account)

        self.debug("Logging into the cloudstack with login API")
        respose = User.login(
                             self.apiclient,
                             username=self.account.name,
                             password=self.services["account"]["password"]
                             )

        self.debug("Login API response: %s" % respose)

        self.assertNotEqual(
                            respose.sessionkey,
                            None,
                            "Login to the CloudStack should be successful" +
                            "response shall have non Null key"
                            )
        return

    @attr(tags=["login", "accounts", "simulator", "advanced",
                        "advancedns", "basic", "eip", "sg"])
    def test_LoginApiDomain(self):
        """Test login API with domain
        """

        # Steps for test scenario
        # 1. create a domain
        # 2. create user in the domain
        # 3. login to the user account above using UUID domain/user
        # 4. delete the user account
        # Validate the following
        # 1. listDomains returns created domain
        # 2. listAccounts returns created user
        # 3. loginResponse should have UUID only in responses
        #    Login also succeeds with non NULL sessionId in response

        self.debug("Creating a domain for login with API domain test")
        domain = Domain.create(
                                self.apiclient,
                                self.services["domain"],
                                parentdomainid=self.domain.id
                                )
        self.debug("Domain: %s is created succesfully." % domain.name)
        self.debug(
            "Checking if the created domain is listed in list domains API")
        domains = Domain.list(self.apiclient, id=domain.id, listall=True)

        self.assertEqual(
                         isinstance(domains, list),
                         True,
                         "List domains shall return a valid response"
                         )
        self.debug("Creating an user account in domain: %s" % domain.name)
        self.account = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     domainid=domain.id
                                     )
        self._cleanup.append(self.account)

        accounts = Account.list(
                                self.apiclient,
                                name=self.account.name,
                                domainid=self.account.domainid,
                                listall=True
                                )

        self.assertEqual(
                         isinstance(accounts, list),
                         True,
                         "List accounts should return a valid response"
                         )

        self.debug("Logging into the cloudstack with login API")
        respose = User.login(
                             self.apiclient,
                             username=self.account.name,
                             password=self.services["account"]["password"],
                             domainid=domain.id)
        self.debug("Login API response: %s" % respose)

        self.assertNotEqual(
                            respose.sessionkey,
                            None,
                            "Login to the CloudStack should be successful" +
                            "response shall have non Null key"
                            )
        return

class TestDomainForceRemove(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        cls.testClient = super(TestDomainForceRemove, cls).getClsTestClient()
        cls.api_client = cls.testClient.getApiClient()

        cls.services = Services().services
        cls.domain = get_domain(cls.api_client)
        cls.zone = get_zone(cls.api_client, cls.testClient.getZoneForTests())
        cls.services['mode'] = cls.zone.networktype

        cls.template = get_template(
                            cls.api_client,
                            cls.zone.id,
                            cls.services["ostype"]
                            )

        cls.services["virtual_machine"]["zoneid"] = cls.zone.id
        cls._cleanup = []
        return

    @classmethod
    def tearDownClass(cls):
        try:
            #Clean up, terminate the created resources
            cleanup_resources(cls.api_client, cls._cleanup)
        except Exception as e:

            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    def setUp(self):
        self.apiclient = self.testClient.getApiClient()
        self.dbclient = self.testClient.getDbConnection()
        self.cleanup = []
        return

    def tearDown(self):
        try:
            #Clean up, terminate the created resources
            cleanup_resources(self.apiclient, self.cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    @attr(tags=["domains", "advanced", "advancedns", "simulator", "selfservice"])
    def test_forceDeleteDomain(self):
        """ Test delete domain with force option"""

        # Steps for validations
        # 1. create a domain DOM
        # 2. create 2 users under this domain
        # 3. deploy 1 VM into each of these user accounts
        # 4. create PF / FW rules for port 22 on these VMs for their
        #    respective accounts
        # 5. delete the domain with force=true option
        # Validate the following
        # 1. listDomains should list the created domain
        # 2. listAccounts should list the created accounts
        # 3. listvirtualmachines should show the Running VMs
        # 4. PF and FW rules should be shown in listFirewallRules
        # 5. domain should delete successfully and above three list calls
        #    should show all the resources now deleted. listRouters should
        #    not return any routers in the deleted accounts/domains

        self.debug("Creating a domain for login with API domain test")
        domain = Domain.create(
                                self.apiclient,
                                self.services["domain"],
                                parentdomainid=self.domain.id
                                )
        self.debug("Domain is created succesfully.")
        self.debug(
            "Checking if the created domain is listed in list domains API")
        domains = Domain.list(self.apiclient, id=domain.id, listall=True)

        self.assertEqual(
                         isinstance(domains, list),
                         True,
                         "List domains shall return a valid response"
                         )
        self.debug("Creating 2 user accounts in domain: %s" % domain.name)
        self.account_1 = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     domainid=domain.id
                                     )

        self.account_2 = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     domainid=domain.id
                                     )

        try:
            self.debug("Creating a tiny service offering for VM deployment")
            self.service_offering = ServiceOffering.create(
                                    self.apiclient,
                                    self.services["service_offering"],
                                    domainid=self.domain.id
                                    )

            self.debug("Deploying virtual machine in account 1: %s" %
                                                self.account_1.name)
            vm_1 = VirtualMachine.create(
                                    self.apiclient,
                                    self.services["virtual_machine"],
                                    templateid=self.template.id,
                                    accountid=self.account_1.name,
                                    domainid=self.account_1.domainid,
                                    serviceofferingid=self.service_offering.id
                                    )

            self.debug("Deploying virtual machine in account 2: %s" %
                                                self.account_2.name)
            VirtualMachine.create(
                                    self.apiclient,
                                    self.services["virtual_machine"],
                                    templateid=self.template.id,
                                    accountid=self.account_2.name,
                                    domainid=self.account_2.domainid,
                                    serviceofferingid=self.service_offering.id
                                    )

            networks = Network.list(
                                self.apiclient,
                                account=self.account_1.name,
                                domainid=self.account_1.domainid,
                                listall=True
                                )
            self.assertEqual(
                         isinstance(networks, list),
                         True,
                         "List networks should return a valid response"
                         )
            network_1 = networks[0]
            self.debug("Default network in account 1: %s is %s" % (
                                                self.account_1.name,
                                                network_1.name))
            src_nat_list = PublicIPAddress.list(
                                    self.apiclient,
                                    associatednetworkid=network_1.id,
                                    account=self.account_1.name,
                                    domainid=self.account_1.domainid,
                                    listall=True,
                                    issourcenat=True,
                                    )
            self.assertEqual(
                         isinstance(src_nat_list, list),
                         True,
                         "List Public IP should return a valid source NAT"
                         )
            self.assertNotEqual(
                    len(src_nat_list),
                    0,
                    "Length of response from listPublicIp should not be 0"
                    )

            src_nat = src_nat_list[0]

            self.debug(
                      "Trying to create a port forwarding rule in source NAT: %s" %
                                                            src_nat.ipaddress)
            #Create NAT rule
            nat_rule = NATRule.create(
                                  self.apiclient,
                                  vm_1,
                                  self.services["natrule"],
                                  ipaddressid=src_nat.id
                           )
            self.debug("Created PF rule on source NAT: %s" % src_nat.ipaddress)

            nat_rules = NATRule.list(self.apiclient, id=nat_rule.id)

            self.assertEqual(
                         isinstance(nat_rules, list),
                         True,
                         "List NAT should return a valid port forwarding rules"
                         )

            self.assertNotEqual(
                    len(nat_rules),
                    0,
                    "Length of response from listLbRules should not be 0"
                    )
        except Exception as e:
            self._cleanup.append(self.account_1)
            self._cleanup.append(self.account_2)
            self.fail(e)

        self.debug("Deleting domain with force option")
        try:
            domain.delete(self.apiclient, cleanup=True)
        except Exception as e:
            self.debug("Waiting for account.cleanup.interval" +
                " to cleanup any remaining resouces")
            # Sleep 3*account.gc to ensure that all resources are deleted
            wait_for_cleanup(self.apiclient, ["account.cleanup.interval"]*3)
            with self.assertRaises(CloudstackAPIException):
                Domain.list(
                        self.apiclient,
                        id=domain.id,
                        listall=True
                        )

        self.debug("Checking if the resources in domain are deleted")
        with self.assertRaises(CloudstackAPIException):
            Account.list(
                        self.apiclient,
                        name=self.account_1.name,
                        domainid=self.account_1.domainid,
                        listall=True
                        )
        return

    @attr(tags=["domains", "advanced", "advancedns", "simulator", "selfservice"])
    def test_DeleteDomain(self):
        """ Test delete domain without force option"""

        # Steps for validations
        # 1. create a domain DOM
        # 2. create 2 users under this domain
        # 3. deploy 1 VM into each of these user accounts
        # 4. create PF / FW rules for port 22 on these VMs for their
        #    respective accounts
        # 5. delete the domain with force=false option
        # Validate the following
        # 1. listDomains should list the created domain
        # 2. listAccounts should list the created accounts
        # 3. listvirtualmachines should show the Running VMs
        # 4. PF and FW rules should be shown in listFirewallRules
        # 5. domain deletion should fail saying there are resources under use

        self.debug("Creating a domain for login with API domain test")
        domain = Domain.create(
                                self.apiclient,
                                self.services["domain"],
                                parentdomainid=self.domain.id
                                )
        self.debug("Domain: %s is created successfully." % domain.name)
        self.debug(
            "Checking if the created domain is listed in list domains API")
        domains = Domain.list(self.apiclient, id=domain.id, listall=True)

        self.assertEqual(
                         isinstance(domains, list),
                         True,
                         "List domains shall return a valid response"
                         )
        self.debug("Creating 2 user accounts in domain: %s" % domain.name)
        self.account_1 = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     domainid=domain.id
                                     )
        self._cleanup.append(self.account_1)

        self.account_2 = Account.create(
                                     self.apiclient,
                                     self.services["account"],
                                     domainid=domain.id
                                     )
        self._cleanup.append(self.account_2)

        self.debug("Creating a tiny service offering for VM deployment")
        self.service_offering = ServiceOffering.create(
                                    self.apiclient,
                                    self.services["service_offering"],
                                    domainid=self.domain.id
                                    )
        self._cleanup.append(self.service_offering)

        self.debug("Deploying virtual machine in account 1: %s" %
                                                self.account_1.name)
        vm_1 = VirtualMachine.create(
                                    self.apiclient,
                                    self.services["virtual_machine"],
                                    templateid=self.template.id,
                                    accountid=self.account_1.name,
                                    domainid=self.account_1.domainid,
                                    serviceofferingid=self.service_offering.id
                                    )

        self.debug("Deploying virtual machine in account 2: %s" %
                                                self.account_2.name)
        VirtualMachine.create(
                                    self.apiclient,
                                    self.services["virtual_machine"],
                                    templateid=self.template.id,
                                    accountid=self.account_2.name,
                                    domainid=self.account_2.domainid,
                                    serviceofferingid=self.service_offering.id
                                    )

        networks = Network.list(
                                self.apiclient,
                                account=self.account_1.name,
                                domainid=self.account_1.domainid,
                                listall=True
                                )
        self.assertEqual(
                         isinstance(networks, list),
                         True,
                         "List networks should return a valid response"
                         )
        network_1 = networks[0]
        self.debug("Default network in account 1: %s is %s" % (
                                                self.account_1.name,
                                                network_1.name))
        src_nat_list = PublicIPAddress.list(
                                    self.apiclient,
                                    associatednetworkid=network_1.id,
                                    account=self.account_1.name,
                                    domainid=self.account_1.domainid,
                                    listall=True,
                                    issourcenat=True,
                                    )
        self.assertEqual(
                         isinstance(src_nat_list, list),
                         True,
                         "List Public IP should return a valid source NAT"
                         )
        self.assertNotEqual(
                    len(src_nat_list),
                    0,
                    "Length of response from listPublicIp should not be 0"
                    )

        src_nat = src_nat_list[0]

        self.debug(
            "Trying to create a port forwarding rule in source NAT: %s" %
                                                            src_nat.ipaddress)
        #Create NAT rule
        nat_rule = NATRule.create(
                                  self.apiclient,
                                  vm_1,
                                  self.services["natrule"],
                                  ipaddressid=src_nat.id
                           )
        self.debug("Created PF rule on source NAT: %s" % src_nat.ipaddress)

        nat_rules = NATRule.list(self.apiclient, id=nat_rule.id)

        self.assertEqual(
                         isinstance(nat_rules, list),
                         True,
                         "List NAT should return a valid port forwarding rules"
                         )

        self.assertNotEqual(
                    len(nat_rules),
                    0,
                    "Length of response from listLbRules should not be 0"
                    )

        self.debug("Deleting domain without force option")
        with self.assertRaises(Exception):
            domain.delete(self.apiclient, cleanup=False)
        return
