import enum
import logging
import threading
from time import sleep
from typing import Optional

import requests

from pulse_jig.config import settings
from .api import Api
from .hwspec import HWSpec

logger = logging.getLogger("registrar")


class ThingType(enum.Enum):
    PULSE = 258
    PROBE = 513


class NetworkStatus(enum.Enum):
    CONNECTED = "Connected"
    NOT_CONNECTED = "Not Connected"
    TIMEOUT = "Request Timeout"
    ERROR = "Network Error"


def threaded(fn):
    """
    Decorator that multithreads the target function
    with the given parameters. Returns the thread
    created for the function
    """

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread

    return wrapper


class Registrar:
    def __init__(self):
        self._api = Api()
        self._network = NetworkStatus.NOT_CONNECTED

    def register_serial(self, hwspec: HWSpec, cable_length: Optional[int] = 0):
        data = {
            "serial": hwspec.serial,
            "fab_id": self._format_hex(hwspec.thing_type_id),
            "fab_ver": hwspec.hw_revision,
            "assembly_id": self._format_hex(hwspec.assembly_id),
            "assembly_ver": hwspec.assembly_version,
            "manufacturer_id": self._format_hex(hwspec.manufacturer_id),
            "date_of_manufacture": hwspec.assembly_timestamp,
        }

        if cable_length != 0:
            data["cable_length"] = str(cable_length) + "mm"

        try:
            response = self._api.add_item(data)
            return True if response.status_code == 201 else False
        except requests.exceptions.ConnectionError:
            self._network = NetworkStatus.NOT_CONNECTED
            return False
        except requests.exceptions.ReadTimeout:
            self._network = NetworkStatus.TIMEOUT
            return False
        except requests.exceptions.RequestException:
            self._network = NetworkStatus.ERROR
            return False

    def submit_provisioning_record(self, hwspec: HWSpec, status: str, logs: str, firmware_version: str):
        data = {
            "status": status,
            "log": logs,
            "provisioning_firmware_ver": firmware_version,
            "provisioning_client_ver": self._get_provisioning_client_ver(),
        }

        try:
            response = self._api.provisioning_record(hwspec.serial, data)
            return True if response.status_code == 201 else False
        except requests.exceptions.ConnectionError:
            self._network = NetworkStatus.NOT_CONNECTED
            return False
        except requests.exceptions.ReadTimeout:
            self._network = NetworkStatus.TIMEOUT
            return False
        except requests.exceptions.RequestException:
            self._network = NetworkStatus.ERROR
            return False

    @threaded
    def network_check(self):
        while True:
            try:
                if self._api.auth_check().status_code == 200:
                    self._network = NetworkStatus.CONNECTED
                else:
                    self._network = NetworkStatus.ERROR
            except requests.exceptions.ConnectionError:
                self._network = NetworkStatus.NOT_CONNECTED
            except requests.exceptions.ReadTimeout:
                self._network = NetworkStatus.TIMEOUT
            except requests.exceptions.RequestException:
                self._network = NetworkStatus.ERROR
            logger.debug(f"network_check(): {self._network.value}")
            sleep(settings.network.ping_interval)

    @property
    def network_status(self) -> enum.Enum:
        return self._network

    @staticmethod
    def _get_provisioning_client_ver() -> str:
        return settings.VERSION

    @staticmethod
    def _format_hex(value) -> str:
        return "{:#04x}".format(value)
