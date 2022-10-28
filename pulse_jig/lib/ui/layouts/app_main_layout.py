import PySimpleGUI as sg

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
                    font=("Arial", 11),
                    expand_x=True,
                ),
            ],
        ]
    return warning


def layout():
    sg.theme("Black")

    return [
        [
            *repair_mode_warning(),
            sg.Column(
                layout=[
                    [sg.Sizer(482, 0)],
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
                                ],
                                [sg.HorizontalSeparator(color="gray")],
                                [
                                    sg.Text(
                                        f"Jig App: v{settings.VERSION}",
                                        font=("Courier New", 8, "bold"),
                                    ),
                                    sg.Text(
                                        key="-TEST_FIRMWARE_VERSION-",
                                        font=("Courier New", 8, "bold"),
                                    ),
                                    sg.Text(
                                        key="-PROD_FIRMWARE_VERSION-",
                                        font=("Courier New", 8, "bold"),
                                    ),
                                ],
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
                    [sg.Sizer(306, 0)],
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
                            pad=(3, (12, 3)),
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
                expand_y=True,
                expand_x=True,
            ),
        ],
        [
            sg.Column(
                layout=[
                    [
                        sg.Frame(
                            "Network",
                            layout=[[sg.Text(key="-NETWORK-", font=("Arial", 12))]],
                            expand_x=True,
                            element_justification="center",
                            size=(160, 55),
                        )
                    ],
                ],
            ),
            sg.Column(
                layout=[
                    [
                        sg.Frame(
                            "Mode",
                            layout=[
                                [
                                    sg.Multiline(
                                        key="-MODE-",
                                        font=("Arial", 10),
                                        disabled=True,
                                        border_width=0,
                                        background_color="black",
                                        expand_x=True,
                                        expand_y=True,
                                        no_scrollbar=True,
                                        pad=(3, 0),
                                    )
                                ]
                            ],
                            expand_x=True,
                            size=(360, 55),
                        )
                    ],
                ],
            ),
            sg.Column(
                layout=[
                    [sg.Sizer(80, 8)],
                    [
                        sg.Button(
                            "Reset",
                            key="-RESET-",
                            font=("Arial", 12),
                            expand_x=True,
                            expand_y=True,
                            disabled=True,
                        ),
                        sg.Sizer(0, 52),
                    ],
                ],
                expand_x=True,
            ),
            sg.Column(
                layout=[
                    [sg.Sizer(160, 8)],
                    [
                        sg.Button(
                            "Change Mode",
                            key="-CHANGE_MODE-",
                            font=("Arial", 12),
                            expand_x=True,
                            expand_y=True,
                        ),
                        sg.Sizer(0, 52),
                    ],
                ],
                expand_x=True,
            ),
        ],
    ]
