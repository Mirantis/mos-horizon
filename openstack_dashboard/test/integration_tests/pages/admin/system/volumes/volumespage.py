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

from openstack_dashboard.test.integration_tests.pages.project.compute.volumes \
    import volumespage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables


class VolumesTable(volumespage.VolumesTable):

    UPDATE_STATUS_FORM_FIELDS = ("status",)

    MIGRATE_VOLUME_FORM_FIELDS = ("name", "current_host", "host")

    @tables.bind_row_action('update_status')
    def update_volume_status(self, update_status_button, row):
        update_status_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.UPDATE_STATUS_FORM_FIELDS)

    @tables.bind_row_action('migrate')
    def migrate_volume(self, migrate_button, row):
        migrate_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.MIGRATE_VOLUME_FORM_FIELDS)


class VolumesPage(volumespage.VolumesPage):

    @property
    def volumes_table(self):
        return VolumesTable(self.driver, self.conf)

    def update_status(self, name, status):
        row = self._get_row_with_volume_name(name)
        volume_status_form = self.volumes_table.update_volume_status(row)
        volume_status_form.status.value = status.lower()
        volume_status_form.submit()

    def migrate_volume(self, name):
        row = self._get_row_with_volume_name(name)
        migrate_volume_form = self.volumes_table.migrate_volume(row)
        cur_host = migrate_volume_form.current_host.text
        values = [option.text for option in
                  migrate_volume_form.host.element.options]
        if len(values) == 1:
            migrate_volume_form.cancel()
            return cur_host, None

        new_host = values[-1]
        migrate_volume_form.host.element.select_by_visible_text(new_host)

        migrate_volume_form.submit()
        return cur_host, new_host
