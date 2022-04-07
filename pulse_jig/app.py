import logging
from registrar import Registrar
from jig_gui import JigGUI
import enum
import click
from typing import Optional
from jig_client import JigClient
from provisioner import Provisioner

logging.basicConfig(level=logging.DEBUG)


class Target(enum.Enum):
    PULSE = "pulse"
    PROBE = "probe"
    FAKE = "fake"


def _create_probe_provisioner(dev: str, registrar: Registrar, reset_pin: int, pcb_sense_pin: int) -> Provisioner:
    from probe_provisioner import ProbeProvisioner
    from pulse_manager import PulseManager

    pulse_manager = PulseManager(reset_pin=reset_pin, pcb_sense_pin=pcb_sense_pin, xdot_volume="/media/pi/XDOT")

    return ProbeProvisioner(registrar=registrar, pulse_manager=pulse_manager, dev=dev)


def _create_fake_provisioner(registrar: Registrar) -> Provisioner:
    from fake_provisioner import FakeProvisioner

    return FakeProvisioner(registrar)


def _parse_target(name: str) -> Target:
    targets = {"pulse-r1b": Target.PULSE, "ta3k": Target.PROBE, "fake": Target.FAKE}
    return targets[name]


def _configure_logging(transitions: bool, jig_client: bool):
    logging.getLogger("transitions").setLevel(logging.INFO if transitions else logging.ERROR)
    logging.getLogger("jig_client").setLevel(logging.INFO if jig_client else logging.ERROR)


@click.command()
@click.option(
    "--target",
    "-t",
    required=True,
    type=click.Choice(["pulse-r1b", "ta3k", "fake"], case_sensitive=False),
)
@click.option("--dev", default=lambda: JigClient.find_device())
@click.option("--debug", "-d", default=False, is_flag=True)
@click.option("--reset-pin", default=6)
@click.option("--pcb-sense-pin", default=5)
def main(target: str, dev: Optional[str], debug: bool, reset_pin: int, pcb_sense_pin: int):
    if dev is None:
        print("Could not detect device")
        exit(1)

    _configure_logging(transitions=debug, jig_client=True)

    registrar = Registrar()

    provider_target = _parse_target(target)
    if Target.PROBE == provider_target:
        provisioner = _create_probe_provisioner(
            dev=dev,
            registrar=registrar,
            reset_pin=reset_pin,
            pcb_sense_pin=pcb_sense_pin,
        )
    elif Target.FAKE == provider_target:
        provisioner = _create_fake_provisioner(registrar)
    elif Target.PULSE == provider_target:
        raise RuntimeError("Not implemented")
    else:
        raise RuntimeError("Invalid target")

    app = JigGUI()
    app.run(provisioner)


if __name__ == "__main__":
    main()
