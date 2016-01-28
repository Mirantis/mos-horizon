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

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables
from selenium.common import exceptions
from selenium.webdriver.common import by


class ElementTable(tables.TableRegion):
    name = "element"
    CREATE_FORM_FIELDS = ()
    EDIT_FORM_FIELDS = ()

    @tables.bind_table_action('create')
    def create(self, create_button):
        create_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.CREATE_FORM_FIELDS)

    @tables.bind_table_action('delete')
    def delete(self, delete_button):
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('edit', primary=True)
    def edit(self, edit_button, row):
        edit_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.EDIT_FORM_FIELDS)


class SubnetsTable(ElementTable):
    name = "subnets"
    CREATE_FORM_FIELDS = (("subnet_name", "cidr", "ip_version",
                           "gateway_ip", "no_gateway"),
                          ("enable_dhcp", "allocation_pools",
                           "dns_nameservers", "host_routes"))

    EDIT_FORM_FIELDS = CREATE_FORM_FIELDS

    @tables.bind_table_action('create')
    def create(self, create_button):
        create_button.click()
        return forms.TabbedFormRegion(self.driver, self.conf,
                                      self.CREATE_FORM_FIELDS)

    @tables.bind_row_action('edit')
    def edit(self, edit_button):
        edit_button.click()
        return forms.TabbedFormRegion(self.driver, self.conf,
                                      self.EDIT_FORM_FIELDS)


class NetworksTable(ElementTable):
    name = "networks"
    CREATE_FORM_FIELDS = (("net_name", "admin_state", "shared",
                           "with_subnet"),
                          ("subnet_name", "cidr", "ip_version",
                           "gateway_ip", "no_gateway"),
                          ("enable_dhcp", "allocation_pools",
                           "dns_nameservers", "host_routes"))

    EDIT_FORM_FIELDS = ("name", "network_id", "admin_state",
                                "shared")

    ADD_SUBNET_FORM_FIELDS = (("subnet_name", "cidr", "ip_version",
                               "gateway_ip", "no_gateway"),
                              ("enable_dhcp", "allocation_pools",
                               "dns_nameservers", "host_routes"))

    @tables.bind_table_action('create')
    def create(self, create_button):
        create_button.click()
        return forms.TabbedFormRegion(self.driver, self.conf,
                                      self.CREATE_FORM_FIELDS)

    @tables.bind_row_action('subnet')
    def edit_add_subnet(self, edit_button, row):
        edit_button.click()
        return forms.TabbedFormRegion(self.driver, self.conf,
                                      self.ADD_SUBNET_FORM_FIELDS)

    @tables.bind_row_action('delete')
    def edit_delete_network(self, delete_button, row):
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)


class NetworksPage(basepage.BaseNavigationPage):
    DEFAULT_ADMIN_STATE = 'True'
    DEFAULT_CREATE_SUBNET = True
    DEFAULT_IP_VERSION = '4'
    DEFAULT_DISABLE_GATEWAY = False
    DEFAULT_ENABLE_DHCP = True
    NETWORKS_TABLE_NAME_COLUMN = 'name'
    NETWORKS_TABLE_STATUS_COLUMN = 'status'
    SUBNET_TAB_INDEX = 1
    DETAILS_TAB_INDEX = 2

    def __init__(self, driver, conf):
        super(NetworksPage, self).__init__(driver, conf)
        self._page_title = "Networks"

    def _get_row_with_network_name(self, name):
        return self.networks_table.get_row(
            self.NETWORKS_TABLE_NAME_COLUMN, name)

    @property
    def networks_table(self):
        return NetworksTable(self.driver, self.conf)

    def create_network(self, network_name, subnet_name,
                       admin_state=DEFAULT_ADMIN_STATE,
                       create_subnet=DEFAULT_CREATE_SUBNET,
                       network_address=None, ip_version=DEFAULT_IP_VERSION,
                       gateway_ip=None,
                       disable_gateway=DEFAULT_DISABLE_GATEWAY,
                       enable_dhcp=DEFAULT_ENABLE_DHCP, allocation_pools=None,
                       dns_name_servers=None, host_routes=None):
        create_network_form = self.networks_table.create()
        create_network_form.net_name.text = network_name
        create_network_form.admin_state.value = admin_state
        if not create_subnet:
            create_network_form.with_subnet.unmark()
        else:
            create_network_form.switch_to(self.SUBNET_TAB_INDEX)
            create_network_form.subnet_name.text = subnet_name
            if network_address is None:
                network_address = self.conf.network.network_cidr
            create_network_form.cidr.text = network_address

            create_network_form.ip_version.value = ip_version
            if gateway_ip is not None:
                create_network_form.gateway_ip.text = gateway_ip
            if disable_gateway:
                create_network_form.disable_gateway.mark()

            create_network_form.switch_to(self.DETAILS_TAB_INDEX)
            if not enable_dhcp:
                create_network_form.enable_dhcp.unmark()
            if allocation_pools is not None:
                create_network_form.allocation_pools.text = allocation_pools
            if dns_name_servers is not None:
                create_network_form.dns_nameservers.text = dns_name_servers
            if host_routes is not None:
                create_network_form.host_routes.text = host_routes
        create_network_form.submit()

    def delete_network(self, name):
        row = self._get_row_with_network_name(name)
        confirm_delete_networks_form = \
            self.networks_table.edit_delete_network(row)
        confirm_delete_networks_form.submit()

    def is_network_present(self, name):
        return bool(self._get_row_with_network_name(name))

    def is_network_active(self, name):

        def cell_getter():
            row = self._get_row_with_network_name(name)
            return row and row.cells[self.NETWORKS_TABLE_STATUS_COLUMN]

        return bool(self.networks_table.wait_cell_status(cell_getter,
                                                         'Active'))

    def add_subnet(self, net_name, subnet_name,
                   network_address=None, ip_version=DEFAULT_IP_VERSION,
                   gateway_ip=None,
                   disable_gateway=DEFAULT_DISABLE_GATEWAY,
                   enable_dhcp=DEFAULT_ENABLE_DHCP, allocation_pools=None,
                   dns_name_servers=None, host_routes=None):
        row = self._get_row_with_network_name(net_name)
        add_subnet_form = self.networks_table.edit_add_subnet(row)
        add_subnet_form.subnet_name.text = subnet_name
        if network_address is None:
            network_address = self.conf.network.network_cidr
        add_subnet_form.cidr.text = network_address
        add_subnet_form.ip_version.value = ip_version
        if gateway_ip is not None:
            add_subnet_form.gateway_ip.text = gateway_ip
        if disable_gateway:
            add_subnet_form.disable_gateway.mark()

        add_subnet_form.switch_to(self.SUBNET_TAB_INDEX)
        if not enable_dhcp:
            add_subnet_form.enable_dhcp.unmark()
        if allocation_pools is not None:
            add_subnet_form.allocation_pools.text = allocation_pools
        if dns_name_servers is not None:
            add_subnet_form.dns_nameservers.text = dns_name_servers
        if host_routes is not None:
            add_subnet_form.host_routes.text = host_routes
        add_subnet_form.submit()
        return NetworkOverviewPage(self.driver, self.conf, net_name)

    def go_to_overview(self, name):
        _network_items_locator = (by.By.CSS_SELECTOR, 'a[href$="/detail"]')
        net_items = self._get_elements(*_network_items_locator)

        for item in net_items:
            if item.text == name:
                item.click()
                break
        else:
            raise exceptions.NoSuchElementException(
                "Not found element with text: %s" % name)
        return NetworkOverviewPage(self.driver, self.conf, name)


