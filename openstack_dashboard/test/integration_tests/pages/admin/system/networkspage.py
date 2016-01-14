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

from openstack_dashboard.test.integration_tests.pages.project.network \
    import networkspage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables


class NetworksTable(networkspage.NetworksTable):
    CREATE_NETWORK_FORM_FIELDS = ("name", "tenant_id", "network_type",
                                  "physical_network", "segmentation_id",
                                  "admin_state", "shared", "external")

    @tables.bind_table_action('create')
    def create_network(self, create_button):
        create_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.CREATE_NETWORK_FORM_FIELDS)


class NetworksPage(networkspage.NetworksPage):
    DEFAULT_ACCESSIBILITY = False
    DEFAULT_EXTERNAL = False
    DEFAULT_STATUS = "UP"
    PROVIDER_DEFAULT = "Local"
    PROVIDER_FLAT = "Flat"
    PROVIDER_VLAN = "VLAN"
    PROVIDER_GRE = "GRE"
    PROVIDER_VXLAN = "VXLAN"

    def create_network(self, name, project, provider_net_type=PROVIDER_DEFAULT,
                       physical_net=None, segmentation_id=None,
                       admin_state=DEFAULT_STATUS,
                       is_shared=DEFAULT_ACCESSIBILITY,
                       is_external=DEFAULT_EXTERNAL):
        create_network_form = self.networks_table.create_network()
        create_network_form.name.text = name
        create_network_form.tenant_id.text = project
        create_network_form.network_type.text = provider_net_type
        if provider_net_type == self.PROVIDER_VLAN:
            create_network_form.physical_network.text = physical_net
            create_network_form.segmentation_id.text = segmentation_id
        create_network_form.admin_state.text = admin_state
        if is_shared:
            create_network_form.shared.mark()
        if is_external:
            create_network_form.external.mark()
        create_network_form.submit()

    @property
    def networks_table(self):
        return NetworksTable(self.driver, self.conf)
