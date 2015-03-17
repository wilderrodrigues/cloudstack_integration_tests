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

""" Component tests for VPC - Router Operations 
"""
#Import Local Modules
import marvin
from nose.plugins.attrib import attr
from marvin.cloudstackTestCase import *
from marvin.cloudstackAPI import *
from marvin.lib.utils import *
from marvin.lib.base import *
from marvin.lib.common import *
import datetime


class Services:
    """Test VPC Router services
    """

    def __init__(self):
        self.services = {
                         "account": {
                                    "email": "test@test.com",
                                    "firstname": "Test",
                                    "lastname": "User",
                                    "username": "test",
                                    # Random characters are appended for unique
                                    # username
                                    "password": "password",
                                    },
                         "service_offering": {
                                    "name": "Tiny Instance",
                                    "displaytext": "Tiny Instance",
                                    "cpunumber": 1,
                                    "cpuspeed": 100,
                                    "memory": 128,
                                    'storagetype': 'local'
                                    },
                         "service_offering_new": {
                                    "name": "Small Instance",
                                    "displaytext": "Small Instance",
                                    "cpunumber": 1,
                                    "cpuspeed": 100,
                                    "memory": 256,
                                    "issystem": 'true',
                                    'storagetype': 'local'
                                    },

                         "network_offering": {
                                    "name": 'VPC Network offering',
                                    "displaytext": 'VPC Network off',
                                    "guestiptype": 'Isolated',
                                    "supportedservices": 'Vpn,Dhcp,Dns,SourceNat,PortForwarding,Lb,UserData,StaticNat,NetworkACL',
                                    "traffictype": 'GUEST',
                                    "availability": 'Optional',
                                    "useVpc": 'on',
                                    "serviceProviderList": {
                                            "Vpn": 'VpcVirtualRouter',
                                            "Dhcp": 'VpcVirtualRouter',
                                            "Dns": 'VpcVirtualRouter',
                                            "SourceNat": 'VpcVirtualRouter',
                                            "PortForwarding": 'VpcVirtualRouter',
                                            "Lb": 'VpcVirtualRouter',
                                            "UserData": 'VpcVirtualRouter',
                                            "StaticNat": 'VpcVirtualRouter',
                                            "NetworkACL": 'VpcVirtualRouter'
                                        },
                                },
                         "network_offering_no_lb": {
                                    "name": 'VPC Network offering',
                                    "displaytext": 'VPC Network off',
                                    "guestiptype": 'Isolated',
                                    "supportedservices": 'Vpn,Dhcp,Dns,SourceNat,PortForwarding,UserData,StaticNat,NetworkACL',
                                    "traffictype": 'GUEST',
                                    "availability": 'Optional',
                                    "useVpc": 'on',
                                    "serviceProviderList": {
                                            "Vpn": 'VpcVirtualRouter',
                                            "Dhcp": 'VpcVirtualRouter',
                                            "Dns": 'VpcVirtualRouter',
                                            "SourceNat": 'VpcVirtualRouter',
                                            "PortForwarding": 'VpcVirtualRouter',
                                            "UserData": 'VpcVirtualRouter',
                                            "StaticNat": 'VpcVirtualRouter',
                                            "NetworkACL": 'VpcVirtualRouter'
                                        },
                                },
                         "redundant_vpc_offering": {
                                    "name": 'Redundant VPC off',
                                    "displaytext": 'Redundant VPC off',
                                    "supportedservices": 'Dhcp,Dns,SourceNat,PortForwarding,Vpn,Lb,UserData,StaticNat',
                                    "serviceProviderList": {
                                            "Vpn": 'VpcVirtualRouter',
                                            "Dhcp": 'VpcVirtualRouter',
                                            "Dns": 'VpcVirtualRouter',
                                            "SourceNat": 'VpcVirtualRouter',
                                            "PortForwarding": 'VpcVirtualRouter',
                                            "Lb": 'VpcVirtualRouter',
                                            "UserData": 'VpcVirtualRouter',
                                            "StaticNat": 'VpcVirtualRouter',
                                            "NetworkACL": 'VpcVirtualRouter'
                                    },
                                    "serviceCapabilityList": {
                                        "SourceNat": {
                                            "RedundantRouter": 'true'
                                        }
                                    },
                                },
                         "vpc": {
                                 "name": "TestVPC",
                                 "displaytext": "TestVPC",
                                 "cidr": '10.0.0.1/24'
                                 },
                         "network": {
                                  "name": "Test Network",
                                  "displaytext": "Test Network",
                                  "netmask": '255.255.255.0'
                                },
                         "lbrule": {
                                    "name": "SSH",
                                    "alg": "leastconn",
                                    # Algorithm used for load balancing
                                    "privateport": 22,
                                    "publicport": 2222,
                                    "openfirewall": False,
                                    "startport": 2222,
                                    "endport": 2222,
                                    "protocol": "TCP",
                                    "cidrlist": '0.0.0.0/0',
                                },
                         "natrule": {
                                    "privateport": 22,
                                    "publicport": 22,
                                    "startport": 22,
                                    "endport": 22,
                                    "protocol": "TCP",
                                    "cidrlist": '0.0.0.0/0',
                                },
                         "fw_rule": {
                                    "startport": 1,
                                    "endport": 6000,
                                    "cidr": '0.0.0.0/0',
                                    # Any network (For creating FW rule)
                                    "protocol": "TCP"
                                },
                         "http_rule": {
                                    "startport": 80,
                                    "endport": 80,
                                    "cidrlist": '0.0.0.0/0',
                                    "protocol": "TCP"
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
                          "ostype": 'CentOS 5.6 (64-bit)',
                         # Cent OS 5.3 (64 bit)
                         "sleep": 60,
                         "timeout": 10,
                         "mode": 'advanced'
                    }

class TestVPCRouterOneNetwork(cloudstackTestCase):

    @classmethod
    def setUpClass(cls):
        cls._cleanup = []
        cls.testClient = super(TestVPCRouterOneNetwork, cls).getClsTestClient()
        cls.api_client = cls.testClient.getApiClient()

        cls.services = Services().services
        # Get Zone, Domain and templates
        cls.domain = get_domain(cls.api_client)
        cls.zone = get_zone(cls.api_client, cls.testClient.getZoneForTests())
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
        cls._cleanup.append(cls.service_offering)
        cls.vpc_off = VpcOffering.create(
                                     cls.api_client,
                                     cls.services["redundant_vpc_offering"]
                                     )
        cls.vpc_off.update(cls.api_client, state='Enabled')
        cls._cleanup.append(cls.vpc_off)

        cls.account = Account.create(
                                     cls.api_client,
                                     cls.services["account"],
                                     admin=True,
                                     domainid=cls.domain.id
                                     )
        cls._cleanup.insert(0, cls.account)

        cls.services["vpc"]["cidr"] = '10.1.1.1/16'
        cls.vpc = VPC.create(
                         cls.api_client,
                         cls.services["vpc"],
                         vpcofferingid=cls.vpc_off.id,
                         zoneid=cls.zone.id,
                         account=cls.account.name,
                         domainid=cls.account.domainid
                         )

        cls.nw_off = NetworkOffering.create(
                                            cls.api_client,
                                            cls.services["network_offering"],
                                            conservemode=False
                                            )
        # Enable Network offering
        cls.nw_off.update(cls.api_client, state='Enabled')
        cls._cleanup.append(cls.nw_off)

        # Creating network using the network offering created
        cls.network_1 = Network.create(
                                cls.api_client,
                                cls.services["network"],
                                accountid=cls.account.name,
                                domainid=cls.account.domainid,
                                networkofferingid=cls.nw_off.id,
                                zoneid=cls.zone.id,
                                gateway='10.1.1.1',
                                vpcid=cls.vpc.id
                                )

        # Spawn an instance in that network
        vm_3 = VirtualMachine.create(
                                  cls.api_client,
                                  cls.services["virtual_machine"],
                                  accountid=cls.account.name,
                                  domainid=cls.account.domainid,
                                  serviceofferingid=cls.service_offering.id,
                                  networkids=[str(cls.network_1.id)]
                                  )

        vms = VirtualMachine.list(
                                  cls.api_client,
                                  account=cls.account.name,
                                  domainid=cls.account.domainid,
                                  listall=True
                                  )

        public_ips = PublicIPAddress.list(
                                    cls.api_client,
                                    networkid=cls.network_1.id,
                                    listall=True,
                                    isstaticnat=True,
                                    account=cls.account.name,
                                    domainid=cls.account.domainid
                                  )
        
        public_ip_2 = PublicIPAddress.create(
                                cls.api_client,
                                accountid=cls.account.name,
                                zoneid=cls.zone.id,
                                domainid=cls.account.domainid,
                                networkid=cls.network_1.id,
                                vpcid=cls.vpc.id
                                )

        lb_rule = LoadBalancerRule.create(
                                    cls.api_client,
                                    cls.services["lbrule"],
                                    ipaddressid=public_ip_2.ipaddress.id,
                                    accountid=cls.account.name,
                                    networkid=cls.network_1.id,
                                    vpcid=cls.vpc.id,
                                    domainid=cls.account.domainid
                                )
 
        lb_rule.assign(cls.api_client, [vm_3])

        nwacl_lb = NetworkACL.create(
                                cls.api_client,
                                networkid=cls.network_1.id,
                                services=cls.services["lbrule"],
                                traffictype='Ingress'
                                )

        nwacl_internet_1 = NetworkACL.create(
                                cls.api_client,
                                networkid=cls.network_1.id,
                                services=cls.services["http_rule"],
                                traffictype='Egress'
                                )
        
    @classmethod
    def tearDownClass(cls):
        try:
            #Cleanup resources used
            cleanup_resources(cls.api_client, cls._cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
        return

    def setUp(self):
        self.api_client = self.testClient.getApiClient()
        self.cleanup = []
        return

    def tearDown(self):
        try:
            #Clean up, terminate the created network offerings
            cleanup_resources(self.api_client, self.cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
       
        return

    def validate_vpc_offering(self, vpc_offering):
        """Validates the VPC offering"""

        self.debug("Check if the VPC offering is created successfully?")
        vpc_offs = VpcOffering.list(
                                    self.api_client,
                                    id=vpc_offering.id
                                    )
        self.assertEqual(
                         isinstance(vpc_offs, list),
                         True,
                         "List VPC offerings should return a valid list"
                         )
        self.assertEqual(
                 vpc_offering.name,
                 vpc_offs[0].name,
                "Name of the VPC offering should match with listVPCOff data"
                )
        self.debug(
                "VPC offering is created successfully - %s" %
                                                        vpc_offering.name)
        return

    def validate_vpc_network(self, network, state=None):
        """Validates the VPC network"""

        self.debug("Check if the VPC network is created successfully?")
        vpc_networks = VPC.list(
                                    self.api_client,
                                    id=network.id
                          )
        self.assertEqual(
                         isinstance(vpc_networks, list),
                         True,
                         "List VPC network should return a valid list"
                         )
        self.assertEqual(
                 network.name,
                 vpc_networks[0].name,
                "Name of the VPC network should match with listVPC data"
                )
        if state:
            self.assertEqual(
                 vpc_networks[0].state,
                 state,
                "VPC state should be '%s'" % state
                )
        self.debug("VPC network validated - %s" % network.name)
        return

    def validate_network_rules(self):
        """ Validate network rules
        """
        vms = VirtualMachine.list(
                                  self.api_client,
                                  account=self.account.name,
                                  domainid=self.account.domainid,
                                  listall=True
                                  )
        public_ips = PublicIPAddress.list(
                                          self.api_client,
                                          account=self.account.name,
                                          domainid=self.account.domainid,
                                          listall=True
                                         )
        for vm, public_ip in zip(vms, public_ips):
            try:
                ssh_1 = vm.get_ssh_client(
                                ipaddress=public_ip.ipaddress.ipaddress)
                self.debug("SSH into VM is successfully")

                self.debug("Verifying if we can ping to outside world from VM?")
                # Ping to outsite world
                res = ssh_1.execute("ping -c 1 www.google.com")
                # res = 64 bytes from maa03s17-in-f20.1e100.net (74.125.236.212):
                # icmp_req=1 ttl=57 time=25.9 ms
                # --- www.l.google.com ping statistics ---
                # 1 packets transmitted, 1 received, 0% packet loss, time 0ms
                # rtt min/avg/max/mdev = 25.970/25.970/25.970/0.000 ms
            except Exception as e:
                self.fail("Failed to SSH into VM - %s, %s" %
                                    (public_ip.ipaddress.ipaddress, e))

            result = str(res)
            self.assertEqual(
                             result.count("1 received"),
                             1,
                             "Ping to outside world from VM should be successful"
                             )

    @attr(tags=["advanced", "intervlan", "provisioining"])
    def test_01_start_stop_router_after_addition_of_one_guest_network(self):
        """ Test start/stop of router after addition of one guest network
	    """
        # Validations
	    #1. Create a VPC with cidr - 10.1.1.1/16
        #2. Add network1(10.1.1.1/24) to this VPC. 
        #3. Deploy vm1,vm2 and vm3 such that they are part of network1.
        #4. Create a PF /Static Nat/LB rule for vms in network1.
        #5. Create ingress network ACL for allowing all the above rules from a public ip range on network1.
        #6. Create egress network ACL for network1 to access google.com.
        #7. Create a private gateway for this VPC and add a static route to this gateway.
        #8. Create a VPN gateway for this VPC and add a static route to this gateway.
        #9. Make sure that all the PF,LB and Static NAT rules work as expected. 
        #10. Make sure that we are able to access google.com from all the user Vms.
        #11. Make sure that the newly added private gateway's and VPN gateway's static routes work as expected

        self.validate_vpc_offering(self.vpc_off)
        self.validate_vpc_network(self.vpc)

        # Stop the VPC Router
        routers = Router.list(
                              self.api_client,
                              account=self.account.name,
                              domainid=self.account.domainid,
                              listall=True
                              )
        self.assertEqual(
                         isinstance(routers, list),
                         True,
                         "List Routers should return a valid list"
                         )
        router = routers[0]	
        self.debug("Stopping the router with ID: %s" % router.id)

        #Stop the router
        cmd = stopRouter.stopRouterCmd()
        cmd.id = router.id
        self.api_client.stopRouter(cmd)
	
        #List routers to check state of router
        router_response = list_routers(
                                    self.api_client,
                                    id=router.id
                                    )
        self.assertEqual(
                            isinstance(router_response, list),
                            True,
                            "Check list response returns a valid list"
                        )
        #List router should have router in stopped state
        self.assertEqual(
                            router_response[0].state,
                            'Stopped',
                            "Check list router response for router state"
                        )

        self.debug("Stopped the router with ID: %s" % router.id)

        # Start The Router
        self.debug("Starting the router with ID: %s" % router.id)
        cmd = startRouter.startRouterCmd()
        cmd.id = router.id
        self.api_client.startRouter(cmd)

        #List routers to check state of router
        router_response = list_routers(
                                    self.api_client,
                                    id=router.id
                                    )
        self.assertEqual(
                            isinstance(router_response, list),
                            True,
                            "Check list response returns a valid list"
                        )
        #List router should have router in running state
        self.assertEqual(
                            router_response[0].state,
                            'Running',
                            "Check list router response for router state"
                        )
        self.debug("Started the router with ID: %s" % router.id)
        
        return

    @attr(tags=["advanced", "intervlan"])
    def test_02_reboot_router_after_addition_of_one_guest_network(self):
        """ Test reboot of router after addition of one guest network
	    """
        # Validations
	    #1. Create a VPC with cidr - 10.1.1.1/16
        #2. Add network1(10.1.1.1/24) to this VPC. 
        #3. Deploy vm1,vm2 and vm3 such that they are part of network1.
        #4. Create a PF /Static Nat/LB rule for vms in network1.
        #5. Create ingress network ACL for allowing all the above rules from a public ip range on network1.
        #6. Create egress network ACL for network1 to access google.com.
        #7. Create a private gateway for this VPC and add a static route to this gateway.
        #8. Create a VPN gateway for this VPC and add a static route to this gateway.
        #9. Make sure that all the PF,LB and Static NAT rules work as expected. 
        #10. Make sure that we are able to access google.com from all the user Vms.
        #11. Make sure that the newly added private gateway's and VPN gateway's static routes work as expected

        self.validate_vpc_offering(self.vpc_off)
        self.validate_vpc_network(self.vpc)

        routers = Router.list(
                              self.api_client,
                              account=self.account.name,
                              domainid=self.account.domainid,
                              listall=True
                              )
        self.assertEqual(
                         isinstance(routers, list),
                         True,
                         "List Routers should return a valid list"
                         )
        router = routers[0]	

        self.debug("Rebooting the router ...")
        #Reboot the router
        cmd = rebootRouter.rebootRouterCmd()
        cmd.id = router.id
        self.api_client.rebootRouter(cmd)

        #List routers to check state of router
        router_response = list_routers(
                                    self.api_client,
                                    id=router.id
                                    )
        self.assertEqual(
                            isinstance(router_response, list),
                            True,
                            "Check list response returns a valid list"
                        )
        #List router should have router in running state and same public IP
        self.assertEqual(
                            router_response[0].state,
                            'Running',
                            "Check list router response for router state"
                        )
        return

    @attr(tags=["advanced", "intervlan"])
    def test_03_destroy_router_after_addition_of_one_guest_network(self):
        """ Test destroy of router after addition of one guest network
        """
        # Validations
	    #1. Create a VPC with cidr - 10.1.1.1/16
        #2. Add network1(10.1.1.1/24) to this VPC. 
        #3. Deploy vm1,vm2 and vm3 such that they are part of network1.
        #4. Create a PF /Static Nat/LB rule for vms in network1.
        #5. Create ingress network ACL for allowing all the above rules from a public ip range on network1.
        #6. Create egress network ACL for network1 to access google.com.
        #7. Create a private gateway for this VPC and add a static route to this gateway.
        #8. Create a VPN gateway for this VPC and add a static route to this gateway.
        #9. Make sure that all the PF,LB and Static NAT rules work as expected. 
        #10. Make sure that we are able to access google.com from all the user Vms.
        #11. Make sure that the newly added private gateway's and VPN gateway's static routes work as expected

        self.validate_vpc_offering(self.vpc_off)
        self.validate_vpc_network(self.vpc)

        routers = Router.list(
                              self.api_client,
                              account=self.account.name,
                              domainid=self.account.domainid,
                              listall=True
                              )
        self.assertEqual(
                         isinstance(routers, list),
                         True,
                         "List Routers should return a valid list"
                         )
     
        Router.destroy( self.api_client,
		        id=routers[0].id
		      )
		
        routers = Router.list(
                              self.api_client,
                              account=self.account.name,
                              domainid=self.account.domainid,
                              listall=True
                              )
        self.assertEqual(
                         isinstance(routers, list),
                         False,
                         "List Routers should be empty"
                         )
        return
