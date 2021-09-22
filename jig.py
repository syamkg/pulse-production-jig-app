#!/usr/bin/env python3
import click
import logging
from pulse_jig.functional_test import FunctionalTest
from pulse_jig.jig_client import JigClient
from typing import Optional


@click.command()
@click.option("--dev", default=lambda: JigClient.find_device())
@click.option("--debug", "-d", default=False, is_flag=True)
def test_jig(dev: Optional[str], debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("transitions").setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger("transitions").setLevel(logging.WARN)

    if dev is None:
        print("Could not detect device")
        return

    ft = FunctionalTest(dev)
    ft.run()


if __name__ == "__main__":
    test_jig()
