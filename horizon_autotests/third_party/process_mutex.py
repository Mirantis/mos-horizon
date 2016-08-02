import fcntl


class Lock(object):
    """Process mutex."""

    def __init__(self, filename):
        self.filename = filename
        # This will create it if it does not exist already
        self.handle = open(self.filename, 'w')

    # Bitwise OR fcntl.LOCK_NB if you need a non-blocking lock
    def acquire(self):
        fcntl.flock(self.handle, fcntl.LOCK_EX)

    def release(self):
        fcntl.flock(self.handle, fcntl.LOCK_UN)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, ext_type, exc_val, exc_tb):
        self.release()

    def __del__(self):
        self.handle.close()
