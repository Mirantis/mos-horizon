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
import os
import shutil
from six import StringIO

from horizon.test import webdriver
import xvfbwrapper

from openstack_dashboard.test.integration_tests import utils
from openstack_dashboard.test.integration_tests.video_recorder import \
    VideoRecorder

ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(logging.DEBUG)

LOGGER = logging.getLogger(__name__)


def logger(test_case):
    log_buffer = StringIO()
    ROOT_LOGGER.handlers[:] = []

    stream_handler = logging.StreamHandler(stream=log_buffer)
    stream_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s#%(lineno)d - %(message)s')
    stream_handler.setFormatter(formatter)
    ROOT_LOGGER.addHandler(stream_handler)

    yield log_buffer

    if test_case.is_failed:
        log_path = os.path.join(test_case._test_report_dir, 'test.log')

        with test_case.log_exception("Attach test log"):
            with open(log_path, 'w') as log_file:
                log_file.write(log_buffer.getvalue().encode('utf-8'))


def video_recorder(test_case):
    recorder = VideoRecorder()
    recorder.start()

    yield recorder

    LOGGER.info("Stop video recording")
    recorder.stop()

    if test_case.is_failed:
        if os.path.isfile(recorder.file_path):
            with test_case.log_exception("Attach video"):
                shutil.move(recorder.file_path,
                            os.path.join(test_case._test_report_dir,
                                         'video.mp4'))
        else:
            LOGGER.warn(
                "Can't move video from {!r}".format(recorder.file_path))
    else:
        recorder.clear()


def web_driver(test_case):
    desired_capabilities = dict(webdriver.desired_capabilities)
    desired_capabilities['loggingPrefs'] = {'browser': 'ALL'}

    driver = webdriver.WebDriverWrapper(
        desired_capabilities=desired_capabilities)

    if utils.CONF.selenium.maximize_browser:
        driver.maximize_window()
        if utils.IS_SELENIUM_HEADLESS:
            driver.set_window_size(*utils.screen_size())

    driver.implicitly_wait(utils.CONF.selenium.implicit_wait)
    driver.set_page_load_timeout(utils.CONF.selenium.page_timeout)

    yield driver

    if test_case.is_failed:
        log_path = os.path.join(test_case._test_report_dir, 'browser.log')

        with test_case.log_exception("Attach browser log"):
            with open(log_path, 'w') as log_file:
                log_file.write(
                    test_case._unwrap_browser_log(driver.get_log('browser')))

    LOGGER.info('Stop web driver')
    driver.quit()


def vdisplay():
    width, height = utils.screen_size()
    vdisplay = xvfbwrapper.Xvfb(width=width, height=height)
    # workaround for memory leak in Xvfb taken from:
    # http://blog.jeffterrace.com/2012/07/xvfb-memory-leak-workaround.html
    # and disables X access control
    args = ["-noreset", "-ac"]

    if hasattr(vdisplay, 'extra_xvfb_args'):
        vdisplay.extra_xvfb_args.extend(args)  # xvfbwrapper 0.2.8 or newer
    else:
        vdisplay.xvfb_cmd.extend(args)

    vdisplay.start()
    current_display = VideoRecorder.DISPLAY
    VideoRecorder.DISPLAY = vdisplay.new_display

    yield vdisplay

    LOGGER.info('Stop xvfb')
    vdisplay.stop()
    VideoRecorder.DISPLAY = current_display
