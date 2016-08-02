import logging
import os
import signal
import subprocess
from threading import Thread
import time

LOGGER = logging.getLogger(__name__)


class VideoRecorder(object):

    def __init__(self, folder, frame_rate=30):
        self.is_launched = False
        self.file_path = os.path.join(folder, 'video.mp4')
        # avconv -f x11grab -r 15 -s 1920x1080 -i :0.0 -codec libx264 out.mp4
        self._cmd = ['avconv', '-f', 'x11grab', '-r', str(frame_rate),
                     '-s', '{}x{}'.format(1920, 1080),
                     '-i', os.environ['DISPLAY'],
                     '-codec', 'libx264', self.file_path]

    def start(self):
        if self.is_launched:
            LOGGER.warn('Video recording is running already')
            return

        fnull = open(os.devnull, 'w')
        LOGGER.info('Record video via {!r}'.format(' '.join(self._cmd)))
        self._popen = subprocess.Popen(self._cmd, stdout=fnull, stderr=fnull)
        self.is_launched = True

    def stop(self):
        if not self.is_launched:
            LOGGER.warn('Video recording is stopped already')
            return

        LOGGER.info('Stop video recording')
        self._popen.send_signal(signal.SIGINT)

        def terminate_avconv():
            limit = time.time() + 10

            while time.time() < limit:
                time.sleep(0.1)
                if self._popen.poll() is not None:
                    return

            os.kill(self._popen.pid, signal.SIGTERM)

        t = Thread(target=terminate_avconv)
        t.start()

        self._popen.communicate()
        t.join()
        self.is_launched = False

    def clear(self):
        if self.is_launched:
            LOGGER.error("Video recording is running still")
            return

        if not os.path.isfile(self.file_path):
            LOGGER.warn("{!r} is absent already".format(self.file_path))
            return

        os.remove(self.file_path)
