import PySimpleGUI as sg

from lib.target import Target
from pulse_jig.config import settings


def repair_mode_warning() -> list:
    warning = []
    if settings.app.hwspec_repair_mode:
        warning = [
            [
                sg.Text(
                    "WARNING: Repair mode is active!",
                    justification="center",
                    text_color="white",
                    background_color="red",
                    font=("Arial", 15),
                    expand_x=True,
                ),
            ],
            [sg.Sizer(0, 10)],
        ]
    return warning


def mode_selection_elements() -> list:
    # Dynamically build the UI elements for the items in
    # the `mode_vars` config item. If the item value is a list
    # then a dropdown will be built & just a text field
    # for a string/number value
    elements = []
    if settings.mode_vars:
        for key in settings.mode_vars:
            if isinstance(settings.mode_vars.get(key), list):
                element = [
                    sg.Text(key.replace("_", " ").title()),
                    sg.Combo(
                        ["--Select one--"] + settings.mode_vars.get(key),
                        key=f"-{key.upper()}-",
                        default_value="--Select one--",
                        readonly=True,
                        background_color="white",
                        text_color="black",
                        expand_x=True,
                        font=("Arial", 20),
                    ),
                ]
                elements.append(element)
                elements.append([sg.Sizer(0, 20)])
            else:
                element = [
                    sg.Text(key.replace("_", " ").title() + ": "),
                    sg.Text(settings.mode_vars.get(key), key=f"-{key.upper()}-", text_color="gray"),
                ]
                elements.append(element)
                elements.append([sg.Sizer(0, 10)])
    return elements


def target_element():
    if not settings.app.allow_target_change:
        return [sg.Text(settings.app.target, key="-TARGET-", text_color="gray")]
    else:
        return (
            sg.Combo(
                [e.value for e in Target],
                key="-TARGET-",
                default_value=settings.app.target,
                readonly=True,
                background_color="white",
                text_color="black",
                expand_x=True,
                font=("Arial", 20),
            ),
        )


def layout():
    sg.theme("Black")

    return [
        [
            sg.Column(
                layout=[
                    [
                        sg.Frame(
                            "Please set the following value(s)",
                            layout=[
                                [
                                    sg.Sizer(0, 380),
                                    sg.Frame(
                                        "",
                                        layout=[
                                            *repair_mode_warning(),
                                            [
                                                sg.Text("Manufacturer: "),
                                                sg.Text(settings.device.manufacturer_name, text_color="gray"),
                                            ],
                                            [sg.Sizer(0, 10)],
                                            [
                                                sg.Text("Target: "),
                                                *target_element(),
                                            ],
                                            [sg.Sizer(0, 10)],
                                            *mode_selection_elements(),
                                            [
                                                sg.Button(
                                                    "Set Mode",
                                                    key="-SET_MODE-",
                                                    button_color="green",
                                                    expand_x=True,
                                                    size=(20, 2),
                                                )
                                            ],
                                            [sg.Sizer(0, 10)],
                                            [
                                                sg.Text(
                                                    "",
                                                    key="-ERROR-",
                                                    text_color="red",
                                                    justification="center",
                                                    expand_x=True,
                                                )
                                            ],
                                        ],
                                        border_width=0,
                                        pad=(60, 10),
                                        expand_x=True,
                                        vertical_alignment="center",
                                    ),
                                ],
                                [
                                    sg.Text(
                                        f"v{settings.VERSION}",
                                        text_color="gray",
                                        justification="right",
                                        expand_x=True,
                                        font=("Arial", 12),
                                        pad=(30, 0),
                                    )
                                ],
                            ],
                            font=("Arial", 22),
                            title_location=sg.TITLE_LOCATION_TOP,
                            expand_x=True,
                            expand_y=True,
                        )
                    ],
                ],
                expand_x=True,
                expand_y=True,
            )
        ],
    ]
