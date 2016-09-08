"""
Custom form.

@author: schipiga@mirantis.com
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pom
from pom import ui
from selenium.webdriver.common.by import By

from horizon_autotests import ACTION_TIMEOUT


class Form(ui.Form):
    """Custom form."""

    timeout = ACTION_TIMEOUT

    submit_locator = By.CSS_SELECTOR, '.btn.btn-primary'
    cancel_locator = By.CSS_SELECTOR, '.btn.cancel'

    @pom.timeit
    @ui.wait_for_presence
    def submit(self):
        """Submit form."""
        submit_button = ui.Button(*self.submit_locator)
        submit_button.container = self
        submit_button.click()
        self._spinner.wait_for_absence()

    @pom.timeit
    @ui.wait_for_presence
    def cancel(self):
        """Cancel form."""
        cancel_button = ui.Button(*self.cancel_locator)
        cancel_button.container = self
        cancel_button.click()
        self._modal.wait_for_absence()

    @property
    @pom.cache
    def _spinner(self):
        container = self.container
        while True:
            spinner = getattr(container, 'spinner', None)
            if spinner:
                return spinner
            else:
                container = container.container

    @property
    @pom.cache
    def _modal(self):
        container = self.container
        while True:
            modal = getattr(container, 'modal', None)
            if modal:
                return modal
            else:
                container = container.container
