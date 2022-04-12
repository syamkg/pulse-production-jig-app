import time


class Timeout:
    def __init__(self, seconds: float):
        """
        Initializes and starts a timeout for ms seconds.
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
    def remaining(self) -> float:
        """
        Returns the number of seconds remaining. If expired the value will be negative.
        """
        return self.end_time - time.monotonic()
