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

import logging

from openstack_dashboard.test.integration_tests.pages import loginpage
from openstack_dashboard.test.integration_tests.regions import messages

LOGGER = logging.getLogger(__name__)


def login(test_case):
    test_case.login_pg = loginpage.LoginPage(test_case.driver,
                                             test_case.CONFIG)
    test_case.login_pg.go_to_login_page()

    # test_case.create_demo_user()

    test_case.home_pg = test_case.login_pg.login(test_case.TEST_USER_NAME,
                                                 test_case.TEST_PASSWORD)
    test_case.home_pg.change_project(test_case.HOME_PROJECT)
    test_case.assertTrue(
        test_case.home_pg.find_message_and_dismiss(messages.SUCCESS))
    test_case.assertFalse(
        test_case.home_pg.find_message_and_dismiss(messages.ERROR))

    yield

    if test_case.home_pg.is_logged_in:
        test_case.home_pg.log_out()
    else:
        LOGGER.warn("{!r} isn't logged in".format(test_case.TEST_USER_NAME))
