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

from selenium.webdriver.common import by

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.pages.project.compute.volumes.\
    volumespage import VolumesPage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import tables


class VolumebackupsTable(tables.TableRegion):
    name = 'volume_backups'
    marker_name = 'backup_marker'
    prev_marker_name = 'prev_backup_marker'

    EDIT_BACKUP_FORM_FIELDS = ("name", "description", "container_name")

    CREATE_VOLUME_FORM_FIELDS = (
        "name", "description", "backup_source", "type", "size")

    @tables.bind_table_action('delete')
    def delete_volume_backups(self, delete_button):
        """Batch Delete table action."""
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('delete')
    def delete_volume_backup(self, delete_button, row):
        """Per-entity delete row action."""
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('edit')
    def edit_backup(self, edit_button, row):
        edit_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.EDIT_BACKUP_FORM_FIELDS)

    @tables.bind_row_action('create_from_backup')
    def create_volume(self, create_volume_button, row):
        create_volume_button.click()
        return forms.FormRegion(self.driver, self.conf,
                                field_mappings=self.CREATE_VOLUME_FORM_FIELDS)


class VolumebackupsPage(basepage.BaseNavigationPage):
    BACKUP_TABLE_NAME_COLUMN = 'name'
    BACKUP_TABLE_STATUS_COLUMN = 'status'
    BACKUP_TABLE_VOLUME_NAME_COLUMN = 'volume_name'
    _volumes_tab_locator = (
        by.By.CSS_SELECTOR,
        'a[href*="tab=volumes_and_snapshots__volumes_tab"]')

    def __init__(self, driver, conf):
        super(VolumebackupsPage, self).__init__(driver, conf)
        self._page_title = "Volumes"

    @property
    def volumebackups_table(self):
        return VolumebackupsTable(self.driver, self.conf)

    def switch_to_volumes_tab(self):
        self._get_element(*self._volumes_tab_locator).click()
        return VolumesPage(self.driver, self.conf)

    def _get_row_with_volume_backup_name(self, name):
        return self.volumebackups_table.get_row(
            self.BACKUP_TABLE_NAME_COLUMN,
            name)

    def is_backup_present(self, name):
        return bool(self._get_row_with_volume_backup_name(name))

    def delete_volume_backup(self, name):
        row = self._get_row_with_volume_backup_name(name)
        confirm_form = self.volumebackups_table.delete_volume_backup(row)
        confirm_form.submit()

    def delete_volume_backups(self, names):
        for name in names:
            row = self._get_row_with_volume_backup_name(name)
            row.mark()
        confirm_form = self.volumebackups_table.delete_volume_backups()
        confirm_form.submit()

    def is_volume_backup_deleted(self, name):
        return self.volumebackups_table.is_row_deleted(
            lambda: self._get_row_with_volume_backup_name(name))

    def is_volume_backup_available(self, name):
        row = self._get_row_with_volume_backup_name(name)
        return bool(self.volumebackups_table.wait_cell_status(
            lambda: row and row.cells[self.BACKUP_TABLE_STATUS_COLUMN],
            'Available'))

    def get_volume_name(self, backup_name):
        row = self._get_row_with_volume_backup_name(backup_name)
        return row.cells[self.BACKUP_TABLE_VOLUME_NAME_COLUMN].text

    def edit_backup(self, name, new_name=None, description=None):
        row = self._get_row_with_volume_backup_name(name)
        backup_edit_form = self.volumebackups_table.edit_backup(row)
        if new_name:
            backup_edit_form.name.text = new_name
        if description:
            backup_edit_form.description.text = description
        backup_edit_form.submit()

    def create_volume_from_backup(self, backup_name, volume_name=None,
                                  description=None, volume_size=None):
        row = self._get_row_with_volume_backup_name(backup_name)
        volume_form = self.volumebackups_table.create_volume(row)
        if volume_name:
            volume_form.name.text = volume_name
        if description:
            volume_form.description.text = description
        if volume_size is None:
            volume_size = self.conf.volume.volume_size
        volume_form.size.value = volume_size
        volume_form.submit()
