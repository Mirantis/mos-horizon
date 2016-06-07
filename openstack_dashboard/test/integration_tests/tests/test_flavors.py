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


class TestFlavors(helpers.AdminTestCase):
    FLAVOR_NAME = helpers.gen_random_resource_name("flavor")

    def flavor_create(self):
        flavors_page = self.home_pg.go_to_system_flavorspage()
        flavors_page.create_flavor(name=self.FLAVOR_NAME, vcpus=1, ram=1024,
                                   root_disk=20, ephemeral_disk=0,
                                   swap_disk=0)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(flavors_page.is_flavor_present(self.FLAVOR_NAME))
        return flavors_page

    def flavor_delete(self, name=None):
        name = name or self.FLAVOR_NAME
        flavors_page = self.home_pg.go_to_system_flavorspage()
        flavors_page.delete_flavor(name)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertFalse(flavors_page.is_flavor_present(name))

    def test_flavor_create(self):
        """tests the flavor creation and deletion functionalities:
        * creates a new flavor
        * verifies the flavor appears in the flavors table
        * deletes the newly created flavor
        * verifies the flavor does not appear in the table after deletion
        """
        self.flavor_create()
        self.flavor_delete()

    def test_flavor_update_metadata(self):
        """Test update flavor metadata
        * logs in as admin user
        * creates a new flavor
        * verifies the flavor appears in the flavors table
        * verifies that Metadata column of the table contains 'No'
        * invokes action 'Update Metadata' for the new flavor
        * adds custom filed 'metadata'
        * adds value 'flavor' for the custom filed 'metadata'
        * verifies that Metadata column of the table is updated to Yes
        * deletes the newly created flavor
        * verifies the flavor does not appear in the table after deletion
        """
        new_metadata = {'metadata1': helpers.gen_random_resource_name("value"),
                        'metadata2': helpers.gen_random_resource_name("value")}
        flavors_page = self.flavor_create()
        self.assertTrue(
            flavors_page.get_metadata_column_value(self.FLAVOR_NAME) == 'No')
        flavors_page.add_custom_metadata(self.FLAVOR_NAME, new_metadata)
        self.assertTrue(
            flavors_page.get_metadata_column_value(self.FLAVOR_NAME) == 'Yes')
        results = flavors_page.check_flavor_metadata(self.FLAVOR_NAME,
                                                     new_metadata)
        self.flavor_delete()
        self.assertSequenceTrue(results)  # custom matcher

    def test_edit_flavor(self):
        new_flavor_name = 'new-' + self.FLAVOR_NAME
        flavors_page = self.flavor_create()

        flavors_page.edit_flavor(name=self.FLAVOR_NAME,
                                 new_name=new_flavor_name)
        self.assertTrue(
            flavors_page.find_message_and_dismiss(messages.SUCCESS))
        self.assertFalse(flavors_page.find_message_and_dismiss(messages.ERROR))
        self.assertTrue(flavors_page.is_flavor_present(new_flavor_name))

        self.flavor_delete(new_flavor_name)
