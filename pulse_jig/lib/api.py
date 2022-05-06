import logging

import botocore.session
import requests
from requests import Response
from requests_aws4auth import AWS4Auth

from pulse_jig.config import settings

logger = logging.getLogger(__name__)


class Api:
    def __init__(self):
        self._region = settings.api.region
        self._host = settings.api.host
        self._stage = settings.app.stage
        self._service = "execute-api"

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
        return self._session().post(url, json=data)

    def provisioning_record(self, serial: str, data: dict) -> Response:
        url = self._url(f"device/{serial}/provisioning_record")
        return self._session().post(url, json=data)
