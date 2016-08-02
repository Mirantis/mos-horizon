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

import time

from selenium.webdriver.common import by

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms
from openstack_dashboard.test.integration_tests.regions import menus
from openstack_dashboard.test.integration_tests.regions import tables


class InstanceFormNG(forms.TabbedFormRegionNG):
    field_mappings = ({"name": "name",
                       "availability_zone": "availability-zone",
                       "instance_count": "count"},
                      ({"boot_source_type": "boot-source-type",
                        "vol_create": "vol-create",
                        'boot_sources': menus.TransferTableMenuRegion}),
                      ({'flavors': menus.TransferTableMenuRegion}),
                      ({'networks': menus.TransferTableMenuRegion}))

    def __init__(self, driver, conf):
        super(InstanceFormNG, self).__init__(
            driver, conf, field_mappings=self.field_mappings)
        # TODO(schipiga): need lazy machanism to get form fields dinamically.
        time.sleep(5)  # wait fields initialization


class InstancesTable(tables.TableRegion):
    name = "instances"
    CREATE_INSTANCE_FORM_FIELDS = ((
        "availability_zone", "name", "flavor",
        "count", "source_type", "instance_snapshot_id",
        "volume_id", "volume_snapshot_id", "image_id", "volume_size",
        "vol_delete_on_instance_delete"),
        ("keypair", "groups"),
        ("script_source", "script_upload", "script_data"),
        ("disk_config", "config_drive")
    )
    RESIZE_INSTANCE_FORM_FIELDS = (("old_flavor_name", "flavor"),
                                   "disk_config")
    CREATE_SNAPSHOT_FORM_FIELDS = ("name", )

    @tables.bind_table_action('launch')
    def launch_instance(self, launch_button):
        launch_button.click()
        return forms.TabbedFormRegion(
            self.driver, self.conf,
            field_mappings=self.CREATE_INSTANCE_FORM_FIELDS)

    @tables.bind_table_action('launch-ng')
    def launch_instance_ng(self, launch_button):
        launch_button.click()
        return InstanceFormNG(self.driver, self.conf)

    @tables.bind_table_action('delete')
    def delete_instances(self, delete_button):
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('delete')
    def delete_instance(self, delete_button, row):
        delete_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('lock')
    def lock_instance(self, lock_button, row):
        lock_button.click()

    @tables.bind_row_action('unlock')
    def unlock_instance(self, unlock_button, row):
        unlock_button.click()

    @tables.bind_row_action('soft_reboot')
    def soft_reboot_instance(self, soft_reboot_button, row):
        soft_reboot_button.click()
        return forms.BaseFormRegion(self.driver, self.conf)

    @tables.bind_row_action('snapshot')
    def create_instance_snapshot(self, create_snapshot_button, row):
        create_snapshot_button.click()
        return forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.CREATE_SNAPSHOT_FORM_FIELDS)

    @tables.bind_row_action('resize')
    def resize_instance(self, resize_instance_button, row):
        resize_instance_button.click()
        return forms.TabbedFormRegion(
            self.driver, self.conf,
            field_mappings=self.RESIZE_INSTANCE_FORM_FIELDS)

    @tables.bind_row_action('confirm')
    def confirm_resize_instance(self, confirm_resize_button, row):
        confirm_resize_button.click()

    @tables.bind_row_action('revert')
    def revert_resize_instance(self, revert_resize_button, row):
        revert_resize_button.click()


