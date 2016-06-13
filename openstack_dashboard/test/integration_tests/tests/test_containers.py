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

from nose import with_setup
import requests

from openstack_dashboard.test.integration_tests import helpers
from openstack_dashboard.test.integration_tests.regions import messages


class TestContainers(helpers.TestCase):

    def setUp(self):
        super(TestContainers, self).setUp()
        self.container_name = helpers.gen_random_resource_name("container")
        self.folder_name = helpers.gen_random_resource_name("folder")
        self.containers_page = self.home_pg.go_to_objectstore_containerspage()
        getattr(self, self._testMethodName).setup(self)

    def setup(self):
        self._create_container()
        self.addCleanup(self._delete_container)

    @with_setup(setup)
    def test_view_private_container(self):
        self._choose_container()

    @with_setup(setup)
    def test_upload_file(self):
        self._choose_container()
        with helpers.gen_temporary_file(size=1024 * 1024) as file_path:
            self._upload_file(file_path)
            self._delete_file(path.basename(file_path))

    def setup(self):
        self._create_container(public=True)
        self.addCleanup(self._delete_container)

    @with_setup(setup)
    def test_view_public_container(self):
        self._choose_container()

    def setup_folder(self):
        self.setup()
        self._choose_container()
        self._create_folder()
        self.addCleanup(self._delete_folder)

    @with_setup(setup_folder)
    def test_available_public_container_url(self):
        link = self.containers_page.get_public_container_link(
            self.container_name)
        self.assertTrue(self.folder_name in requests.get(link).text)

    @with_setup(setup_folder)
    def test_upload_file_to_folder(self):
        self.containers_page.choose_folder(self.folder_name)
        with helpers.gen_temporary_file(size=1024 * 1024) as file_path:
            self._upload_file(file_path)
            self._delete_file(path.basename(file_path))
        self._choose_container()

    # steps
    def _create_container(self, public=False):
        self.containers_page.create_container(self.container_name, public)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_present(self.container_name))

    def _delete_container(self):
        self.containers_page.delete_container(self.container_name)
        self.assertTrue(
            self.containers_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_container_deleted(self.container_name))

    def _choose_container(self):
        self.containers_page.choose_container(self.container_name)
        self.assertTrue(self.containers_page.has_details(self.container_name))

    def _create_folder(self):
        self.containers_page.create_folder(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_present(self.folder_name))

    def _delete_folder(self):
        self.containers_page.delete_object(self.folder_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_deleted(self.folder_name))

    def _upload_file(self, file_path):
        self.containers_page.upload_file(file_path)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(
            self.containers_page.is_object_present(path.basename(file_path)))

    def _delete_file(self, file_name):
        self.containers_page.delete_object(file_name)
        self.assertTrue(self.containers_page.find_message_and_dismiss(
            messages.SUCCESS))
        self.assertFalse(
            self.containers_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(self.containers_page.is_object_deleted(file_name))
        sleep(5)  # be sure file is deleted at backend


class TestAdminContainers(helpers.AdminTestCase, TestContainers):
    pass
