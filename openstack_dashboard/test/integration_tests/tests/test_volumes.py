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

from openstack_dashboard.test.integration_tests import helpers
from openstack_dashboard.test.integration_tests.regions import messages


class TestVolumes(helpers.TestCase):

    def __init__(self, *args, **kwgs):
        super(TestVolumes, self).__init__(*args, **kwgs)
        self.VOLUME_NAME = helpers.gen_random_resource_name("volume")
        self.IMAGE_NAME = helpers.gen_random_resource_name("image")
        self.INSTANCE_NAME = helpers.gen_random_resource_name("instance")

    @property
    def volumes_page(self):
        return self.home_pg.go_to_compute_volumes_volumespage()

    def test_volume_create_edit_delete(self):
        """This test case checks create, edit, delete volume functionality:
            Steps:
            1. Login to Horizon Dashboard
            2. Navigate to Project -> Compute -> Volumes page
            3. Create new volume
            4. Check that the volume is in the list
            5. Check that no Error messages present
            6. Edit the volume
            7. Check that the volume is still in the list
            8. Check that no Error messages present
            9. Delete the volume via proper page (depends on user)
            10. Check that the volume is absent in the list
            11. Check that no Error messages present
        """
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        new_name = "edited_" + self.VOLUME_NAME
        volumes_page.edit_volume(self.VOLUME_NAME, new_name, "description")
        self.VOLUME_NAME = new_name
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        volumes_page = self.volumes_page
        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))
        # NOTE(tsufiev): A short regression test on bug 1553314: we try to
        # re-open 'Create Volume' button after the volume was deleted. If the
        # regression occurs, the form won't appear (because link is going to be
        # invalid in this case). Give JavaScript callbacks an additional second
        # to do all the job and possibly cause the regression.
        if not isinstance(self, helpers.AdminTestCase):
            time.sleep(1)
            form = volumes_page.volumes_table.create_volume()
            form.cancel()

    def test_delete_volumes(self):
        volume_names = ['{}-{}'.format(self.VOLUME_NAME, i) for i in range(3)]
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()

        for volume_name in volume_names:
            volumes_page.create_volume(volume_name)
            self.assertTrue(
                volumes_page.find_message_and_dismiss(messages.INFO))
            self.assertFalse(
                volumes_page.find_message_and_dismiss(messages.ERROR))
            self.assertTrue(volumes_page.is_volume_present(volume_name))
            self.assertTrue(volumes_page.is_volume_status(volume_name,
                                                          'Available'))

        volume_name = volume_names.pop()
        volumes_page.delete_volumes(volume_name)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(volume_name))

        volumes_page.delete_volumes(*volume_names)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertSequenceTrue(volumes_page.is_volume_deleted(volume_name)
                                for volume_name in volume_names)

    def test_volumes_pagination(self):
        """This test checks volumes pagination
            Steps:
            1) Login to Horizon Dashboard
            2) Go to Project -> Compute -> Volumes -> Volumes tab and create
            three volumes
            3) Navigate to user settings page
            4) Change 'Items Per Page' value to 1
            5) Go to Project -> Compute -> Volumes -> Volumes tab or
            Admin -> System -> Volumes -> Volumes tab (depends on user)
            6) Check that only 'Next' link is available, only one volume is
            available (and it has correct name)
            7) Click 'Next' and check that both 'Prev' and 'Next' links are
            available, only one volume is available (and it has correct name)
            8) Click 'Next' and check that only 'Prev' link is available,
            only one volume is visible (and it has correct name)
            9) Click 'Prev' and check result (should be the same as for step7)
            10) Click 'Prev' and check result (should be the same as for step6)
            11) Go to user settings page and restore 'Items Per Page'
            12) Delete created volumes
        """
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        count = 3
        items_per_page = 1
        volumes_names = ["{0}_{1}".format(self.VOLUME_NAME, i) for i in
                         range(count)]
        for volume_name in volumes_names:
            volumes_page.create_volume(volume_name)
            volumes_page.find_message_and_dismiss(messages.INFO)
            self.assertTrue(volumes_page.is_volume_present(volume_name))

        first_page_definition = {'Next': True, 'Prev': False,
                                 'Count': items_per_page,
                                 'Names': [volumes_names[2]]}
        second_page_definition = {'Next': True, 'Prev': True,
                                  'Count': items_per_page,
                                  'Names': [volumes_names[1]]}
        third_page_definition = {'Next': False, 'Prev': True,
                                 'Count': items_per_page,
                                 'Names': [volumes_names[0]]}
        settings_page = self.home_pg.go_to_settings_usersettingspage()
        settings_page.change_pagesize(items_per_page)
        settings_page.find_message_and_dismiss(messages.SUCCESS)

        volumes_page = self.volumes_page
        volumes_page.volumes_table.assert_definition(first_page_definition)

        volumes_page.volumes_table.turn_next_page()
        volumes_page.volumes_table.assert_definition(second_page_definition)

        volumes_page.volumes_table.turn_next_page()
        volumes_page.volumes_table.assert_definition(third_page_definition)

        volumes_page.volumes_table.turn_prev_page()
        volumes_page.volumes_table.assert_definition(second_page_definition)

        volumes_page.volumes_table.turn_prev_page()
        volumes_page.volumes_table.assert_definition(first_page_definition)

        settings_page = self.home_pg.go_to_settings_usersettingspage()
        settings_page.change_pagesize()
        settings_page.find_message_and_dismiss(messages.SUCCESS)

        volumes_page = self.volumes_page
        for volume_name in volumes_names:
            volumes_page.delete_volume(volume_name)
            volumes_page.find_message_and_dismiss(messages.SUCCESS)
            self.assertTrue(volumes_page.is_volume_deleted(volume_name))

    def test_view_volume(self):
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))
        volumes_page.view_volume(self.VOLUME_NAME)
        assert self.driver.title.startswith(self.VOLUME_NAME)
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))

    def test_change_volume_type(self):
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME, set_type=False)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        volumes_page.set_type(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))

    def test_volume_upload_to_image(self):
        """This test case checks upload volume to image functionality:
            Steps:
            1. Upload volume to image with some disk format
            2. Check that image is created
            3. Check that no Error messages present
            4. Delete the image
            5. Repeat actions for all disk formats
        """
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        all_formats = {"qcow2": u'QCOW2', "raw": u'Raw', "vdi": u'VDI',
                       "vmdk": u'VMDK'}
        for disk_format in all_formats:
            volumes_page.upload_volume_to_image(self.VOLUME_NAME,
                                                self.IMAGE_NAME,
                                                disk_format)
            self.assertFalse(
                volumes_page.find_message_and_dismiss(messages.ERROR))
            self.assertTrue(volumes_page.is_volume_status(
                self.VOLUME_NAME, 'Available'))

            images_page = self.home_pg.go_to_compute_imagespage()
            self.assertTrue(images_page.is_image_present(self.IMAGE_NAME))
            self.assertTrue(images_page.is_image_active(self.IMAGE_NAME))
            self.assertEqual(images_page.get_image_format(self.IMAGE_NAME),
                             all_formats[disk_format])

            images_page.delete_image(self.IMAGE_NAME)
            self.assertTrue(images_page.find_message_and_dismiss(
                messages.SUCCESS))
            self.assertFalse(images_page.find_message_and_dismiss(
                messages.ERROR))
            self.assertFalse(images_page.is_image_present(self.IMAGE_NAME))
            volumes_page = \
                self.home_pg.go_to_compute_volumes_volumespage()

        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))

    def test_volume_extend(self):
        """This test case checks extend volume functionality:
            Steps:
            1. Check current volume size
            2. Extend volume
            3. Check that no Error messages present
            4. Check that the volume is still in the list
            5. Check that the volume size is changed
        """
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        orig_size = volumes_page.get_size(self.VOLUME_NAME)
        volumes_page.extend_volume(self.VOLUME_NAME, orig_size + 1)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))
        new_size = volumes_page.get_size(self.VOLUME_NAME)
        self.assertFalse(orig_size >= new_size)

        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))


