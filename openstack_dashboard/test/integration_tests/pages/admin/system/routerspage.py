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
    import routerspage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables


class RoutersTable(routerspage.RoutersTable):

    UPDATE_ROUTER_FORM_FIELDS = ("name", "admin_state", "router_id", "mode")

    @tables.bind_row_action('update')
    def update_router(self, update_button, row):
        update_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.UPDATE_ROUTER_FORM_FIELDS)


class RoutersPage(routerspage.RoutersPage):

    @property
    def routers_table(self):
        return RoutersTable(self.driver, self.conf)

    def edit_router(self, name, new_name, admin_state=None):
        row = self._get_row_with_router_name(name)
        edit_router_form = self.routers_table.edit_router(row)
        edit_router_form.name.text = new_name
        if admin_state is not None:
            edit_router_form.admin_state.text = admin_state
        edit_router_form.submit()

    def get_router_info(self, router_name):
        row = self._get_row_with_router_name(router_name)
        update_router_form = self.routers_table.update_router(row)
        info = {'name': update_router_form.name.text,
                'admin_state': update_router_form.admin_state.text,
                'router_id': update_router_form.router_id.text,
                'mode': update_router_form.mode.text}
        update_router_form.cancel()
        return info
