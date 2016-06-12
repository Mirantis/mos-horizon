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


class TestDefaults(helpers.AdminTestCase):

    def setUp(self):
        super(TestDefaults, self).setUp()
        self.defaults_page = self.home_pg.go_to_system_defaultspage()

    def test_update_defaults(self):
        volumes_quota = self.defaults_page.get_volumes_quota()
        new_volumes_quota = volumes_quota + "0"
        self.defaults_page.set_volumes_quota(new_volumes_quota)
        self.assertTrue(
            self.defaults_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.defaults_page.find_message_and_dismiss(messages.ERROR))
        self.assertEqual(self.defaults_page.get_volumes_quota(),
                         new_volumes_quota)

        self.defaults_page.set_volumes_quota(volumes_quota)
        self.assertTrue(
            self.defaults_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(
            self.defaults_page.find_message_and_dismiss(messages.ERROR))
        self.assertEqual(self.defaults_page.get_volumes_quota(),
                         volumes_quota)
