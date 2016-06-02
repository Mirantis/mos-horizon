# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import contextlib
from functools import wraps
import logging
import os
import tempfile
import time
import traceback
import types
import uuid

from selenium.webdriver.remote.remote_connection import RemoteConnection
import testtools

from openstack_dashboard.test.integration_tests import config
from openstack_dashboard.test.integration_tests import fixtures
from openstack_dashboard.test.integration_tests import steps
from openstack_dashboard.test.integration_tests import utils

try:
    from unittest2.case import SkipTest
except ImportError:
    from unittest.case import SkipTest

LOGGER = logging.getLogger(__name__)
ROOT_PATH = os.path.dirname(os.path.abspath(config.__file__))
RemoteConnection.set_timeout(60)


def gen_random_resource_name(resource="", timestamp=True):
    """Generate random resource name using uuid and timestamp.

    Input fields are usually limited to 255 or 80 characters hence their
    provide enough space for quite long resource names, but it might be
    the case that maximum field length is quite restricted, it is then
    necessary to consider using shorter resource argument or avoid using
    timestamp by setting timestamp argument to False.
    """
    fields = ["horizon"]
    if resource:
        fields.append(resource)
    if timestamp:
        tstamp = time.strftime("%d-%m-%H-%M-%S")
        fields.append(tstamp)
    fields.append(str(uuid.uuid4()).replace("-", ""))
    return "_".join(fields)


@contextlib.contextmanager
def gen_temporary_file(name='', suffix='.qcow2', size=10485760):
    """Generate temporary file with provided parameters.

    :param name: file name except the extension /suffix
    :param suffix: file extension/suffix
    :param size: size of the file to create, bytes are generated randomly
    :return: path to the generated file
    """
    with tempfile.NamedTemporaryFile(prefix=name, suffix=suffix) as tmp_file:
        tmp_file.write(os.urandom(size))
        yield tmp_file.name


class AssertsMixin(object):

    def assertSequenceTrue(self, actual):
        return self.assertEqual(list(actual), [True] * len(actual))

    def assertSequenceFalse(self, actual):
        return self.assertEqual(list(actual), [False] * len(actual))


class BaseTestCase(testtools.TestCase, AssertsMixin):

    CONFIG = config.get_config()

    def __init__(self, *args, **kwgs):
        super(BaseTestCase, self).__init__(*args, **kwgs)
        self.is_failed = False
        self.addOnException(lambda exc_info: setattr(self, 'is_failed', True))

    def inject(self, func, *args, **kwgs):
        result = obj = func(*args, **kwgs)
        if isinstance(obj, types.GeneratorType):
            result = obj.next()

            def cleanup():
                try:
                    obj.next()
                except StopIteration:
                    pass

            self.addCleanup(cleanup)
        return result

    def addOnException(self, exception_handler):

        @wraps(exception_handler)
        def wrapped_handler(exc_info):
            if issubclass(exc_info[0], SkipTest):
                return
            return exception_handler(exc_info)

        super(BaseTestCase, self).addOnException(wrapped_handler)

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.inject(fixtures.logger, self)

        if utils.IS_SELENIUM_HEADLESS:
            self.inject(fixtures.vdisplay)

        self.inject(fixtures.video_recorder, self)
        self.driver = self.inject(fixtures.web_driver, self)

        self.addOnException(self._attach_page_source)
        self.addOnException(self._attach_screenshot)

    @property
    def _test_report_dir(self):
        report_dir = os.path.join(ROOT_PATH, 'test_reports',
                                  '{}.{}'.format(self.__class__.__name__,
                                                 self._testMethodName))
        if not os.path.isdir(report_dir):
            os.makedirs(report_dir)
        return report_dir

    def _attach_page_source(self, exc_info):
        source_path = os.path.join(self._test_report_dir, 'page.html')
        with self.log_exception("Attach page source"):
            with open(source_path, 'w') as f:
                f.write(self._get_page_html_source())

    def _attach_screenshot(self, exc_info):
        screen_path = os.path.join(self._test_report_dir, 'screenshot.png')
        with self.log_exception("Attach screenshot"):
            self.driver.get_screenshot_as_file(screen_path)

    @contextlib.contextmanager
    def log_exception(self, label):
        try:
            yield
        except Exception:
            self.addDetail(
                label, testtools.content.text_content(traceback.format_exc()))

    @staticmethod
    def _unwrap_browser_log(_log):
        def rec(log):
            if isinstance(log, dict):
                return log['message'].encode('utf-8')
            elif isinstance(log, list):
                return '\n'.join([rec(item) for item in log])
            else:
                return log.encode('utf-8')
        return rec(_log)

    def _get_page_html_source(self):
        """Gets html page source.

        self.driver.page_source is not used on purpose because it does not
        display html code generated/changed by javascript.
        """
        html_elem = self.driver.find_element_by_tag_name("html")
        return html_elem.get_attribute("innerHTML").encode("utf-8")


class TestCase(BaseTestCase):

    ADMIN_NAME = BaseTestCase.CONFIG.identity.admin_username
    ADMIN_PASSWORD = BaseTestCase.CONFIG.identity.admin_password
    ADMIN_PROJECT = BaseTestCase.CONFIG.identity.admin_home_project

    DEMO_NAME = BaseTestCase.CONFIG.identity.username
    DEMO_PASSWORD = BaseTestCase.CONFIG.identity.password
    DEMO_PROJECT = BaseTestCase.CONFIG.identity.home_project

    TEST_USER_NAME = BaseTestCase.CONFIG.identity.username
    TEST_PASSWORD = BaseTestCase.CONFIG.identity.password
    HOME_PROJECT = BaseTestCase.CONFIG.identity.home_project

    def setUp(self):
        super(TestCase, self).setUp()
        self.inject(steps.login, self)

    @utils.once_only
    def create_demo_user(self):
        self.home_pg = self.login_pg.login(self.ADMIN_NAME,
                                           self.ADMIN_PASSWORD)
        self.home_pg.change_project(self.ADMIN_PROJECT)

        projects_page = self.home_pg.go_to_identity_projectspage()
        if not projects_page.is_project_present(self.DEMO_PROJECT):
            projects_page.create_project(self.DEMO_PROJECT)

        users_page = self.home_pg.go_to_identity_userspage()
        if users_page.is_user_present(self.DEMO_NAME):
            users_page.delete_user(self.DEMO_NAME)
        users_page.create_user(self.DEMO_NAME, password=self.DEMO_PASSWORD,
                               project=self.DEMO_PROJECT, role='_member_')

        if self.home_pg.is_logged_in:
            self.home_pg.go_to_home_page()
            self.home_pg.log_out()


class AdminTestCase(TestCase):

    TEST_USER_NAME = TestCase.CONFIG.identity.admin_username
    TEST_PASSWORD = TestCase.CONFIG.identity.admin_password
    HOME_PROJECT = BaseTestCase.CONFIG.identity.admin_home_project
