#!/usr/bin/env python

'''
This is a placeholder application demonstrating how PySimpleGUI can accept controls from both a user
and a TBD test harness. It has the currently understood wait/test/display QR loop.

It runs fullscreen with no capability to exit and is intended to be run on boot on an RPI with a touchscreen.
'''

import PySimpleGUI as sg
import qrcode
import time
import io
import uuid

sg.theme('Black')

layout = [
  [ sg.Text(key='-STATUS-') ],
  [ sg.Text(key='-PASSFAIL-', font='Helvetica 20 bold') ],
  [ sg.Image(key='-QRCODE-') ]
]

window = sg.Window(
  'Pulse Production Jig',
  layout,
  element_justification='center',
  finalize=True
)
window.maximize()

def testing_result(run):
  success = run % 2
  serial = str(uuid.uuid4()) if success else None 
  return (success, serial)

def generate_qrcode(text):
  img = qrcode.make(text)
  bio = io.BytesIO()
  img.get_image().save(bio, format='PNG')
  return bio.getvalue()

def state_waiting():
  window['-STATUS-'].update('Waiting for device')
  window.refresh()

def state_testing():
  window['-STATUS-'].update('Running tests')
  window.refresh()

def state_fail():
  window['-PASSFAIL-'].update('Fail', text_color='red')
  window['-QRCODE-'].update(None)
  window.refresh()

def state_success(serial):
  window['-PASSFAIL-'].update('Pass', text_color='green')
  window['-QRCODE-'].update(data=generate_qrcode(serial))
  window.refresh()

def perform_device_testing(count):
  state_waiting()
  time.sleep(1) # pretend to do something...
  state_testing()
  time.sleep(1)
  (success, serial) = testing_result(count)
  state_success(serial) if success else state_fail()


count=0
while True:
  # perform a blocking read for 10ms so that when we're not running the tests
  # a user can interact with the program
  event, values = window.read(timeout=10)
  if event == sg.WIN_CLOSED:
    break
  # if other GUI interaction events: ...

  # perform device testing loop
  perform_device_testing(count)
  count += 1


window.close()
