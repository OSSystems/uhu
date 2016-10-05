# Copyright (C) 2016 O.S. Systems Software LTDA.
# This software is released under the MIT License

import click

from .config import config_cli, cleanup_command
from .hardware import hardware_cli
from .package import package_cli
from .product import product_cli


@click.group()
def cli():
    ''' EasyFOTA utility '''


# General commands
cli.add_command(cleanup_command)

# Subcommands
cli.add_command(config_cli)
cli.add_command(hardware_cli)
cli.add_command(package_cli)
cli.add_command(product_cli)
