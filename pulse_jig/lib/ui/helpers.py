import io
import re

import qrcode
from PySimpleGUI import Window

from pulse_jig.config import settings
from ..registrar import NetworkStatus


def generate_qrcode(data: str) -> bytes:
    qr = qrcode.QRCode()
    qr.add_data(data)
    # allow the library to determine the encoding settings based on the data it is given
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    # scale it to a fixed size
    img = img.resize((300, 300))

    bio = io.BytesIO()
    img.save(bio, format="PNG")

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


def validate_mode_selection_input(window: Window) -> bool:
    valid = True
    if settings.mode_vars:
        for key in settings.mode_vars:
            if isinstance(settings.mode_vars.get(key), list) and window[
                f"-{key.upper()}-"
            ].get() not in settings.mode_vars.get(key):
                valid = False
    return valid


def parse_selected_iecex_cert(selected: str) -> str:
    return re.sub(" *\(.*\)", "", selected)


def set_mode_values(mode: dict, window: Window):
    if settings.mode_vars:
        for key in settings.mode_vars:
            if key in mode.__dict__:
                value = window[f"-{key.upper()}-"].get()
                if key == "iecex_cert":
                    value = parse_selected_iecex_cert(window[f"-{key.upper()}-"].get())
                setattr(mode, key, value)
