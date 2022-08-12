import io
import json

import qrcode

from pulse_jig.config import settings
from ..registrar import NetworkStatus


def generate_qrcode(data: dict) -> bytes:
    qr = qrcode.QRCode(version=10, box_size=4, border=3)
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")

    bio = io.BytesIO()
    img.get_image().save(bio, format="PNG")

    return bio.getvalue()


def network_status_text(network_status: NetworkStatus) -> dict:
    if network_status == NetworkStatus.CONNECTED:
        status_msg = {"value": network_status.value, "text_color": "green"}
    elif network_status == NetworkStatus.TIMEOUT:
        status_msg = {"value": network_status.value, "text_color": "orange"}
    elif network_status in [NetworkStatus.NOT_CONNECTED, NetworkStatus.ERROR]:
        status_msg = {"value": network_status.value, "text_color": "red"}
    else:
        status_msg = {"value": "Not Connected", "text_color": "red"}

    return status_msg


def parse_mode(mode: dict) -> str:
    mode_text = ""
    for item in mode.__dict__:
        if mode_text != "":
            mode_text += ", "
        mode_text += f"{item}: {mode.__dict__[item]}"

        if item == "cable_length":
            mode_text += "m"

    return mode_text


def validate_mode_selection_input(data) -> bool:
    valid = True
    if settings.mode_vars:
        for key in settings.mode_vars:
            if data[f"-{key.upper()}-"] not in settings.mode_vars.get(key):
                valid = False
    return valid


def set_mode_values(mode: dict, data):
    if settings.mode_vars:
        for key in settings.mode_vars:
            if key in mode.__dict__:
                setattr(mode, key, data[f"-{key.upper()}-"])
