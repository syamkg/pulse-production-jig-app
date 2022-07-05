import PySimpleGUI as sg

from pulse_jig.config import settings

repair_mode_warning = []
if settings.app.hwspec_repair_mode:
    repair_mode_warning = [
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
                                    sg.Frame(
                                        "",
                                        layout=[
                                            *repair_mode_warning,
                                            [
                                                sg.Text("Manufacturer: "),
                                                sg.Text(settings.device.manufacturer_name, text_color="gray"),
                                            ],
                                            [sg.Sizer(0, 10)],
                                            [
                                                sg.Text("Device: "),
                                                sg.Text(settings.device.thing_type_name, text_color="gray"),
                                            ],
                                            [sg.Sizer(0, 10)],
                                            [
                                                sg.Text("Cable Length (m)"),
                                                sg.Combo(
                                                    ["--Select one--"] + settings.device.cable_lengths,
                                                    key="-CABLE_LENGTH-",
                                                    default_value="--Select one--",
                                                    readonly=True,
                                                    background_color="white",
                                                    text_color="black",
                                                    expand_x=True,
                                                    font=("Arial", 20),
                                                ),
                                            ],
                                            [sg.Sizer(0, 20)],
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
                                                    expand_y=True,
                                                )
                                            ],
                                            [
                                                sg.Text(
                                                    f"v{settings.VERSION}",
                                                    text_color="gray",
                                                    justification="right",
                                                    expand_x=True,
                                                    expand_y=True,
                                                    font=("Arial", 12),
                                                )
                                            ],
                                        ],
                                        border_width=0,
                                        pad=(60, 50),
                                        expand_x=True,
                                        expand_y=True,
                                    )
                                ]
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
