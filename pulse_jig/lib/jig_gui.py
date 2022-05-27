import io
import json
import logging
import queue
import threading

import PySimpleGUI as sg
import qrcode

from .provisioner.provisioner import Provisioner
from .timeout import Timeout


def _provisioner_thread(window, provisioner):
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

    def run(self, provisioner):
        self._init_gui()
        self._init_logs()

        threading.Thread(target=_provisioner_thread, args=(self.window, provisioner), daemon=True).start()

        while True:
            event, data = self.window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break
            elif event == sg.TIMEOUT_KEY:
                pass
            else:
                self._update_state(event)
                self._set_status(data[event].status)
                self._update_qr(data[event])
            self._update_logs(event, data)
            self._update_network_status(provisioner.has_network())

        self.window.close()

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
            data = _generate_qrcode(
                {"sn": state.hwspec.serial, "rev": state.hwspec.hw_revision, "dom": state.hwspec.assembly_timestamp}
            )
        self.window["-QRCODE-"].update(data=data)

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

    def _update_network_status(self, network_status):
        if network_status:
            status_msg = {"value": "Connected", "text_color": "green"}
        else:
            status_msg = {"value": "Not connected", "text_color": "red"}
        self.window["-NETWORK-"].update(**status_msg)

    def _init_gui(self):
        sg.theme("Black")
        layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Sizer(450, 0)],
                        [
                            sg.Frame(
                                "State",
                                layout=[
                                    [
                                        sg.Text(
                                            key="-STATE-",
                                            font=("Arial", 20, "bold"),
                                            expand_x=True,
                                            expand_y=True,
                                        )
                                    ],
                                    [sg.Sizer(0, 5)],
                                ],
                                expand_x=True,
                            )
                        ],
                        [
                            sg.Frame(
                                "Log",
                                layout=[
                                    [
                                        sg.Multiline(
                                            key="-LOG-",
                                            disabled=True,
                                            autoscroll=True,
                                            border_width=0,
                                            font=("Courier New", 8),
                                            background_color="black",
                                            expand_x=True,
                                            expand_y=True,
                                        )
                                    ]
                                ],
                                expand_x=True,
                                expand_y=True,
                            )
                        ],
                    ],
                    expand_x=True,
                    expand_y=True,
                ),
                sg.Column(
                    layout=[
                        [sg.Sizer(350, 0)],
                        [
                            sg.Frame(
                                "",
                                key="-PASSFAIL_WRAPPER-",
                                layout=[
                                    [sg.Sizer(0, 8)],
                                    [
                                        sg.Text(
                                            key="-PASSFAIL-",
                                            font=("Arial", 20, "bold"),
                                            justification="center",
                                            pad=0,
                                            expand_x=True,
                                        )
                                    ],
                                    [sg.Sizer(0, 8)],
                                ],
                                vertical_alignment="center",
                                expand_x=True,
                                pad=(4, (10, 4)),
                            )
                        ],
                        [
                            sg.Frame(
                                "QR Code",
                                layout=[[sg.Image(key="-QRCODE-", expand_x=True, expand_y=True)]],
                                element_justification="center",
                                vertical_alignment="center",
                                expand_x=True,
                                expand_y=True,
                            )
                        ],
                    ],
                    element_justification="center",
                    expand_y=True,
                    expand_x=True,
                ),
            ],
            [
                sg.Frame(
                    "App status",
                    layout=[
                        [sg.Text("Network:"), sg.Text(key="-NETWORK-")],
                        [sg.Sizer(0, 5)],
                    ],
                    expand_x=True,
                    pad=(10, 5),
                )
            ],
        ]

        self.window = sg.Window(
            "Pulse Production Jig",
            layout,
            element_justification="center",
            resizable=True,
            finalize=True,
            font=("Arial", 10),
        )
        self.window.maximize()
        self.window.refresh()
