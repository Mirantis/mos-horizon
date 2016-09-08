"""
Network page.

@author: gdyuldin@mirantis.com
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

from pom import ui
from selenium.webdriver.common.by import By

from horizon_autotests.app import ui as _ui

from ..base import PageBase


@ui.register_ui(
    checkbox=_ui.CheckBox(By.CSS_SELECTOR, 'input[type="checkbox"]'))
class RowSubnet(_ui.Row):
    """Row with network in networks table."""


class TableSubnets(_ui.Table):
    """Table of subnets."""

    columns = {'name': 2, 'network_address': 3}
    row_cls = RowSubnet


@ui.register_ui(label_name=ui.UI(By.CSS_SELECTOR, 'dd:nth-of-type(1)'))
class Info(ui.Block):
    """Network info table."""


@ui.register_ui(button_next=ui.Button(By.CSS_SELECTOR, '.button-next'),
                field_subnet_name=ui.TextField(By.NAME, 'subnet_name'),
                field_network_address=ui.TextField(By.NAME, 'cidr'),
                combobox_ip_version=ui.ComboBox(By.NAME, 'ip_version'),
                field_gateway_ip=ui.TextField(By.NAME, 'gateway_ip'),
                checkbox_no_gateway=_ui.CheckBox(By.NAME, 'no_gateway'))
class FormCreateSubnet(_ui.Form):
    """Form to create subnet."""

    submit_locator = By.CSS_SELECTOR, '.btn.btn-primary.button-final'
    cancel_locator = By.CSS_SELECTOR, '.btn.btn-default.cancel'


@ui.register_ui(
    table_subnets=TableSubnets(By.ID, 'subnets'),
    info_network=Info(By.CSS_SELECTOR,
                      'div.detail dl.dl-horizontal:nth-of-type(1)'),
    button_create_subnet=ui.Button(By.ID, 'subnets__action_create'),
    button_delete_subnet=ui.Button(By.ID, 'subnets__action_delete'),
    form_create_subnet=FormCreateSubnet(
        By.XPATH, './/form[contains(@action, "subnets/create")]'))
class PageAdminNetwork(PageBase):
    """Admin network page"""

    url = "/admin/networks/{}/detail"
