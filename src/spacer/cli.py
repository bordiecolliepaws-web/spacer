import click
from .init import init_cmd
from .status import status_cmd
from .bib import bib_group
from .auth import auth_cmd
from .chat import chat_cmd

@click.group()
def cli():
    """SPACER — research paper pipeline management."""
    pass

cli.add_command(init_cmd, "init")
cli.add_command(status_cmd, "status")
cli.add_command(bib_group, "bib")
cli.add_command(auth_cmd, "auth")
cli.add_command(chat_cmd, "chat")
