import click
from click import core, Group

from aim._ext.cli.version import commands as version_commands
from aim._ext.cli.conatiners import commands as container_commands
from aim._ext.cli.upload import commands as upload_commands
from aim._ext.cli.login import commands as login_commands

try:
    from aim._ext.cli.init import commands as init_commands
except ImportError:
    init_commands = None

try:
    from aim._ext.cli.ui import commands as ui_commands
except ImportError:
    ui_commands = None

try:
    from aim._ext.cli.server import commands as server_commands
except ImportError:
    server_commands = None

try:
    from aim._ext.cli.migrate import commands as migrate_commands
except ImportError:
    migrate_commands = None

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from click import Context

core._verify_python3_env = lambda: None


class CommandOrderedGroup(Group):
    def get_help(self, ctx: 'Context') -> str:
        ctx.terminal_width = 120
        return super().get_help(ctx)

    def list_commands(self, ctx: 'Context'):
        # Return commands in the order of their definition
        return self.commands


@click.group(cls=CommandOrderedGroup)
def cli_entry_point():
    """
    The main entry point for Aim CLI: a toolset for tracking and managing machine learning experiments.

    The Aim CLI provides a suite of commands to facilitate the tracking, visualization,
    and management of machine learning experiments. The toolset is designed to seamlessly
    integrate with various stages of the ML workflow, from initializing repositories and
    tracking experiments in real-time, to visualizing results through the UI and managing
    custom packages or apps.
    """


if init_commands:
    cli_entry_point.add_command(init_commands.init)
if server_commands:
    cli_entry_point.add_command(server_commands.server)
if ui_commands:
    cli_entry_point.add_command(ui_commands.ui)
cli_entry_point.add_command(container_commands.containers)
if migrate_commands:
    cli_entry_point.add_command(migrate_commands.migrate)

cli_entry_point.add_command(upload_commands.upload)
cli_entry_point.add_command(login_commands.login)
cli_entry_point.add_command(version_commands.version)
