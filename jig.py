#!/usr/bin/env python3
import click
import logging
from pulse_jig.functional_test import FunctionalTest


@click.command()
@click.argument('dev')
def test_jig(dev: str):
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('transitions').setLevel(logging.INFO)
    ft = FunctionalTest(dev)
    ft.run()


if __name__ == '__main__':
    test_jig()