class InstancesPage(basepage.BaseNavigationPage):

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
    INSTANCES_TABLE_SIZE_COLUMN = 'size'

    DEFAULT_BOOT_SOURCE_NG = 'image'
    DEFAULT_VOLUME_CREATION_NG = 'No'
    DEFAULT_BOOT_SOURCE_NAME_NG = 'TestVM'
    DEFAULT_NETWORK_NG = "admin_internal_net"

    def __init__(self, driver, conf):
        super(InstancesPage, self).__init__(driver, conf)
        self._page_title = "Instances"

    def _get_row_with_instance_name(self, name):
        return self.instances_table.get_row(self.INSTANCES_TABLE_NAME_COLUMN,
                                            name)

    @property
    def instances_table(self):
        return InstancesTable(self.driver, self.conf)

    def is_instance_present(self, name):
        return bool(self._get_row_with_instance_name(name))

    def create_instance(
            self, instance_name,
            available_zone=None,
            instance_count=DEFAULT_COUNT,
            flavor=DEFAULT_FLAVOR,
            boot_source=DEFAULT_BOOT_SOURCE,
            source_name=None,
            device_size=None,
            vol_delete_on_instance_delete=DEFAULT_VOL_DELETE_ON_INSTANCE_DELETE
    ):
        if not available_zone:
            available_zone = self.conf.launch_instances.available_zone
        instance_form = self.instances_table.launch_instance()
        instance_form.availability_zone.value = available_zone
        instance_form.name.text = instance_name
        instance_form.flavor.text = flavor
        instance_form.count.value = instance_count
        instance_form.source_type.text = boot_source
        boot_source = self._get_source_name(instance_form, boot_source,
                                            self.conf.launch_instances)
        if not source_name:
            source_name = boot_source[1]
        boot_source[0].text = source_name
        if device_size:
            instance_form.volume_size.value = device_size
        if vol_delete_on_instance_delete:
            instance_form.vol_delete_on_instance_delete.mark()
        instance_form.submit()

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
        instance_form.name.text = name
        instance_form.availability_zone.text = availability_zone
        instance_form.instance_count.value = instance_count

        instance_form.switch_to(1)
        instance_form.boot_source_type = boot_source_type
        instance_form.vol_create.text = vol_create
        instance_form.boot_sources.allocate_item(name=image_name)

        instance_form.switch_to(2)
        instance_form.flavors.allocate_item(name=flavor_size)

        instance_form.switch_to(3)
        instance_form.networks.allocate_item(name=network)
        instance_form.submit()

    def view_instance(self, name):
        row = self._get_row_with_instance_name(name)
        name_link = row.cells['name'].find_element(by.By.CSS_SELECTOR, 'a')
        name_link.click()

    def view_log_instance(self, name):
        self.view_instance(name)
        log_link = self.driver.find_element_by_css_selector(
            'a[href="?tab=instance_details__log"]')
        log_link.click()
        self.wait_till_spinner_disappears()

    def view_console_instance(self, name):
        self.view_instance(name)
        console_link = self.driver.find_element_by_css_selector(
            'a[href="?tab=instance_details__console"]')
        console_link.click()
        self.wait_till_spinner_disappears()

    def lock_instance(self, name):
        row = self._get_row_with_instance_name(name)
        self.instances_table.lock_instance(row)

    def unlock_instance(self, name):
        row = self._get_row_with_instance_name(name)
        self.instances_table.unlock_instance(row)

    def delete_instance(self, name):
        row = self._get_row_with_instance_name(name)
        confirm_delete_form = self.instances_table.delete_instance(row)
        confirm_delete_form.submit()

    def delete_instances(self, *names):
        for name in names:
            self._get_row_with_instance_name(name).mark()
        confirm_delete_instances_form = self.instances_table.delete_instances()
        confirm_delete_instances_form.submit()

    def is_instance_deleted(self, name):
        return self.instances_table.is_row_deleted(
            lambda: self._get_row_with_instance_name(name))

    def is_instance_active(self, name):
        def cell_getter():
            row = self._get_row_with_instance_name(name)
            return row and row.cells[self.INSTANCES_TABLE_STATUS_COLUMN]

        status = self.instances_table.wait_cell_status(cell_getter,
                                                       ('Active', 'Error'))
        return status == 'Active'

    def soft_reboot(self, name):
        row = self._get_row_with_instance_name(name)
        confirm__form = self.instances_table.soft_reboot_instance(row)
        confirm__form.submit()

    def create_snapshot(self, name, snapshot_name):
        row = self._get_row_with_instance_name(name)
        create_form = self.instances_table.create_instance_snapshot(row)
        create_form.name.text = snapshot_name
        create_form.submit()

    def resize_instance(self, name, new_flavor):
        row = self._get_row_with_instance_name(name)
        resize_form = self.instances_table.resize_instance(row)
        resize_form.flavor.text = new_flavor
        resize_form.submit()

    def is_instance_rebooting(self, name):
        def cell_getter():
            row = self._get_row_with_instance_name(name)
            return row and row.cells[self.INSTANCES_TABLE_STATUS_COLUMN]

        status = self.instances_table.wait_cell_status(cell_getter,
                                                       ('Reboot', 'Error'))
        return status == 'Reboot'

    def is_instance_resizing(self, name):
        def cell_getter():
            row = self._get_row_with_instance_name(name)
            return row and row.cells[self.INSTANCES_TABLE_STATUS_COLUMN]

        status = self.instances_table.wait_cell_status(
            cell_getter, ("Confirm or Revert Resize/Migrate", "Error"))
        return status == "Confirm or Revert Resize/Migrate"

    def confirm_resize(self, name):
        row = self._get_row_with_instance_name(name)
        self.instances_table.confirm_resize_instance(row)

    def revert_resize(self, name):
        row = self._get_row_with_instance_name(name)
        self.instances_table.revert_resize_instance(row)

    def is_size_correct(self, instance_name, size):
        def cell_getter():
            row = self._get_row_with_instance_name(instance_name)
            return row and row.cells[self.INSTANCES_TABLE_SIZE_COLUMN]

        actual_size = self.instances_table.wait_cell_status(cell_getter, size)
        return actual_size == size

    def _get_source_name(self, instance, boot_source,
                         conf):
        if 'image' in boot_source:
            return instance.image_id, conf.image_name
        elif boot_source == 'Boot from volume':
            return instance.volume_id, self.DEFAULT_VOLUME_NAME
        elif boot_source == 'Boot from snapshot':
            return instance.instance_snapshot_id, self.DEFAULT_SNAPSHOT_NAME
        elif 'volume snapshot (creates a new volume)' in boot_source:
            return (instance.volume_snapshot_id,
                    self.DEFAULT_VOLUME_SNAPSHOT_NAME)

    def get_image_name(self, instance_name):
        row = self._get_row_with_instance_name(instance_name)
        return row.cells[self.INSTANCES_TABLE_IMAGE_NAME_COLUMN].text

    def get_fixed_ipv4(self, name):
        row = self._get_row_with_instance_name(name)
        ips = row.cells[self.INSTANCES_TABLE_IP_COLUMN].text
        return ips.split()[0]
