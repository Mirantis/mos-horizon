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
import re
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import time
from time import sleep

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.pages.project.compute. \
    instancespage import InstancesTable
from openstack_dashboard.test.integration_tests import basewebobject
from openstack_dashboard.test.integration_tests.pages.project.network.\
    networkspage import NetworksTable
from openstack_dashboard.test.integration_tests.pages.project.network.\
    routerspage import RoutersTable
from openstack_dashboard.test.integration_tests.pages.project.network.\
    routerspage import InterfacesTable


class NetworktopologyPage(basepage.BaseNavigationPage):
    def __init__(self, driver, conf):
        super(NetworktopologyPage, self).__init__(driver, conf)
        self._page_title = "Network Topology"

    _toggle_labels = (By.CSS_SELECTOR, 'button[id="toggle_labels"]')
    _toggle_networks = (By.CSS_SELECTOR, 'button[id="toggle_networks"]')

    _launch_instance = (By.CSS_SELECTOR, 'a[id="instances__action_launch"]')
    _create_network = (By.CSS_SELECTOR, 'a[id="networks__action_create"]')
    _create_router = (By.CSS_SELECTOR, 'a[id="Routers__action_create"]')
    _networks_locator = (
        By.CSS_SELECTOR, 'div.modal-dialog ul.networklist.ui-sortable li')
    SUBNET_TAB_INDEX = 1
    NETWORK_TAB_INDEX = 2

    # some vars from instances page
    DEFAULT_FLAVOR = 'm1.tiny'
    DEFAULT_COUNT = 1
    DEFAULT_BOOT_SOURCE = 'Boot from image'
    DEFAULT_VOLUME_NAME = None
    DEFAULT_SNAPSHOT_NAME = None
    DEFAULT_VOLUME_SNAPSHOT_NAME = None
    DEFAULT_VOL_DELETE_ON_INSTANCE_DELETE = False
    DEFAULT_SECURITY_GROUP = True

    INSTANCES_TABLE_NAME_COLUMN = 'name'
    INSTANCES_TABLE_STATUS_COLUMN = 'status'
    INSTANCES_TABLE_IP_COLUMN = 'ip'
    INSTANCES_TABLE_IMAGE_NAME_COLUMN = 'image_name'

    DEFAULT_BOOT_SOURCE_NG = 'image'
    DEFAULT_VOLUME_CREATION_NG = 'No'
    DEFAULT_BOOT_SOURCE_NAME_NG = 'TestVM'
    DEFAULT_NETWORK_NG = "admin_internal_net"

    @property
    def topology(self):
        return TopologyCanvas(self.driver, self.conf)

    @property
    def toggle_labels(self):
        return self._get_element(*self._toggle_labels)

    @property
    def toggle_networks(self):
        return self._get_element(*self._toggle_networks)

    @property
    def launch_instance_btn(self):
        return self._get_element(*self._launch_instance)

    @property
    def create_network_btn(self):
        return self._get_element(*self._create_network)

    @property
    def create_router_btn(self):
        return self._get_element(*self._create_router)

    def launch_instance(self):
        self._get_element(*self._launch_instance).click()
        return forms.TabbedFormRegion(
            self.driver,
            self.conf,
            InstancesTable.CREATE_INSTANCE_FORM_FIELDS)

    def create_network_action(self):
        self._get_element(*self._create_network).click()
        return forms.TabbedFormRegion(
            self.driver,
            self.conf,
            field_mappings=NetworksTable.CREATE_NETWORK_FORM_FIELDS)

    def create_router_action(self):
        self._get_element(*self._create_router).click()
        return forms.FormRegion(
            self.driver,
            self.conf,
            field_mappings=RoutersTable.CREATE_ROUTER_FORM_FIELDS)

    def create_instance(self, instance_name,
                        available_zone=None,
                        instance_count=1,
                        flavor="m1.tiny",
                        boot_source='Boot from image',
                        source_name=None,
                        device_size=None,
                        vol_delete_on_instance_delete=False,
                        networks=None,
                        net=None):
        launch_instance_form = self.launch_instance()
        if not available_zone:
            available_zone = self.conf.launch_instances.available_zone
        launch_instance_form.availability_zone.value = available_zone
        launch_instance_form.name.text = instance_name
        launch_instance_form.flavor.text = flavor
        launch_instance_form.count.value = instance_count
        launch_instance_form.source_type.text = boot_source
        if not source_name:
            source_name = self.conf.launch_instances.image_name
        launch_instance_form.image_id.text = source_name
        if device_size:
            launch_instance_form.volume_size.value = device_size
        if vol_delete_on_instance_delete:
            launch_instance_form.vol_delete_on_instance_delete.mark()
        if networks:
            launch_instance_form.switch_to(self.NETWORK_TAB_INDEX)
            net_elems = self._get_elements(*self._networks_locator)
            net_elem = [elem for elem in net_elems if net in elem.text][0]
            net_elem.find_element_by_css_selector('a:nth-child(2)').click()
        launch_instance_form.submit()

    @property
    def instances_table(self):
        return InstancesTable(self.driver, self.conf)

    def create_instance_ng(self, name,
                           availability_zone=None,
                           instance_count=DEFAULT_COUNT,
                           boot_source_type=DEFAULT_BOOT_SOURCE_NG,
                           image_name=DEFAULT_BOOT_SOURCE_NAME_NG,
                           vol_create=DEFAULT_VOLUME_CREATION_NG,
                           flavor_size=DEFAULT_FLAVOR,
                           network=DEFAULT_NETWORK_NG):
        if not availability_zone:
            availability_zone = self.conf.launch_instances.available_zone

        instance_form = self.instances_table.launch_instance_ng()
        sleep(2)
        instance_form.name.text = name
        instance_form.availability_zone.text = availability_zone
        instance_form.instance_count.value = instance_count

        instance_form.switch_to(1)
        sleep(2)
        instance_form.boot_source_type = boot_source_type
        instance_form.vol_create.text = vol_create
        instance_form.boot_sources.allocate_item(name=image_name)

        instance_form.switch_to(2)
        sleep(2)
        instance_form.flavors.allocate_item(name=flavor_size)

        instance_form.switch_to(3)
        sleep(2)
        instance_form.networks.allocate_item(name=network)
        instance_form.submit()

    def create_network(self, network_name, subnet_name,
                       disable_gateway=True, network_address=None):
        create_network_form = self.create_network_action()
        create_network_form.net_name.text = network_name
        create_network_form.switch_to(self.SUBNET_TAB_INDEX)
        create_network_form.subnet_name.text = subnet_name
        if network_address is None:
            network_address = self.conf.network.network_cidr
        create_network_form.cidr.text = network_address
        if disable_gateway:
            create_network_form.no_gateway.mark()
        create_network_form.submit()

    def create_router(self, name, admin_state_up='True',
                      external_network='public'):
        create_router_form = self.create_router_action()
        create_router_form.name.text = name
        create_router_form.admin_state_up.value = admin_state_up
        create_router_form.external_network.text = external_network
        create_router_form.submit()

    def _is_labels_visible(self):
        return self.toggle_labels.get_attribute('class').endswith('active')

    def hide_labels(self):
        if self._is_labels_visible():
            self.toggle_labels.click()

    def show_labels(self):
        if not self._is_labels_visible():
            self.toggle_labels.click()

    def _is_network_collapsed(self):
        return self.toggle_networks.get_attribute('class').endswith('active')

    def expand_network(self):
        if self._is_network_collapsed():
            self.toggle_networks.click()

    def collapse_network(self):
        if not self._is_network_collapsed():
            self.toggle_networks.click()


