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

from os import path
from time import sleep

import requests

from openstack_dashboard.test.integration_tests import helpers
from openstack_dashboard.test.integration_tests.regions import messages


class TestContainers(helpers.TestCase):

    def __init__(self, *args, **kwgs):
        super(TestContainers, self).__init__(*args, **kwgs)
        self.container_name = helpers.gen_random_resource_name("container")
        self.folder_name = helpers.gen_random_resource_name("folder")

    def setUp(self):
        super(TestContainers, self).setUp()
        self.containers_page = self.home_pg.go_to_objectstore_containerspage()

    def test_create_private_container(self):
        self.containers_page.create_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_present(self.container_name))

        self.containers_page.choose_container(self.container_name)
        self.assertTrue(self.containers_page.has_details(self.container_name))

        self.containers_page.delete_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_deleted(self.container_name))

    def test_create_public_container(self):
        self.containers_page.create_container(self.container_name, public=True)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_present(self.container_name))

        self.containers_page.choose_container(self.container_name)
        self.assertTrue(self.containers_page.has_details(self.container_name))

        self.containers_page.delete_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_deleted(self.container_name))

    def test_available_public_container_url(self):
        self.containers_page.create_container(self.container_name, public=True)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_present(self.container_name))

        self.containers_page.choose_container(self.container_name)

        self.containers_page.create_folder(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_present(self.folder_name))

        link = self.containers_page.get_public_container_link(
            self.container_name)
        self.assertTrue(self.folder_name in requests.get(link).text)

        self.containers_page.delete_object(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_deleted(self.folder_name))

        self.containers_page.delete_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_deleted(self.container_name))

    def test_upload_file(self):
        self.containers_page.create_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_present(self.container_name))

        self.containers_page.choose_container(self.container_name)

        with helpers.gen_temporary_file(size=1024*1024) as file_path:
            file_name = path.basename(file_path)

            self.containers_page.upload_file(file_path)
            self.assertTrue(self.containers_page.find_message_and_dismiss(
                messages.SUCCESS))
            self.assertFalse(
                self.containers_page.find_message_and_dismiss(messages.ERROR))
            self.assertTrue(self.containers_page.is_object_present(file_name))

            self.containers_page.delete_object(file_name)
            self.assertTrue(self.containers_page.find_message_and_dismiss(
                messages.SUCCESS))
            self.assertFalse(
                self.containers_page.find_message_and_dismiss(messages.ERROR))
            self.assertTrue(self.containers_page.is_object_deleted(file_name))
            sleep(5)  # be sure file is deleted at backend

        self.containers_page.delete_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_deleted(self.container_name))

    def test_create_folder(self):
        self.containers_page.create_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_present(self.container_name))

        self.containers_page.choose_container(self.container_name)

        self.containers_page.create_folder(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_present(self.folder_name))

        self.containers_page.delete_object(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_deleted(self.folder_name))

        self.containers_page.delete_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_deleted(self.container_name))

    def test_upload_file_to_folder(self):
        self.containers_page.create_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_present(self.container_name))

        self.containers_page.choose_container(self.container_name)

        self.containers_page.create_folder(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_present(self.folder_name))

        self.containers_page.choose_folder(self.folder_name)

        with helpers.gen_temporary_file(size=1024*1024) as file_path:
            file_name = path.basename(file_path)

            self.containers_page.upload_file(file_path)
            self.assertTrue(self.containers_page.find_message_and_dismiss(
                messages.SUCCESS))
            self.assertFalse(
                self.containers_page.find_message_and_dismiss(messages.ERROR))
            self.assertTrue(self.containers_page.is_object_present(file_name))

            self.containers_page.delete_object(file_name)
            self.assertTrue(self.containers_page.find_message_and_dismiss(
                messages.SUCCESS))
            self.assertFalse(
                self.containers_page.find_message_and_dismiss(messages.ERROR))
            self.assertTrue(self.containers_page.is_object_deleted(file_name))
            sleep(5)  # be sure file is deleted at backend

        self.containers_page.choose_container(self.container_name)
        self.containers_page.delete_object(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_deleted(self.folder_name))

        self.containers_page.delete_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_deleted(self.container_name))


class TestAdminContainers(helpers.AdminTestCase, TestContainers):
    pass
