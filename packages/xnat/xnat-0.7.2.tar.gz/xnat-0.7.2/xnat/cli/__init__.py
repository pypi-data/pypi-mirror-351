import sys

import click

from .download import download
from .helpers import connect_cli, xnatpy_all_options, xnatpy_common_options, xnatpy_login_options
from .importing import importing
from .listings import listings
from .prearchive import prearchive
from .rest import rest
from .scripts import script
from .search import search
from .upload import upload


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@xnatpy_login_options
def login(**kwargs):
    """
    Establish a connection to XNAT and print the JSESSIONID so it can be used in sequent calls.
    The session is purposefully not closed so will live for next commands to use until it will
    time-out.
    """
    with connect_cli(**kwargs) as session:
        click.echo(session.jsession)


@cli.command()
@click.pass_context
def logout(**kwargs):
    """
    Close your current connection to XNAT.
    """
    with connect_cli(cli=False, **kwargs) as session:
        pass
    click.echo("Disconnected from {host}!".format(host=kwargs["host"]))


def load_sub_commands():
    # Load default subcommands shipped with xnatpy
    cli.add_command(download)
    cli.add_command(upload)
    cli.add_command(listings)
    cli.add_command(importing)
    cli.add_command(search)
    cli.add_command(rest)
    cli.add_command(script)
    cli.add_command(prearchive)

    # Load plugins via entrypoints
    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    discovered_plugins = entry_points(group="xnat.cli")

    for entry_point in discovered_plugins:
        print(f"Trying entrypoint {entry_point}")
        try:
            found_object = entry_point.load()
        except (ModuleNotFoundError, AttributeError) as exception:
            print(f"Encountered error loading plugin from {entry_point.value}: {exception}")
            continue

        if isinstance(found_object, (click.core.Command, click.core.Group)):
            cli.add_command(found_object)
        else:
            print(f"Encountered error loading plugin from {entry_point.value}: Not a valid click group!")


# Make sure we register all subcommands
load_sub_commands()


if __name__ == "__main__":
    cli()