class NetworkOverviewPage(basepage.BaseNavigationPage):
    DEFAULT_ADMIN_STATE = 'True'
    DEFAULT_IP_VERSION = '4'
    DEFAULT_DISABLE_GATEWAY = False
    DEFAULT_ENABLE_DHCP = True
    DETAILS_TAB_INDEX = 1
    TABLE_NAME_COLUMN = 'name'
    _edit_network_locator = (
        by.By.CSS_SELECTOR,
        'form.actions_column > .btn-group > a.btn:nth-child(1)')
    _dropdown_open_locator = (
        by.By.CSS_SELECTOR,
        'form.actions_column > .btn-group > a.btn:nth-child(2)')
    _dropdown_menu_locator = (
        by.By.CSS_SELECTOR,
        'form.actions_column > .btn-group > ul.row_actions > li > *')

    def __init__(self, driver, conf, network_name):
        super(NetworkOverviewPage, self).__init__(driver, conf)
        self._page_title = "Network Details: {}".format(network_name)

    @property
    def subnets_table(self):
        return SubnetsTable(self.driver, self.conf)

    def _get_row_with_name(self, name, table):
        return table.get_row(self.TABLE_NAME_COLUMN, name)

    def _get_row_action(self, action_name):
        open_dropdown_elem = self._get_element(*self._dropdown_open_locator)
        open_dropdown_elem.click()
        for action in self._get_elements(*self._dropdown_menu_locator):
            pattern = "__action_%s" % action_name
            if action.get_attribute('id').endswith(pattern):
                action_element = action
                break
        return action_element

    def delete_network(self):
        delete_elem = self._get_row_action('delete')
        delete_elem.click()
        confirm_delete_network_form = forms.BaseFormRegion(self.driver,
                                                           self.conf)
        confirm_delete_network_form.submit()
        return NetworksPage(self.driver, self.conf)

    def create_subnet(self, subnet_name,
                      network_address=None, ip_version=DEFAULT_IP_VERSION,
                      gateway_ip=None,
                      disable_gateway=DEFAULT_DISABLE_GATEWAY,
                      enable_dhcp=DEFAULT_ENABLE_DHCP, allocation_pools=None,
                      dns_name_servers=None, host_routes=None):
        create_subnet_form = self.subnets_table.create()
        create_subnet_form.subnet_name.text = subnet_name
        if network_address is None:
            network_address = self.conf.network.network_cidr
        create_subnet_form.cidr.text = network_address
        create_subnet_form.ip_version.value = ip_version
        if gateway_ip is not None:
            create_subnet_form.gateway_ip.text = gateway_ip
        if disable_gateway:
            create_subnet_form.disable_gateway.mark()

        create_subnet_form.tabs.switch_to(self.DETAILS_TAB_INDEX)
        if not enable_dhcp:
            create_subnet_form.enable_dhcp.unmark()
        if allocation_pools is not None:
            create_subnet_form.allocation_pools.text = allocation_pools
        if dns_name_servers is not None:
            create_subnet_form.dns_nameservers.text = dns_name_servers
        if host_routes is not None:
            create_subnet_form.host_routes.text = host_routes
        create_subnet_form.submit()

    def delete_subnet(self, name):
        row = self._get_row_with_name(name, self.subnets_table)
        row.mark()
        confirm_delete_subnet_form = self.subnets_table.delete()
        confirm_delete_subnet_form.submit()

    def is_subnet_present(self, name):
        return bool(self._get_row_with_name(name, self.subnets_table))
