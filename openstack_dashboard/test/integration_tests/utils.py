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

from functools import wraps
import logging
import os
import subprocess
import types

from openstack_dashboard.test.integration_tests import config

CONF = config.get_config()
LOGGER = logging.getLogger(__name__)
IS_SELENIUM_HEADLESS = os.environ.get('SELENIUM_HEADLESS', False)


def once_only(func):
    called_funcs = {}

    @wraps(func)
    def wrapper(*args, **kwgs):
        if func.__name__ not in called_funcs:
            result = obj = func(*args, **kwgs)
            if isinstance(obj, types.GeneratorType):

                def gi_wrapper():
                    while True:
                        result = obj.next()
                        called_funcs[func.__name__] = result
                        yield result

                return gi_wrapper()
            else:
                called_funcs[func.__name__] = result
                return result
        else:
            return called_funcs[func.__name__]

    return wrapper


def screen_size():
    if IS_SELENIUM_HEADLESS:
        return (1920, 1080)

    if not subprocess.call('which xdpyinfo > /dev/null 2>&1', shell=True):
        return subprocess.check_output(
            'xdpyinfo | grep dimensions', shell=True).split()[1].split('x')

    else:
        default = (1024, 768)
        LOGGER.error(
            "can't define screen resolution, use default {!r}".format(default))
        return default