class TopologyCanvas(basepage.BasePage):
    _nodes_locator = (By.CSS_SELECTOR, 'g.node')
    _lines_locator = (By.CSS_SELECTOR, 'line.link')
    _node_type_locator = (By.XPATH, '*[contains(@transform, "scale")]')
    _node_label_locator = (By.XPATH, '*[@class="nodeLabel"]')
    _vm_count_locator = (By.XPATH, '*[@class="vmCount"]')
    _svg_locator = (By.CSS_SELECTOR, 'path.hulls')

    @property
    def nodes(self):
        return self._get_elements(*self._nodes_locator)

    @property
    def lines(self):
        return self._get_elements(*self._lines_locator)

    def _get_svg_definition(self):
        return self._get_element(*self._svg_locator).get_attribute('d')

    def wait_for_svg_loads(self):
        self._wait_till_element_visible(self._get_element(*self._svg_locator))
        svg_definition = self._get_svg_definition()
        time.sleep(1)
        svg_definition_new = self._get_svg_definition()
        while svg_definition != svg_definition_new:
            svg_definition = svg_definition_new
            svg_definition_new = self._get_svg_definition()

    def _get_nodes(self):
        nodes = self.nodes
        nodes_dict = {}
        for node in nodes:
            nodes_dict[node] = [
                node.find_element(*self._node_type_locator).get_attribute(
                    'transform'),
                re.findall(r'\d+\.*\d*', node.get_attribute('transform')),
                node.find_element(*self._node_label_locator).text]
        return nodes_dict.items()

    def get_instances(self):
        instances = {k: v for k, v in self._get_nodes()
                     if v[0].startswith('scale(1)')}.items()
        return instances

    def get_internal_networks(self):
        int_nets = {k: v for k, v in self._get_nodes()
                    if v[0].startswith('scale(1.5)')}.items()
        return int_nets

    def get_external_networks(self):
        ext_nets = {k: v for k, v in self._get_nodes()
                    if v[0].startswith('scale(2.5)')}.items()
        return ext_nets

    def get_routers(self):
        routers = {k: v for k, v in self._get_nodes()
                   if v[0].startswith('scale(1.2)')}.items()
        return routers

    def get_lines(self):
        lines = self.lines
        points = []
        for line in lines:
            x1, y1 = [line.get_attribute('x1'), line.get_attribute('y1')]
            x2, y2 = [line.get_attribute('x2'), line.get_attribute('y2')]
            points.append(dict.fromkeys(["{0}:{1}".format(x1, y1),
                                         "{0}:{1}".format(x2, y2)]))
        return points

    def is_link_between_nodes_available(self, node1, node2):
        x1, y1 = node1[1][1]
        x2, y2 = node2[1][1]
        expected_line = \
            dict.fromkeys(["{0}:{1}".format(x1, y1), "{0}:{1}".format(x2, y2)])
        for line in self.get_lines():
            if line == expected_line:
                return True
        return False

    def _close_active_balloon(self):
        try:
            self._get_element(By.CSS_SELECTOR,
                              'a.closeTopologyBalloon').click()
        except exceptions.NoSuchElementException:
            pass

    def _open_balloon(self, item):
        self._close_active_balloon()
        item[0].click()
        return TopologyBalloon(self.driver, self.conf)

    def delete_instance(self, instance):
        self._open_balloon(instance).delete()

    def is_status_active(self, item):
        def is_active():
            actual_status = self._open_balloon(item).get_status_element().text
            return actual_status == 'Active'
        try:
            self._wait_until(lambda x: is_active(),
                             timeout=120, poll_frequency=2)
        except exceptions.TimeoutException:
            return False
        return True

    def get_vm_count(self, int_net):
        vm_count = int_net[0].find_element(*self._vm_count_locator).text
        if vm_count != '':
            return int(vm_count)
        return None

    def delete_network(self, network):
        self._open_balloon(network).delete()

    def add_interface_to_router(self, router, subnet):
        self._open_balloon(router).add_interface(subnet)

    def delete_router(self, router):
        self._open_balloon(router).delete()


