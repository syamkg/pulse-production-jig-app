import time
from typing import Optional


class Timeout:
    def __init__(self, seconds: float):
        """
        Initialises and starts a timeout for given seconds.
        """
        self.end_time = time.monotonic() + seconds

    @property
    def expired(self) -> bool:
        """
        True if the timer has expired.
        """
        return time.monotonic() >= self.end_time

    @property
    def active(self) -> bool:
        """
        True if the timer has not expired.
        """
        return time.monotonic() < self.end_time

    @property
    def remaining(self) -> Optional[float]:
        """
        Returns the number of seconds remaining. If expired the value will be negative.
        """
        return self.end_time - time.monotonic()


class TimeoutNever(Timeout):
    def __init__(self):
        """
        Initialises and starts a timeout 0 seconds.
        """
        super().__init__(0)

    @property
    def expired(self):
        """
        Return False always, as timer will never expire
        """
        return False

    @property
    def active(self):
        """
        Return True always, as timer is never expired
        """
        return True

    @property
    def remaining(self):
        """
        Return None always for remaining number of seconds
        """
        return None
