import logging
import sys
from typing import Optional

import click

sys.path.append("..")

from pulse_jig.config import settings
from lib.jig_client import JigClient
from lib.ui.jig_gui import JigGUI
from lib.provisioner.provisioner import Provisioner
from lib.registrar import Registrar
from lib.pulse_manager import PulseManager


def _configure_logging(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="[%(asctime)s] [%(levelname)-5s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("transitions").setLevel(logging.INFO if debug else logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.WARN if debug else logging.ERROR)


@click.command()
@click.option("--dev", default=lambda: JigClient.find_device())
@click.option("--reset-pin", default=6)
@click.option("--pcb-sense-pin", default=5)
@click.option("--xdot-volume", default="/media/pi/XDOT")
def main(dev: Optional[str], reset_pin: int, pcb_sense_pin: int, xdot_volume: str):
    if dev is None:
        print("Could not detect device")
        exit(1)

    _configure_logging(settings.app.debug)

    registrar = Registrar()
    registrar.network_check()

    pulse_manager = PulseManager(reset_pin, pcb_sense_pin, xdot_volume)
    provisioner_factory = Provisioner.build_factory(registrar, pulse_manager, dev)

    app = JigGUI()
    app.run(provisioner_factory, registrar)


if __name__ == "__main__":
    main()
