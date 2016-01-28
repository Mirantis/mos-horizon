#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from openstack_dashboard.test.integration_tests import decorators
from openstack_dashboard.test.integration_tests import helpers
from openstack_dashboard.test.integration_tests.regions import messages


@decorators.services_required("neutron")
class TestNetworks(helpers.TestCase):
    NETWORK_NAME = helpers.gen_random_resource_name("network")
    SUBNET_NAME = helpers.gen_random_resource_name("subnet")
    SUBNET_NAME_2 = helpers.gen_random_resource_name("subnet")

    @decorators.skip_new_design
    def test_private_network_create(self):
        """tests the network creation and deletion functionalities:
        * creates a new private network and a new subnet associated with it
        * verifies the network appears in the networks table as active
        * deletes the newly created network
        * verifies the network does not appear in the table after deletion
        """

        networks_page = self.home_pg.go_to_network_networkspage()

        networks_page.create_network(self.NETWORK_NAME, self.SUBNET_NAME)
        self.assertTrue(
            networks_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            networks_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(networks_page.is_network_present(self.NETWORK_NAME))
        self.assertTrue(networks_page.is_network_active(self.NETWORK_NAME))

        networks_page.delete_network(self.NETWORK_NAME)
        self.assertTrue(
            networks_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            networks_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(networks_page.is_network_present(self.NETWORK_NAME))

    def test_subnet_add(self):
        """This test checks add subnet functionality
            Steps:
            1) Login to Horizon dashboard as demo user
            2) Go to Project -> Network -> Networks
            3) Create network with subnet
            4) Add subnet for created network
            5) Check that subnet is created (on NetworkOverview page)
            6) Delete created subnet
            7) Check that subnet was deleted
            8) Check that subnet that was added during creation
             of network is still presented
            9) Delete created network
        """
        networks_page = self.home_pg.go_to_network_networkspage()
        networks_page.create_network(self.NETWORK_NAME, self.SUBNET_NAME)
        self.assertTrue(
            networks_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            networks_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(networks_page.is_network_present(self.NETWORK_NAME))
        self.assertTrue(networks_page.is_network_active(self.NETWORK_NAME))
        overview = networks_page.add_subnet(self.NETWORK_NAME,
                                            self.SUBNET_NAME_2,
                                            network_address='10.50.0.0/16')
        self.assertTrue(overview.is_subnet_present(self.SUBNET_NAME))
        self.assertTrue(overview.is_subnet_present(self.SUBNET_NAME_2))
        overview.delete_subnet(self.SUBNET_NAME_2)
        self.assertTrue(
            networks_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            networks_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(overview.is_subnet_present(self.SUBNET_NAME))
        self.assertFalse(overview.is_subnet_present(self.SUBNET_NAME_2))
        networks_page = overview.delete_network()
        self.assertFalse(networks_page.is_network_present(self.NETWORK_NAME))


class TestAdminNetworks(helpers.AdminTestCase):
    NETWORK_NAME = helpers.gen_random_resource_name("network")

    def test_network_create_delete_from_admin(self):
        """tests the network creation and deletion functionality:
        * creates a new network through Admin panel
        * verifies the network appears in the networks table
        * deletes the newly created network
        * verifies the network does not appear in the table after deletion
        """
        networks_page = self.home_pg.go_to_system_networkspage()
        networks_page.create_network(name=self.NETWORK_NAME,
                                     project=self.HOME_PROJECT)
        self.assertTrue(
            networks_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            networks_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(networks_page.is_network_present(self.NETWORK_NAME))
        self.assertTrue(networks_page.is_network_active(self.NETWORK_NAME))

        networks_page.delete_network(self.NETWORK_NAME)
        self.assertTrue(
            networks_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            networks_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(networks_page.is_network_present(self.NETWORK_NAME))
