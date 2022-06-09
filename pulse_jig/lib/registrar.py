import enum
import json
import logging
import threading
from time import sleep

import requests

from pulse_jig.config import settings
from .api import Api
from .hwspec import HWSpec

logger = logging.getLogger("registrar")


class ThingType(enum.Enum):
    PULSE = 258
    PROBE = 513


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
        self._network = False

    def register_serial(self, hwspec: HWSpec):
        data = {
            "serial": hwspec.serial,
            "fab_id": self._format_hex(hwspec.thing_type_id),
            "fab_ver": hwspec.hw_revision,
            "assembly_id": self._format_hex(hwspec.assembly_id),
            "assembly_ver": hwspec.assembly_version,
            "manufacturer_id": self._format_hex(hwspec.manufacturer_id),
            "date_of_manufacture": hwspec.assembly_timestamp,
            "provisioning_firmware_ver": hwspec.factory_test_firmware_version,
            "provisioning_client_ver": self._get_provisioning_client_ver(),
        }

        if self._is_pulse(hwspec.thing_type_id):
            data["dev_eui"] = ""  # TODO implement
            data["join_eui"] = settings.lora.join_eui
            data["app_key"] = ""  # TODO implement
            data["provisioned_firmware_ver"] = ""  # TODO implement

        response = self._api.add_item(data)
        logger.info(response.json()["message"])
        logger.debug("\n" + self._pretty_print(response.text))
        return True if response.status_code == 201 else False

    def submit_provisioning_record(self, hwspec: HWSpec, status: str, logs: str, error: str = ""):
        data = {
            "status": status,
            "failure_reason": error,
            "log": logs,
            "provisioning_firmware_ver": hwspec.factory_test_firmware_version,
            "provisioning_client_ver": self._get_provisioning_client_ver(),
        }

        if self._is_pulse(hwspec.thing_type_id):
            data["provisioned_firmware_ver"] = ""  # TODO implement

        response = self._api.provisioning_record(hwspec.serial, data)
        logger.info(response.json()["message"])
        logger.debug("\n" + self._pretty_print(response.text))
        return True if response.status_code == 201 else False

    @threaded
    def network_check(self):
        while True:
            try:
                self._network = self._api.auth_check().status_code == 200
            except requests.exceptions.ConnectionError:
                self._network = False
            status = "Connected" if self._network else "Not connected"
            logger.debug(f"Network: {status}")
            sleep(settings.network.ping_interval)

    @property
    def network(self) -> bool:
        return self._network

    @staticmethod
    def _pretty_print(data):
        try:
            return json.dumps(json.loads(data), sort_keys=False, indent=4)
        except (ValueError, TypeError):
            return json.dumps(data, sort_keys=False, indent=4)

    @staticmethod
    def _is_pulse(thing_type_id: int) -> bool:
        return thing_type_id == ThingType.PULSE.value

    @staticmethod
    def _get_provisioning_client_ver() -> str:
        return settings.VERSION

    @staticmethod
    def _format_hex(value) -> str:
        return "{:#04x}".format(value)
