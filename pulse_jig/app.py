#!/usr/bin/env python
"""
This is a placeholder application demonstrating how PySimpleGUI can accept
controls from both a user and a TBD test harness. It has the currently
understood wait/test/display QR loop.

It runs fullscreen with no capability to exit and is intended to be run on
boot on an RPI with a touchscreen.
"""

import io
import logging
import queue
import threading
from typing import Optional

import PySimpleGUI as sg
import click
import qrcode

from jig_client import JigClient
from jig_tester import JigTester


def create_jig_tester(dev: str):
    return JigTester(
        dev,
        pcb_sense_gpio_pin=5,
        reset_gpio_pin=6,
        registrar_url="https://1mgiqq52xc.execute-api.ap-southeast-2.amazonaws.com/prod/",
    )


def tester_thread(window: sg.Window, dev: str):
    ft = create_jig_tester(dev)

    def handler(event, data):
        window.write_event_value(event, data)

    ft.add_listener(handler)
    ft.run()


def generate_qrcode(serial: str):
    img = qrcode.make(serial)
    bio = io.BytesIO()
    img.get_image().save(bio, format="PNG")
    return bio.getvalue()


def configure_logging(debug: bool, gui: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("transitions").setLevel(logging.INFO)
        logging.getLogger("JigClient").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("transitions").setLevel(logging.WARN)

    log_queue = None
    queue_handler = None
    if gui:
        log_queue = queue.Queue()
        queue_handler = QueueHandler(log_queue)
        queue_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logging.getLogger().addHandler(queue_handler)

    return log_queue, queue_handler


class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)


class App:
    def __init__(self, dev: str):
        self.window = None
        self.dev = dev

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
                                layout=[
                                    [
                                        sg.Image(
                                            key="-QRCODE-", expand_x=True, expand_y=True
                                        )
                                    ]
                                ],
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

    def _state_wait_for_serial(self):
        self.window["-STATE-"].update("Waiting for serial...")
        self.window.refresh()

    def _state_wait_for_pcb(self):
        self.window["-STATE-"].update("Waiting for PCB...")
        self.window.refresh()

    def _state_test_running(self):
        self.window["-STATE-"].update("Running test...")
        self.window.refresh()

    def _state_test_passed(self, serial):
        self.window["-PASSFAIL-"].update("Pass", background_color="green")
        self.window["-PASSFAIL_WRAPPER-"].Widget.config(background="green")
        self.window["-QRCODE-"].update(data=generate_qrcode(serial))
        self.window["-STATE-"].update("Disconnect PCB...")
        self.window.refresh()

    def _state_test_failed(self):
        self.window["-PASSFAIL-"].update("Failed", background_color="Red")
        self.window["-PASSFAIL_WRAPPER-"].Widget.config(background="Red")
        self.window["-QRCODE-"].update()
        self.window["-STATE-"].update("Disconnect PCB...")
        self.window.refresh()

    def _state_pcb_removed(self):
        self.window["-QRCODE-"].update()
        self.window["-PASSFAIL-"].update("", background_color="black")
        self.window["-PASSFAIL_WRAPPER-"].Widget.config(background="black")
        self.window["-LOG-"].update("")
        self.window.refresh()

    def _state_serial_detected(self, serial):
        self.window["-STATE-"].update("Serial Detected, Waiting for PCB...")
        self.window["-QRCODE-"].update(data=generate_qrcode(serial))
        self.window["-PASSFAIL-"].update("", background_color="black")
        self.window["-PASSFAIL_WRAPPER-"].Widget.config(background="black")
        self.window.refresh()

    def _display_logs(self, log_queue, queue_handler):
        try:
            record = log_queue.get(block=False)
        except queue.Empty:
            pass
        else:
            msg = queue_handler.format(record)
            self.window["-LOG-"].update(msg + "\n", append=True)

    def run(self, log_queue, queue_handler):
        self._init_gui()

        threading.Thread(
            target=tester_thread, args=(self.window, self.dev), daemon=True
        ).start()

        while True:
            event, data = self.window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break
            if event == "waiting_for_serial":
                self._state_wait_for_serial()
            if event == "waiting_for_pcb":
                self._state_wait_for_pcb()
            if event == "provisioning":
                self._state_test_running()
            if event == "provisioning_failed":
                self._state_test_failed()
            if event == "provisioning_successful":
                self._state_test_passed(data["provisioning_successful"]["serial_no"])
            if event == "pcb_removed":
                self._state_pcb_removed()
            if event == "serial_detected":
                self._state_serial_detected(data["serial_detected"]["serial_no"])

            self._display_logs(log_queue=log_queue, queue_handler=queue_handler)

        self.window.close()


@click.command()
@click.option("--dev", default=lambda: JigClient.find_device())
@click.option("--debug", "-d", default=False, is_flag=True)
@click.option("--gui/--no-gui", default=True)
def main(dev: Optional[str], gui: bool, debug: bool):
    log_queue, queue_handler = configure_logging(debug, gui)

    if dev is None:
        print("Could not detect device")
        return

    if gui:
        app = App(dev)
        app.run(log_queue=log_queue, queue_handler=queue_handler)
    else:
        app = create_jig_tester(dev)
        app.run()


if __name__ == "__main__":
    try:
        main()
    except:
        logging.exception("Oops:")