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
import sys

import requests

from openstack_dashboard.test.integration_tests.helpers import ROOT_PATH

ROOT_LOGGER = logging.getLogger()
LOGGER = logging.getLogger(__name__)


def _reports_dir():
    reports_dir = os.path.join(ROOT_PATH, 'test_reports')
    if not os.path.isdir(reports_dir):
        os.makedirs(reports_dir)
    return reports_dir


def _configure_log():
    file_handler = logging.FileHandler(
        os.path.join(_reports_dir(), 'attach_diagnostic_snapshot.log'))
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s#%(lineno)d - %(message)s')
    file_handler.setFormatter(formatter)
    ROOT_LOGGER.addHandler(file_handler)


def _attach_diagnostic_snapshot():
    _configure_log()

    # FIXME(schipiga): include already installed packages for import visibility
    sys.path.extend(['/usr/lib/python2.7',
                     '/usr/lib/python2.7/dist-packages',
                     '/usr/local/lib/python2.7/dist-packages'])

    try:
        from devops.models import Environment
        from fuelclient import client, fuelclient_settings
        from fuelclient.objects import SnapshotTask
    except ImportError as e:
        LOGGER.error(e)
        return

    job_name = os.environ.get('JOB_NAME')
    if not job_name:
        LOGGER.info("Diagnostic snapshot is attached only on CI server")
        return

    env_name = os.environ.get('ENV_NAME')
    if not env_name:
        LOGGER.error("Environment name isn't specified at build")
        return

    try:
        env = Environment.get(name=env_name)
        master = env.get_nodes(role__in=('fuel_master', 'admin'))[0]
        admin_ip = master.get_ip_address_by_network_name('admin')

        os.environ.update({
            'SERVER_ADDRESS': admin_ip,
            'KEYSTONE_USER': 'admin',
            'KEYSTONE_PASS': 'admin',
        })
        fuelclient_settings._SETTINGS = None
        client.APIClient.__init__()

        config = SnapshotTask.get_default_config()
        task = SnapshotTask.start_snapshot_task(config)

        LOGGER.info('Starting snapshot creating...')
        task.wait()
        if task.status != 'ready':
            LOGGER.error("Snapshot creating is finished with error: {}".format(
                task.data["message"]))
            return
        LOGGER.info("Snapshot creating is finished")

        response = requests.get(
            'http://{}:8000{}'.format(admin_ip, task.data["message"]),
            stream=True,
            headers={'x-auth-token': client.APIClient.auth_token})

        file_path = os.path.join(_reports_dir(), 'diagnostic_snapshot.tar.xz')
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(65536):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        LOGGER.error(e)


def teardown_package():
    _attach_diagnostic_snapshot()
