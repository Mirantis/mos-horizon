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
from openstack_dashboard.test.integration_tests.regions import tables


class ObjectRowRegion(tables.RowRegion):

    _cell_locator = (By.CSS_SELECTOR, 'td')

    def __init__(self, driver, conf, src_elem):
        super(ObjectRowRegion, self).__init__(driver, conf, src_elem, None)

    @property
    def cells(self):
        return self._get_elements(*self._cell_locator)


class ObjectsTable(tables.TableRegion):
    name = 'objects'

    _default_src_locator = (By.CSS_SELECTOR, 'table.table.hz-objects')
    _upload_selector = (By.XPATH, "//a[@ng-click='oc.uploadObject()']")
    _folder_selector = (By.XPATH, "//a[@ng-click='oc.createFolder()']")
    _dropdown_selector = (By.CSS_SELECTOR, "button.dropdown-toggle")
    _delete_button_selector = (By.CSS_SELECTOR, "button.btn.btn-danger")
    _delete_item_selector = (By.CSS_SELECTOR, "a.text-danger")
    _empty_table_locator = (By.CSS_SELECTOR, 'tbody > tr > td.no-rows-help')

    def __init__(self, driver, conf):
        super(tables.TableRegion, self).__init__(driver, conf)

    def _get_rows(self, *args):
        return [ObjectRowRegion(self.driver, self.conf, elem)
                for elem in self._get_elements(*self._rows_locator)]

    @property
    def create_folder_button(self):
        return self._get_element(*self._folder_selector)

    @property
    def upload_button(self):
        return self._get_element(*self._upload_selector)

    @property
    def is_empty(self):
        return self._is_element_present(*self._empty_table_locator)

    def delete_row(self, name):
        row = self._wait_until(lambda _: self.get_row(0, name))
        
        if row._is_element_present(*self._dropdown_selector):
            dropdown = row._get_element(*self._dropdown_selector)
            dropdown.click()
            delete_button = row._get_element(*self._delete_item_selector)
        else:
            delete_button = row._get_element(*self._delete_button_selector)
        delete_button.click()


class ContainersPage(basepage.BaseNavigationPage):

    CREATE_CONTAINER_FORM_FIELDS = ("name", "public")
    UPLOAD_FILE_FORM_FIELDS = ("file",)
    CREATE_FOLDER_FORM_FIELDS = ("name",)

    _create_container_selector = (By.CSS_SELECTOR, "button.btn.btn-default")
    _container_selector_tmpl = ("//div[contains(@class, 'panel') and "
                                "contains(@class ,'panel-default') and "
                                "descendant::span[contains(@class, "
                                "'hz-container-title') and @tooltip='{}']]")
    _delete_container_selector = (By.CSS_SELECTOR,
                                  "span.hz-container-delete-icon")
    _container_details = (By.CSS_SELECTOR, 'div.panel-body')
    _public_link = (By.CSS_SELECTOR, 'a[ng-show="container.public_url"]')

    def __init__(self, driver, conf):
        super(ContainersPage, self).__init__(driver, conf)
        self._page_title = "Containers"

    @property
    def create_container_button(self):
        return self._get_element(*self._create_container_selector)

    def get_container(self, name):
        container_selector = self._container_selector_tmpl.format(name)
        return self._get_element(By.XPATH, container_selector)

    def create_container(self, name, public=False):
        self.create_container_button.click()
        create_container_form = forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.CREATE_CONTAINER_FORM_FIELDS)
        create_container_form.name.text = name
        if public:
            create_container_form.public.mark()
        else:
            create_container_form.public.unmark()
        create_container_form.submit()

    def get_public_container_link(self, name):
        container = self.get_container(name)
        return container.find_element(*self._public_link).get_attribute('href')

    def choose_container(self, name):
        container = self.get_container(name)
        container.click()

    def has_details(self, name):
        container = self.get_container(name)
        return container.find_element(*self._container_details).is_displayed()

    def delete_container(self, name):
        container = self.get_container(name)
        delete_button = container.find_element(
            *self._delete_container_selector)
        delete_button.click()

        confirm_delete_form = forms.BaseFormRegion(self.driver, self.conf)
        confirm_delete_form.submit()

    @property
    def objects_table(self):
        return ObjectsTable(self.driver, self.conf)

    def upload_file(self, file_name):
        self.objects_table.upload_button.click()
        upload_file_form = forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.UPLOAD_FILE_FORM_FIELDS)
        upload_file_form.file.choose(file_name)
        upload_file_form.submit()

    def create_folder(self, folder_name):
        self.objects_table.create_folder_button.click()
        create_folder_form = forms.FormRegion(
            self.driver, self.conf,
            field_mappings=self.CREATE_FOLDER_FORM_FIELDS)
        create_folder_form.name.text = folder_name
        create_folder_form.submit()

    def delete_object(self, object_name):
        self.objects_table.delete_row(object_name)

        confirm_delete_form = forms.BaseFormRegion(self.driver, self.conf)
        confirm_delete_form.submit()

    def choose_folder(self, folder_name):
        folder = self.is_object_present(folder_name)
        folder_link = folder.cells[0].find_element(By.CSS_SELECTOR, 'a')
        folder_link.click()
        self._wait_until(lambda _: self.objects_table.is_empty)

    def is_object_present(self, name):
        return self._wait_until(lambda _: self.objects_table.get_row(0, name))

    def is_object_deleted(self, name):
        return self._wait_until(lambda _: not self.objects_table.get_row(0,
                                                                         name))

    def is_container_present(self, name):
        container_selector = self._container_selector_tmpl.format(name)
        return self._wait_till_element_visible((By.XPATH, container_selector))

    def is_container_deleted(self, name):
        container_selector = self._container_selector_tmpl.format(name)
        return self.wait_till_element_disappears(
            lambda: self._get_element(By.XPATH, container_selector))
