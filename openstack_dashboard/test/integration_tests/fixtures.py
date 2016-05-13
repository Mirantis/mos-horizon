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

from horizon.test import webdriver
import xvfbwrapper

from openstack_dashboard.test.integration_tests import utils
from openstack_dashboard.test.integration_tests.video_recorder import \
    VideoRecorder

LOGGER = logging.getLogger(__name__)


def video_recorder():
    recorder = VideoRecorder()
    recorder.start()

    yield recorder

    LOGGER.info("Stop video recording")
    recorder.stop()
    recorder.clear()


def web_driver():
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
