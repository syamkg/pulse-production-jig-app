import PySimpleGUI as sg
import threading
from provisioner import Provisioner
import qrcode
import io
import queue
import logging


def provisioner_thread(window, provisioner):
    def handler(event, data):
        window.write_event_value(event, data)

    provisioner.add_listener(handler)
    provisioner.run()


def generate_qrcode(serial: str):
    img = qrcode.make(serial)
    bio = io.BytesIO()
    img.get_image().save(bio, format="PNG")
    return bio.getvalue()


class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class JigGUI:
    def __init__(self):
        self.current_status = Provisioner.Status.UNKNOWN

    def run(self, provisioner):
        self._init_gui()
        self._init_logs()

        threading.Thread(target=provisioner_thread, args=(self.window, provisioner), daemon=True).start()

        while True:
            event, data = self.window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break
            elif event == sg.TIMEOUT_KEY:
                pass
            else:
                self._update_state(event)
                self._set_status(data[event]["status"])
                self._update_qr(data[event])
            self._update_logs()

        self.window.close()

    def _init_logs(self):
        self._log_queue = queue.Queue()
        self._queue_handler = QueueHandler(self._log_queue)
        self._queue_handler.setFormatter(logging.Formatter("[%(levelname)s:%(name)s] %(message)s"))
        logging.getLogger().addHandler(self._queue_handler)

    def _update_logs(self):
        try:
            record = self._log_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            msg = self._queue_handler.format(record)
            self.window["-LOG-"].update(msg + "\n", append=True)

    def _update_qr(self, state):
        if state["status"] == Provisioner.Status.PASSED:
            data = generate_qrcode(state["hwspec"]["serial"])
        else:
            data = None
        self.window["-QRCODE-"].update(data=data)

    def _set_status(self, status: Provisioner.Status):
        opts = {
            Provisioner.Status.UNKNOWN: ("", "black"),
            Provisioner.Status.WAITING: ("Waiting", "black"),
            Provisioner.Status.INPROGRESS: ("In Progress", "gray"),
            Provisioner.Status.PASSED: ("Pass", "green"),
            Provisioner.Status.FAILED: ("Fail", "red"),
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

    def _init_gui(self):
        sg.theme("Black")
        layout = [
            [
                sg.Column(
                    layout=[
                        [sg.Sizer(500, 0)],
                        [
                            sg.Frame(
                                "State",
                                layout=[
                                    [
                                        sg.Text(
                                            key="-STATE-",
                                            font="Helvetica 20 bold",
                                            expand_x=True,
                                            expand_y=True,
                                        )
                                    ]
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
                                            font="Monospace 8 normal",
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
                        [sg.Sizer(300, 0)],
                        [
                            sg.Frame(
                                "",
                                key="-PASSFAIL_WRAPPER-",
                                layout=[
                                    [sg.Sizer(0, 10)],
                                    [
                                        sg.Text(
                                            key="-PASSFAIL-",
                                            font="Helvetica 20 bold",
                                            justification="center",
                                            pad=0,
                                            expand_x=True,
                                        )
                                    ],
                                    [sg.Sizer(0, 1)],
                                ],
                                vertical_alignment="center",
                                expand_x=True,
                                pad=(4, (10, 4)),
                            )
                        ],
                        [
                            sg.Frame(
                                "QRCode",
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
            ]
        ]

        self.window = sg.Window(
            "Pulse Production Jig",
            layout,
            element_justification="center",
            resizable=True,
            finalize=True,
        )
        self.window.maximize()
        self.window.refresh()
