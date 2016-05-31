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
import signal
import subprocess
from tempfile import mktemp

from openstack_dashboard.test.integration_tests.utils import screen_size

LOGGER = logging.getLogger(__name__)


def if_ffmpeg(func):

    @wraps(func)
    def wrapper(self, *args, **kwgs):
        if self._no_ffmpeg:
            return
        return func(self, *args, **kwgs)

    return wrapper


class VideoRecorder(object):

    DISPLAY = '0.0'

    def __init__(self):
        self._no_ffmpeg = False
        self.is_launched = False
        self.file_path = mktemp() + '.mp4'
        self._args = ['ffmpeg', '-video_size', '{}x{}'.format(*screen_size()),
                      '-framerate', '15', '-f', 'x11grab', '-i',
                      ':{}'.format(self.DISPLAY), '-codec', 'libx264',
                      self.file_path]

    @if_ffmpeg
    def start(self):
        if self.is_launched:
            LOGGER.warn("recording is already launched")
            return

        if subprocess.call('which ffmpeg > /dev/null 2>&1', shell=True):
            LOGGER.error("ffmpeg isn't installed")
            self._no_ffmpeg = True
            return

        fnull = open(os.devnull, 'w')
        LOGGER.info('record video with {!r}'.format(' '.join(self._args)))
        self._popen = subprocess.Popen(self._args, stdout=fnull, stderr=fnull)
        self.is_launched = True

    @if_ffmpeg
    def stop(self):
        if not self.is_launched:
            LOGGER.warn("recording isn't launched")
            return

        self._popen.send_signal(signal.SIGINT)
        self._popen.communicate()
        self.is_launched = False

    @if_ffmpeg
    def clear(self):
        if not os.path.isfile(self.file_path):
            LOGGER.warn("{!r} is absent".format(self.file_path))
            return

        os.remove(self.file_path)
