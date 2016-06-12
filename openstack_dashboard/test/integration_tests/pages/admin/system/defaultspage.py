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

from selenium.webdriver.common.by import By

from openstack_dashboard.test.integration_tests.pages import basepage
from openstack_dashboard.test.integration_tests.regions import forms


class DefaultsPage(basepage.BaseNavigationPage):

    UPDATE_QUOTAS_FORM_FIELDS = ("injected_file_content_bytes",)

    _uploaded_file_selector = (
        By.CSS_SELECTOR,
        "tr#quotas__row__injected_file_content_bytes > td:last-child")
    _update_quotas_button = (By.CSS_SELECTOR,
                             "a#quotas__action_update_defaults")

    def __init__(self, driver, conf):
        super(DefaultsPage, self).__init__(driver, conf)
        self._page_title = "Defaults"

    def get_uploaded_file_quota(self):
        return self._get_element(*self._uploaded_file_selector).text

    def set_uploaded_file_quota(self, value):
        self._get_element(*self._update_quotas_button).click()
        update_quotas_form = forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.UPDATE_QUOTAS_FORM_FIELDS)
        update_quotas_form.injected_file_content_bytes.value = value
        update_quotas_form.submit()
