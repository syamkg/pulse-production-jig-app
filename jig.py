#!/usr/bin/env python3
import click
import logging
from pulse_jig.functional_test import FunctionalTest


@click.command()
@click.argument('dev')
@click.option('--debug', '-d', default=False, is_flag=True)
def test_jig(dev: str, debug: bool):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('transitions').setLevel(logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
        logging.getLogger('transitions').setLevel(logging.WARN)
    ft = FunctionalTest(dev)
    ft.run()


if __name__ == '__main__':
    test_jig()
