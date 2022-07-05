import enum
import io
import json
import logging
import queue
import threading

import PySimpleGUI as sg
import qrcode

from pulse_jig.config import settings
from ..provisioner.provisioner import Provisioner
from ..registrar import NetworkStatus
from ..timeout import Timeout
from ..ui.layouts.app_main_layout import layout as app_layout
from ..ui.layouts.mode_set_layout import layout as mode_layout


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread

    return wrapper


@threaded
def provisioner_thread(window, provisioner):
    def handler(event, data):
        window.write_event_value(event, data)

    provisioner.add_listener(handler)
    provisioner.run()


def _generate_qrcode(data: dict) -> bytes:
    qr = qrcode.QRCode(version=8, box_size=5, border=3)
    qr.add_data(json.dumps(data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black")

    bio = io.BytesIO()
    img.get_image().save(bio, format="PNG")

    return bio.getvalue()


class QueueHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord):
        self.log_queue.put(record)


class JigGUI:
    def __init__(self):
        self.current_status = Provisioner.Status.UNKNOWN

    def run(self, provisioner, registrar):
        self._app_window()
        self._mode_window()

        self._init_logs()

        while True:
            window, event, data = sg.read_all_windows(timeout=100)
            if event == sg.WIN_CLOSED:
                window.close()
            elif event == sg.TIMEOUT_KEY:
                pass
            else:
                self._set_mode(event, data, provisioner)
                self._update_mode(provisioner)
                if event in data:
                    self._update_state(event)
                    self._set_status(data[event].status)
                    self._update_qr(data[event])
                    self._update_firmware_version(data[event])
            self._update_logs(event, data)
            self._update_network_status(registrar.network_status)

    def _init_logs(self):
        self._log_queue = queue.Queue()
        self._queue_handler = QueueHandler(self._log_queue)
        self._queue_handler.setFormatter(logging.Formatter("[%(levelname)s:%(name)s] %(message)s"))
        logging.getLogger().addHandler(self._queue_handler)

    def _update_logs(self, event, data):
        try:
            timeout = Timeout(0.1)
            while not timeout.expired:
                if event == "waiting_for_target" and data[event].reset_logs:
                    self.window["-LOG-"].update("")
                else:
                    record = self._log_queue.get(block=False)
                    msg = self._queue_handler.format(record)
                    self.window["-LOG-"].update(msg + "\n", append=True)
        except queue.Empty:
            pass

    def _update_qr(self, state):
        data = None
        if state.status == Provisioner.Status.PASSED:
            data = _generate_qrcode(state.qrcode.__dict__)
        self.window["-QRCODE-"].update(data=data)

    def _update_firmware_version(self, state):
        firmware_version = state.firmware_version
        self.window["-FIRMWARE_VERSION-"].update(
            f"Firmware Version: v{firmware_version}",
        )

    def _set_status(self, status: Provisioner.Status):
        opts = {
            Provisioner.Status.UNKNOWN: ("", "black"),
            Provisioner.Status.WAITING: ("Waiting", "black"),
            Provisioner.Status.INPROGRESS: ("In Progress", "gray"),
            Provisioner.Status.PASSED: ("Passed", "green"),
            Provisioner.Status.FAILED: ("Failed", "red"),
            Provisioner.Status.RETRY: ("Retry", "orange"),
        }
        if self.current_status != status:
            self.current_status = status
            self.window["-PASSFAIL-"].update(opts[status][0], background_color=opts[status][1])
            self.window["-PASSFAIL_WRAPPER-"].Widget.config(background=opts[status][1])

    def _update_state(self, name):
        # Munge the status handle into something resembling English
        # based on our inside knowledge
        self.window["-STATE-"].update(name.replace("_", " ").capitalize())

    def _update_network_status(self, network_status: enum.Enum):
        if network_status == NetworkStatus.CONNECTED:
            status_msg = {"value": network_status.value, "text_color": "green"}
        elif network_status == NetworkStatus.TIMEOUT:
            status_msg = {"value": network_status.value, "text_color": "orange"}
        elif network_status in [NetworkStatus.NOT_CONNECTED, NetworkStatus.ERROR]:
            status_msg = {"value": network_status.value, "text_color": "red"}
        else:
            status_msg = {"value": "", "text_color": "white"}
        self.window["-NETWORK-"].update(**status_msg)

    def _update_mode(self, provisioner):
        mode_text = ""
        for item in provisioner.mode.__dict__:
            if mode_text != "":
                mode_text += ", "
            mode_text += f"{item}: {provisioner.mode.__dict__[item]}"
            if item == "cable_length":
                mode_text += "m"
        self.window["-MODE-"].update(mode_text)

    def _set_mode(self, event, data, provisioner):
        if event == "waiting_for_mode_set" or event == "-CHANGE_MODE-":
            self.window_mode.force_focus()
        elif event == "-SET_MODE-":
            if data["-CABLE_LENGTH-"] not in settings.device.cable_lengths:
                self.window_mode["-ERROR-"].update("Please select a value")
            else:
                self.window_mode["-ERROR-"].update("")

                # TODO can be improved for Pulse
                if provisioner.mode.cable_length == 0:
                    provisioner_thread(self.window, provisioner)
                else:
                    provisioner.restart()

                provisioner.mode.cable_length = data["-CABLE_LENGTH-"]
                provisioner.mode.manufacturer = settings.device.manufacturer_name
                provisioner.mode.device = settings.device.thing_type_name
                self.window.force_focus()
                self._update_mode(provisioner)

    def _app_window(self):
        self.window = sg.Window(
            "Pulse Production Jig",
            app_layout(),
            element_justification="center",
            resizable=True,
            finalize=True,
            font=("Arial", 10),
        )

        self.window.set_cursor("none")
        self.window.maximize()

    def _mode_window(self):
        self.window_mode = sg.Window(
            "Mode - Pulse Production Jig",
            mode_layout(),
            element_justification="center",
            resizable=True,
            finalize=True,
            font=("Arial", 18),
        )

        self.window_mode.set_cursor("none")
        self.window_mode.maximize()
