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

INSTANCE_NAME = helpers.gen_random_resource_name('instance',
                                                 timestamp=False)


@decorators.services_required("neutron")
class TestNetworkTopology(helpers.AdminTestCase):

    def setUp(self):
        super(TestNetworkTopology, self).setUp()
        topology_page = self.home_pg.go_to_network_networktopologypage()
        topology_page.topology.wait_for_svg_loads()
        vms = topology_page.topology.get_instances()
        for vm in vms:
            topology_page.topology.delete_instance(vm)
            topology_page.find_message_and_dismiss(messages.SUCCESS)
            self.assertFalse(
                topology_page.find_message_and_dismiss(messages.ERROR))

    def test_create_delete_instance_from_network_topology(self):
        """This test checks create/delete instance from network topology page
            Steps:
            1) Login to Horizon Dashboard as reqular user
            2) Go to the Project -> Network -> Network Topology page
            3) Launch new instance from current page
            4) Check instance status (via popup window)
            5) Wait for SVG fully loading (wait for stable state)
            6) Get all instances, routers and networks
            7) Check that all instances are linked to internal network
            8) Check that there are no direct links between instances and
            external network
            9) Check that internal and external networks are linked
            through router
            10) Delete instance
        """
        net_topology_page = self.home_pg.go_to_network_networktopologypage()

        net_topology_page.create_instance(INSTANCE_NAME)
        net_topology_page.find_message_and_dismiss(messages.SUCCESS)
        self.assertFalse(
            net_topology_page.find_message_and_dismiss(messages.ERROR))

        net_topology_page.topology.wait_for_svg_loads()
        net_topology_page.show_labels()
        vms = net_topology_page.topology.get_instances()
        for vm in vms:
            self.assertTrue(net_topology_page.topology.is_status_active(vm))

        net_topology_page.topology.wait_for_svg_loads()
        vm = net_topology_page.topology.get_instances()[0]
        int_net = net_topology_page.topology.get_internal_networks()[0]
        ext_net = net_topology_page.topology.get_external_networks()[0]
        router = net_topology_page.topology.get_routers()[0]

        self.assertTrue(net_topology_page.topology.
                        is_link_between_nodes_available(vm, int_net))
        self.assertFalse(net_topology_page.topology.
                         is_link_between_nodes_available(vm, ext_net))
        self.assertTrue(net_topology_page.topology.
                        is_link_between_nodes_available(int_net, router))
        self.assertTrue(net_topology_page.topology.
                        is_link_between_nodes_available(router, ext_net))
        self.assertFalse(net_topology_page.topology.
                         is_link_between_nodes_available(int_net, ext_net))

        net_topology_page.topology.delete_instance(vm)
        net_topology_page.find_message_and_dismiss(messages.SUCCESS)
        self.assertFalse(
            net_topology_page.find_message_and_dismiss(messages.ERROR))

        net_topology_page.topology.wait_for_svg_loads()
        vms = net_topology_page.topology.get_instances()
        self.assertEqual(len(vms), 0)

    def test_toggle_network(self):
        """This test checks possibility to collapse/expand network
            Steps:
            1) Login to Horizon Dashboard as reqular user
            2) Go to the Project -> Network -> Network Topology page
            3) Launch 2 new instances from current page
            4) Wait for SVG fully loading (wait for stable state)
            6) Collapse network by click 'Toggle Network Collapse' button
            7) Check that no instances are shown
            8) Check that correct count of instances (2) is shown for private
            network
            9) Expand network by 'Toggle Network Collapse' button again
            10) Check that 2 instances are visible now, count of instances is
            not visible for private network
            11) Check that instances have link to private network
            12) Delete instances
        """
        count = 2
        net_topology_page = self.home_pg.go_to_network_networktopologypage()
        net_topology_page.create_instance(INSTANCE_NAME, instance_count=count)
        net_topology_page.find_message_and_dismiss(messages.SUCCESS)
        self.assertFalse(
            net_topology_page.find_message_and_dismiss(messages.ERROR))
        net_topology_page.collapse_network()
        net_topology_page.topology.wait_for_svg_loads()

        vms = net_topology_page.topology.get_instances()
        int_net = net_topology_page.topology.get_internal_networks()[0]
        self.assertEqual(len(vms), 0)
        self.assertEqual(
            net_topology_page.topology.get_vm_count(int_net), count)

        net_topology_page.expand_network()
        net_topology_page.topology.wait_for_svg_loads()
        vms = net_topology_page.topology.get_instances()
        int_net = net_topology_page.topology.get_internal_networks()[0]
        self.assertEqual(len(vms), count)
        self.assertEqual(
            net_topology_page.topology.get_vm_count(int_net), None)

        vms = net_topology_page.topology.get_instances()
        int_net = net_topology_page.topology.get_internal_networks()[0]
        for vm in vms:
            self.assertTrue(net_topology_page.topology.
                            is_link_between_nodes_available(vm, int_net))

        for vm in vms:
            net_topology_page.topology.delete_instance(vm)
            net_topology_page.find_message_and_dismiss(messages.SUCCESS)
            self.assertFalse(
                net_topology_page.find_message_and_dismiss(messages.ERROR))