class TopologyBalloon(basewebobject.BaseWebObject):
    _balloon_locator = (By.CSS_SELECTOR, 'div.topologyBalloon')
    _body_locator = (By.CSS_SELECTOR, 'div.contentBody')
    _footer_locator = (By.CSS_SELECTOR, 'div.footer')
    _delete_locator = (By.CSS_SELECTOR,
                       "button[class^='delete-device btn btn-danger']")
    _status_locator = (By.CSS_SELECTOR, 'span')
    _add_interface_locator = (By.CSS_SELECTOR, '.add-interface')

    @property
    def balloon(self):
        return self._get_element(*self._balloon_locator)

    @property
    def body(self):
        return self._get_element(*self._body_locator)

    @property
    def add_interface_btn(self):
        return self._get_element(*self._add_interface_locator)

    @property
    def footer(self):
        return self._get_element(*self._footer_locator)

    def delete(self):
        delete_button = self.footer.find_element(*self._delete_locator)
        delete_button.click()
        self.wait_till_balloon_disappears()

    def get_status_element(self):
        status_element = self.body.find_element(*self._status_locator)
        return status_element

    def add_interface_action(self):
        self.add_interface_btn.click()
        return forms.FormRegion(
            self.driver,
            self.conf,
            field_mappings=InterfacesTable.ADD_INTERFACE_FORM_FIELDS)

    def add_interface(self, subnet_name):
        add_interface_form = self.add_interface_action()
        _subnets_locator = (By.CSS_SELECTOR, '#id_subnet_id > option')
        subnet_elems = self.driver.find_elements(*_subnets_locator)
        subnet = [sub for sub in subnet_elems if subnet_name in sub.text][0]
        add_interface_form.subnet_id.text = subnet.text
        add_interface_form.ip_address.text = '10.100.0.254'
        add_interface_form.submit()
