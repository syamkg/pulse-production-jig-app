#!/usr/bin/env python
'''
This is a placeholder application demonstrating how PySimpleGUI can accept
controls from both a user and a TBD test harness. It has the currently
understood wait/test/display QR loop.

It runs fullscreen with no capability to exit and is intended to be run on
boot on an RPI with a touchscreen.
'''

import PySimpleGUI as sg
import qrcode
import io
from pulse_jig.functional_test import FunctionalTest
import threading
import logging
import click


def tester_thread(window: sg.Window, dev: str):
    ft = FunctionalTest(dev)

    def handler(event, data):
        window.write_event_value(event, data)

    ft.add_listener(handler)
    ft.run()


def generate_qrcode(serial: str):
    img = qrcode.make(serial)
    bio = io.BytesIO()
    img.get_image().save(bio, format='PNG')
    return bio.getvalue()


class App:
    def __init__(self, dev: str):
        self.window = None
        self.dev = dev

    def _init_gui(self):
        sg.theme('Black')
        layout = [
            [
                sg.Frame("State",
                         layout=[[sg.Text(key='-STATE-', font='Helvetica 20 bold')]],
                         expand_x=True),
                sg.Frame("Test Status",
                         layout=[[sg.Text(key='-PASSFAIL-', font='Helvetica 20 bold')]],
                         expand_x=False)
            ],
            [sg.Frame("QRCode",
                      layout=[[sg.Image(key='-QRCODE-', expand_x=True, expand_y=True)]],
                      element_justification="center",
                      vertical_alignment='center',
                      expand_x=True,
                      expand_y=True)
             ]]

        self.window = sg.Window(
            'Pulse Production Jig',
            layout,
            element_justification='center',
            resizable=True,
            finalize=True)
        self.window.maximize()
        self.window.refresh()

    def _state_wait_for_serial(self):
        self.window['-STATE-'].update("Waiting for serial...")
        self.window.refresh()

    def _state_wait_for_pcb(self):
        self.window['-STATE-'].update("Waiting for PCB...")
        self.window.refresh()

    def _state_test_running(self):
        self.window['-STATE-'].update("Running test...")
        self.window.refresh()

    def _state_test_passed(self, serial):
        self.window['-PASSFAIL-'].update('Pass', background_color='green')
        self.window['-QRCODE-'].update(data=generate_qrcode(serial))
        self.window['-STATE-'].update("Disconnect PCB...")
        self.window.refresh()

    def _state_test_failed(self, serial):
        self.window['-PASSFAIL-'].update('Failed', background_color='Red')
        self.window['-QRCODE-'].update()
        self.window['-STATE-'].update("Disconnect PCB...")
        self.window.refresh()

    def _state_test_finished(self):
        self.window['-QRCODE-'].update()
        self.window['-PASSFAIL-'].update('', background_color="black")
        self.window.refresh()

    def _state_serial_detected(self, serial):
        self.window['-STATE-'].update("Serial Detected, Waiting for PCB...")
        self.window['-QRCODE-'].update(data=generate_qrcode(serial))
        self.window['-PASSFAIL-'].update('', background_color="black")
        self.window.refresh()

    def run(self):
        self._init_gui()

        threading.Thread(
            target=tester_thread,
            args=(self.window, self.dev),
            daemon=True).start()

        while True:
            event, data = self.window.read(timeout=500)
            if event == sg.WIN_CLOSED:
                break
            if event == "waiting_for_serial":
                self._state_wait_for_serial()
            if event == "waiting_for_pcb":
                self._state_wait_for_pcb()
            if event == "running_test":
                self._state_test_running()
            if event == "test_failed":
                self._state_test_failed()
            if event == "test_passed":
                self._state_test_passed(data['test_passed'])
            if event == "test_finished":
                self._state_test_finished()
            if event == "serial_detected":
                self._state_serial_detected(data['serial_detected'])

        self.window.close()


@click.command()
@click.argument('dev')
@click.option('--debug', '-d', default=False, is_flag=True)
def main(dev: str, debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('transitions').setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('transitions').setLevel(logging.WARN)
    app = App(dev)
    app.run()


if __name__ == '__main__':
    main()
