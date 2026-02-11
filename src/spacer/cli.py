import click
from .init import init_cmd
from .status import status_cmd
from .bib import bib_group

@click.group()
def cli():
    """SPACER — research paper pipeline management."""
    pass

cli.add_command(init_cmd, "init")
cli.add_command(status_cmd, "status")
cli.add_command(bib_group, "bib")
