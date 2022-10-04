import logging
import queue
import threading

import PySimpleGUI as sg

from . import helpers as h
from ..provisioner.provisioner import Provisioner
from ..registrar import Registrar, NetworkStatus
from ..timeout import Timeout
from ..ui.layouts.app_main_layout import layout as app_layout
from ..ui.layouts.mode_set_layout import layout as mode_layout

logger = logging.getLogger("jig_gui")


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


@threaded
def provisioner_thread(window, provisioner):
    def handler(event, data):
        window.write_event_value(event, data)

    provisioner.add_listener(handler)
    provisioner.run()


class QueueHandler(logging.Handler):
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        self.log_queue.put(record)


class JigGUI:
    def __init__(self):
        self.current_status = Provisioner.Status.UNKNOWN
        self.provisioner = None
        self.provisioner_thread = None

    def run(self, provisioner_factory, registrar: Registrar):
        self._provisioner_factory = provisioner_factory
        self._app_window()

        # show the "mode selection window"
        self._mode_window()

        self._init_logs()

        while True:
            window, event, data = sg.read_all_windows(timeout=100)
            if event == sg.WIN_CLOSED:
                window.close()
            elif event == sg.TIMEOUT_KEY:
                pass
            else:
                self._update_mode(event, data)
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
        self._queue_handler.setFormatter(logging.Formatter("[%(levelname)-4.4s:%(name)-11.11s] %(message)s"))
        logging.getLogger().addHandler(self._queue_handler)

    def _update_logs(self, event, data):
        try:
            timeout = Timeout(0.1)
            while not timeout.expired:
                if data and event in data and data[event].reset_logs:
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
            data = h.generate_qrcode(str(state.qrcode))
        self.window["-QRCODE-"].update(data=data)

    def _update_firmware_version(self, state):
        self.window["-TEST_FIRMWARE_VERSION-"].update(f"Test Firmware: v{state.test_firmware_version}")
        self.window["-PROD_FIRMWARE_VERSION-"].update(f"Prod Firmware: v{state.prod_firmware_version}")

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

    def _update_network_status(self, network_status: NetworkStatus):
        status_msg = h.network_status_text(network_status)
        self.window["-NETWORK-"].update(**status_msg)

    def _update_mode(self, event, data):
        if event == "waiting_for_mode_set" or event == "-CHANGE_MODE-":
            self.window_mode.force_focus()
        elif event == "-SET_MODE-":
            if h.validate_mode_selection_input(data):
                self.window_mode["-ERROR-"].update("")

                if self.provisioner_thread:
                    self.provisioner.terminate()

                self.provisioner = self._provisioner_factory(data["-TARGET-"])
                self.provisioner_thread = provisioner_thread(self.window, self.provisioner)

                # Set values to each field in provisioner.mode
                h.set_mode_values(self.provisioner.mode, data)
                mode_text = h.parse_mode(self.provisioner.mode)
                self.window["-MODE-"].update(mode_text)

                self.window.force_focus()
            else:
                self.window_mode["-ERROR-"].update("Please select a value")

    def _app_window(self):
        self.window = sg.Window(
            "Pulse Production Jig",
            app_layout(),
            element_justification="center",
            resizable=True,
            finalize=True,
            font=("Arial", 10),
            element_padding=3,
            margins=(0, 0),
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
