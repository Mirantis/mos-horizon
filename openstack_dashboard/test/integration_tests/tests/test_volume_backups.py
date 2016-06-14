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

from openstack_dashboard.test.integration_tests import helpers
from openstack_dashboard.test.integration_tests.regions import messages


class TestVolumeBackups(helpers.TestCase):
    """Login as demo user"""
    VOLUME_NAME = helpers.gen_random_resource_name("volume")
    VOLUME_BACKUP_NAME = helpers.gen_random_resource_name("volume_backup")

    def setUp(self):
        """Setup: create volume"""
        super(TestVolumeBackups, self).setUp()
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        volumes_page.find_message_and_dismiss(messages.INFO)
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        def cleanup():
            volumes_backup_page = \
                self.home_pg.go_to_compute_volumes_volumebackupspage()
            volumes_page = volumes_backup_page.switch_to_volumes_tab()
            volumes_page.delete_volume(self.VOLUME_NAME)
            volumes_page.find_message_and_dismiss(messages.SUCCESS)
            self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))

        self.addCleanup(cleanup)

    def test_volume_backups_pagination(self):
        """This test checks volumes backups pagination
            Steps:
            1) Login to Horizon Dashboard
            2) Go to Project -> Compute -> Volumes -> Volumes tab, create
            volumes and 3 backups
            3) Navigate to user settings page
            4) Change 'Items Per Page' value to 1
            5) Go to Project -> Compute -> Volumes -> Volumes Snapshot tab
            or Admin -> System -> Volumes -> Volumes Snapshot tab
            (depends on user)
            6) Check that only 'Next' link is available, only one backup is
            available (and it has correct name)
            7) Click 'Next' and check that both 'Prev' and 'Next' links are
            available, only one backup is available (and it has correct name)
            8) Click 'Next' and check that only 'Prev' link is available,
            only one backup is visible (and it has correct name)
            9) Click 'Prev' and check result (should be the same as for step7)
            10) Click 'Prev' and check result (should be the same as for step6)
            11) Go to user settings page and restore 'Items Per Page'
            12) Delete created backups and volumes
        """
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        count = 3
        items_per_page = 1
        backup_names = ["{0}_{1}".format(self.VOLUME_BACKUP_NAME, i) for i
                        in range(count)]
        for i, name in enumerate(backup_names):
            volumes_backup_page = volumes_page.create_volume_backup(
                self.VOLUME_NAME, name)
            volumes_page.find_message_and_dismiss(messages.INFO)
            self.assertTrue(
                volumes_backup_page.is_volume_backup_available(name))
            if i < count - 1:
                volumes_backup_page.switch_to_volumes_tab()

        first_page_definition = {'Next': True, 'Prev': False,
                                 'Count': items_per_page,
                                 'Names': [backup_names[2]]}
        second_page_definition = {'Next': True, 'Prev': True,
                                  'Count': items_per_page,
                                  'Names': [backup_names[1]]}
        third_page_definition = {'Next': False, 'Prev': True,
                                 'Count': items_per_page,
                                 'Names': [backup_names[0]]}

        settings_page = self.home_pg.go_to_settings_usersettingspage()
        settings_page.change_pagesize(items_per_page)
        settings_page.find_message_and_dismiss(messages.SUCCESS)

        volumes_backup_page = self.home_pg \
            .go_to_compute_volumes_volumebackupspage()
        volumes_backup_page.volumebackups_table.assert_definition(
            first_page_definition)

        volumes_backup_page.volumebackups_table.turn_next_page()
        volumes_backup_page.volumebackups_table.assert_definition(
            second_page_definition)

        volumes_backup_page.volumebackups_table.turn_next_page()
        volumes_backup_page.volumebackups_table.assert_definition(
            third_page_definition)

        volumes_backup_page.volumebackups_table.turn_prev_page()
        volumes_backup_page.volumebackups_table.assert_definition(
            second_page_definition)

        volumes_backup_page.volumebackups_table.turn_prev_page()
        volumes_backup_page.volumebackups_table.assert_definition(
            first_page_definition)

        settings_page = self.home_pg.go_to_settings_usersettingspage()
        settings_page.change_pagesize()
        settings_page.find_message_and_dismiss(messages.SUCCESS)

        volumes_backup_page = self.home_pg \
            .go_to_compute_volumes_volumebackupspage()
        volumes_backup_page.delete_volume_backups(backup_names)
        volumes_backup_page.find_message_and_dismiss(messages.SUCCESS)
        for name in backup_names:
            volumes_backup_page.is_volume_backup_deleted(name)


class TestAdminVolumeBackups(helpers.AdminTestCase, TestVolumeBackups):

    VOLUME_NAME = helpers.gen_random_resource_name("volume")
    VOLUME_BACKUP_NAME = helpers.gen_random_resource_name("volume_backup")
