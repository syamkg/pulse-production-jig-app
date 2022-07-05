import json
import logging

import botocore.session
import requests
from requests import Response
from requests_aws4auth import AWS4Auth

from pulse_jig.config import settings

logger = logging.getLogger("api")

logging.getLogger("botocore").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)


class Api:
    def __init__(self):
        self._region = settings.api.region
        self._host = settings.api.host
        self._stage = settings.api.stage
        self._service = "execute-api"
        self._timeout = 10

    def _auth(self) -> AWS4Auth:
        credentials = botocore.session.Session().get_credentials()
        return AWS4Auth(region=self._region, service=self._service, refreshable_credentials=credentials)

    def _url(self, uri: str) -> str:
        return "/".join([self._host, self._stage, uri])

    def _session(self):
        s = requests.Session()
        s.auth = self._auth()
        return s

    def add_item(self, data: dict) -> Response:
        url = self._url("device")
        response = self._session().post(url, json=data, timeout=self._timeout)
        log(response)
        return response

    def provisioning_record(self, serial: str, data: dict) -> Response:
        url = self._url(f"device/{serial}/provisioning_record")
        response = self._session().post(url, json=data, timeout=self._timeout)
        log(response)
        return response

    def auth_check(self) -> Response:
        url = self._url("auth/check")
        response = self._session().get(url, timeout=self._timeout)
        return response


def log(response: Response):
    logger.info(response.json()["message"])
    logger.debug("\n" + pretty_print(response.text))


def pretty_print(data):
    try:
        return json.dumps(json.loads(data), sort_keys=False, indent=4)
    except (ValueError, TypeError):
        return json.dumps(data, sort_keys=False, indent=4)
