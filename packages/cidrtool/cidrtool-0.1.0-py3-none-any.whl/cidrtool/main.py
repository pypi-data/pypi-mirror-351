import click

from cidrtool.commands.expr import expr
from cidrtool.commands.merge_cidr import merge_cidr
from cidrtool.commands.show import show


@click.group()
def cidrtool():
    """CIDR calulation tool"""
    pass


cidrtool.add_command(expr)
cidrtool.add_command(merge_cidr)
cidrtool.add_command(show)
