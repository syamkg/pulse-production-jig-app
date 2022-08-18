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
from lib.target import Target


def _create_probe_provisioner(dev: str, registrar: Registrar, reset_pin: int, pcb_sense_pin: int) -> Provisioner:
    from lib.provisioner.probe_provisioner import ProbeProvisioner
    from lib.pulse_manager import PulseManager

    pulse_manager = PulseManager(reset_pin=reset_pin, pcb_sense_pin=pcb_sense_pin, xdot_volume="/media/pi/XDOT")

    return ProbeProvisioner(registrar=registrar, pulse_manager=pulse_manager, dev=dev)


def _create_pulse_provisioner_phase_1(
    dev: str, registrar: Registrar, reset_pin: int, pcb_sense_pin: int
) -> Provisioner:
    from lib.provisioner.pulse_provisioner_phase_1 import PulseProvisionerPhase1
    from lib.pulse_manager import PulseManager

    pulse_manager = PulseManager(reset_pin=reset_pin, pcb_sense_pin=pcb_sense_pin, xdot_volume="/media/pi/XDOT")

    return PulseProvisionerPhase1(registrar=registrar, pulse_manager=pulse_manager, dev=dev)


def _create_pulse_provisioner_phase_2(
    dev: str, registrar: Registrar, reset_pin: int, pcb_sense_pin: int
) -> Provisioner:
    from lib.provisioner.pulse_provisioner_phase_2 import PulseProvisionerPhase2
    from lib.pulse_manager import PulseManager

    pulse_manager = PulseManager(reset_pin=reset_pin, pcb_sense_pin=pcb_sense_pin, xdot_volume="/media/pi/XDOT")

    return PulseProvisionerPhase2(registrar=registrar, pulse_manager=pulse_manager, dev=dev)


def _create_fake_provisioner(registrar: Registrar) -> Provisioner:
    from lib.provisioner.fake_provisioner import FakeProvisioner

    return FakeProvisioner(registrar)


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
def main(dev: Optional[str], reset_pin: int, pcb_sense_pin: int):
    if dev is None:
        print("Could not detect device")
        exit(1)

    _configure_logging(settings.app.debug)

    registrar = Registrar()
    registrar.network_check()

    target = settings.app.target

    if Target.TA3K == target:
        provisioner = _create_probe_provisioner(
            dev=dev,
            registrar=registrar,
            reset_pin=reset_pin,
            pcb_sense_pin=pcb_sense_pin,
        )
    elif Target.PULSE_R1B_PHASE_1 == target:
        provisioner = _create_pulse_provisioner_phase_1(
            dev=dev,
            registrar=registrar,
            reset_pin=reset_pin,
            pcb_sense_pin=pcb_sense_pin,
        )
    elif Target.PULSE_R1B_PHASE_2 == target:
        provisioner = _create_pulse_provisioner_phase_2(
            dev=dev,
            registrar=registrar,
            reset_pin=reset_pin,
            pcb_sense_pin=pcb_sense_pin,
        )
    elif Target.FAKE == target:
        provisioner = _create_fake_provisioner(registrar)
    else:
        raise RuntimeError("Invalid target")

    app = JigGUI()
    app.run(provisioner, registrar)


if __name__ == "__main__":
    main()
