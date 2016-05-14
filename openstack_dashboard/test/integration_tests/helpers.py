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
import logging
import os
from shutil import copyfile
from six import StringIO
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

ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(logging.DEBUG)
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


class AssertsMixin(object):

    def assertSequenceTrue(self, actual):
        return self.assertEqual(list(actual), [True] * len(actual))

    def assertSequenceFalse(self, actual):
        return self.assertEqual(list(actual), [False] * len(actual))


class BaseTestCase(testtools.TestCase, AssertsMixin):

    CONFIG = config.get_config()

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

    def setUp(self):
        self._configure_log()

        # TODO(schipiga): remove that code. Launch logic must be above.
        if not os.environ.get('INTEGRATION_TESTS', False):
            raise self.skipException(
                "The INTEGRATION_TESTS env variable is not set.")

        # Start a virtual display server for running the tests headless.
        if utils.IS_SELENIUM_HEADLESS:
            self.vdisplay = self.inject(fixtures.vdisplay)

        self.video_recorder = self.inject(fixtures.video_recorder)
        self.driver = self.inject(fixtures.web_driver)

        self.addOnException(self._attach_page_source)
        self.addOnException(self._attach_screenshot)
        self.addOnException(self._attach_video)
        self.addOnException(self._attach_browser_log)
        self.addOnException(self._attach_test_log)

        super(BaseTestCase, self).setUp()

    def _configure_log(self):
        """Configure log to capture test logs include selenium logs in order
        to attach them if test will be broken.
        """
        ROOT_LOGGER.handlers[:] = []  # clear other handlers to set target handler
        self._log_buffer = StringIO()
        stream_handler = logging.StreamHandler(stream=self._log_buffer)
        stream_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        ROOT_LOGGER.addHandler(stream_handler)

    @property
    def _test_report_dir(self):
        report_dir = os.path.join(ROOT_PATH, 'test_reports',
                                  '{}.{}'.format(self.__class__.__name__,
                                                 self._testMethodName))
        if not os.path.isdir(report_dir):
            os.makedirs(report_dir)
        return report_dir

    @utils.ignore_skip
    def _attach_page_source(self, exc_info):
        source_path = os.path.join(self._test_report_dir, 'page.html')
        with self.log_exception("Attach page source"):
            with open(source_path, 'w') as f:
                f.write(self._get_page_html_source())

    @utils.ignore_skip
    def _attach_screenshot(self, exc_info):
        screen_path = os.path.join(self._test_report_dir, 'screenshot.png')
        with self.log_exception("Attach screenshot"):
            self.driver.get_screenshot_as_file(screen_path)

    @utils.ignore_skip
    def _attach_video(self, exc_info):
        with self.log_exception("Attach video"):
            self.video_recorder.stop()

            if not os.path.isfile(self.video_recorder.file_path):
                LOGGER.warn("can't copy video from {!r}".format(
                    self.video_recorder.file_path))
                return

            copyfile(self.video_recorder.file_path,
                     os.path.join(self._test_report_dir, 'video.mp4'))

    @utils.ignore_skip
    def _attach_browser_log(self, exc_info):
        browser_log_path = os.path.join(self._test_report_dir, 'browser.log')
        with self.log_exception("Attach browser log"):
            with open(browser_log_path, 'w') as f:
                f.write(
                    self._unwrap_browser_log(self.driver.get_log('browser')))

    @utils.ignore_skip
    def _attach_test_log(self, exc_info):
        test_log_path = os.path.join(self._test_report_dir, 'test.log')
        with self.log_exception("Attach test log"):
            with open(test_log_path, 'w') as f:
                f.write(self._log_buffer.getvalue().encode('utf-8'))

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
