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


class TestUser(helpers.AdminTestCase):

    @property
    def username(self):
        return helpers.gen_random_resource_name("user")

    @property
    def email(self):
        return helpers.gen_random_resource_name("email") + "@localhost"

    @property
    def project_name(self):
        return helpers.gen_random_resource_name("project")

    def test_create_delete_user(self):
        username = self.username

        users_page = self.home_pg.go_to_identity_userspage()
        password = self.TEST_PASSWORD

        users_page.create_user(username, password=password,
                               project='admin', role='admin')
        self.assertTrue(users_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(users_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(users_page.is_user_present(username))

        users_page.delete_user(username)
        self.assertTrue(users_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(users_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(users_page.is_user_present(username))

    def test_edit_user(self):
        username = self.username
        new_username = self.username
        new_email = self.email
        new_project_name = self.project_name

        projects_page = self.home_pg.go_to_identity_projectspage()
        projects_page.create_project(new_project_name)

        self.assertTrue(
            projects_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            projects_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(projects_page.is_project_present(new_project_name))

        users_page = self.home_pg.go_to_identity_userspage()
        users_page.create_user(username, password="user123", project='admin',
                               role='admin')

        self.assertTrue(users_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(users_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(users_page.is_user_present(username))

        users_page.edit_user(username, new_username, new_email,
                             new_project_name)

        self.assertTrue(users_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(users_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(users_page.is_user_present(new_username))

        user_info = users_page.get_user_info(new_username)
        self.assertEqual(user_info['name'], new_username)
        self.assertEqual(user_info['email'], new_email)
        self.assertEqual(user_info['primary_project'], new_project_name)

        users_page.delete_user(new_username)

        self.assertTrue(users_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(users_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(users_page.is_user_present(new_username))

        projects_page = self.home_pg.go_to_identity_projectspage()
        projects_page.delete_project(new_project_name)

        self.assertTrue(
            projects_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            projects_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(projects_page.is_project_present(new_project_name))
