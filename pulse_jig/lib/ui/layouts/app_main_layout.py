import PySimpleGUI as sg


def layout():
    sg.theme("Black")

    return [
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
                            pad=(4, (12, 4)),
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
            sg.Column(
                layout=[
                    [sg.Sizer(200, 0)],
                    [
                        sg.Frame(
                            "Network",
                            layout=[[sg.Text(key="-NETWORK-", font=("Arial", 12))], [sg.Sizer(0, 5)]],
                            expand_x=True,
                            element_justification="center",
                        )
                    ],
                ],
            ),
            sg.Column(
                layout=[
                    [sg.Sizer(400, 0)],
                    [
                        sg.Frame(
                            "Mode",
                            layout=[[sg.Text(key="-MODE-", font=("Arial", 10))], [sg.Sizer(0, 7)]],
                            expand_x=True,
                        )
                    ],
                ],
            ),
            sg.Column(
                layout=[
                    [sg.Sizer(200, 8)],
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