class TestAdminVolumes(helpers.AdminTestCase, TestVolumes):

    @property
    def volumes_page(self):
        return self.home_pg.go_to_system_volumes_volumespage()

    def test_change_volume_status(self):
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        volumes_page = self.volumes_page
        volumes_page.update_status(self.VOLUME_NAME, 'Error')
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Error'))

        volumes_page.update_status(self.VOLUME_NAME, 'Available')
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))

    def test_launch_volume_as_instance(self):
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        target_instance = "created_from_{0}".format(self.VOLUME_NAME)
        volumes_page.launch_instance_from_image(self.VOLUME_NAME,
                                                target_instance)
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        instances_page = self.home_pg.go_to_system_instancespage()
        self.assertTrue(instances_page.is_instance_active(target_instance))

        instances_page.delete_instance(target_instance)
        self.assertTrue(
            instances_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            instances_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(instances_page.is_instance_deleted(target_instance))

        volumes_page = self.volumes_page
        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))

    def test_manage_volume_attachments(self):
        """This test case checks attach/detach actions for volume
            Steps:
            1. Login to Horizon Dashboard as horizon user
            2. Navigate to Project -> Compute -> Instances, create instance
            3. Navigate to Project -> Compute -> Volumes, create volume
            4. Attach volume to instance from step2
            5. Check that volume status and link to instance
            6. Detach volume from instance
            7. Check volume status
            8. Delete volume and instance
        """
        instance_name = helpers.gen_random_resource_name('instance')
        instances_page = self.home_pg.go_to_compute_instancespage()
        instances_page.create_instance_ng(instance_name)
        instances_page.find_message_and_dismiss(messages.SUCCESS)
        self.assertFalse(
            instances_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(instances_page.is_instance_active(instance_name))

        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        volumes_page.find_message_and_dismiss(messages.INFO)
        self.assertFalse(volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        volumes_page.attach_volume_to_instance(self.VOLUME_NAME, instance_name)
        volumes_page.find_message_and_dismiss(messages.INFO)
        self.assertFalse(volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'In-use'))
        self.assertTrue(
            volumes_page.is_volume_attached_to_instance(self.VOLUME_NAME,
                                                        instance_name))

        volumes_page.detach_volume_from_instance(self.VOLUME_NAME,
                                                 instance_name)
        volumes_page.find_message_and_dismiss(messages.SUCCESS)
        self.assertFalse(volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        volumes_page.delete_volume(self.VOLUME_NAME)
        volumes_page.find_message_and_dismiss(messages.SUCCESS)
        self.assertFalse(volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))

        instances_page = self.home_pg.go_to_compute_instancespage()
        instances_page.delete_instance(instance_name)
        instances_page.find_message_and_dismiss(messages.SUCCESS)
        self.assertFalse(
            instances_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(instances_page.is_instance_deleted(instance_name))

    def test_transfer_volume(self):
        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        volumes_page.create_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.INFO))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        transfer_name = 'transfered-' + self.VOLUME_NAME
        volume_transfer_form = volumes_page.create_transfer(
            self.VOLUME_NAME, transfer_name)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))

        transfer_id = volume_transfer_form._dynamic_properties['id'].text
        transfer_key = volume_transfer_form.auth_key.text
        volume_transfer_form.cancel()

        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'awaiting-transfer'))

        self.home_pg.log_out()
        self.home_pg = self.login_pg.login(self.DEMO_NAME,
                                           self.DEMO_PASSWORD)
        self.home_pg.change_project(self.DEMO_PROJECT)

        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        self.assertFalse(volumes_page.is_volume_present(self.VOLUME_NAME))

        volumes_page.accept_transfer(transfer_id, transfer_key)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_present(self.VOLUME_NAME))
        self.assertTrue(volumes_page.is_volume_status(self.VOLUME_NAME,
                                                      'Available'))

        self.home_pg.log_out()
        self.home_pg = self.login_pg.login(self.ADMIN_NAME,
                                           self.ADMIN_PASSWORD)
        self.home_pg.change_project(self.ADMIN_PROJECT)

        volumes_page = self.home_pg.go_to_compute_volumes_volumespage()
        self.assertFalse(volumes_page.is_volume_present(self.VOLUME_NAME))

        volumes_page = self.volumes_page
        volumes_page.delete_volume(self.VOLUME_NAME)
        self.assertTrue(
            volumes_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            volumes_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(volumes_page.is_volume_deleted(self.VOLUME_NAME))
