import click

from xnat import exceptions

from .helpers import connect_cli, xnatpy_all_options


@click.group(name="import")
def importing():
    """
    Commands to import data from your machine into XNAT
    """


@importing.command()
@click.argument("folder")
@click.option("--destination", help="The destination to upload the scan to.")
@click.option(
    "--project", help="The project in the archive to assign the session to (only accepts project ID, not a label)."
)
@click.option("--subject", help="The subject in the archive to assign the session to.")
@click.option("--experiment", help="The experiment in the archive to assign the session content to.")
@click.option("--import_handler")
@click.option("--quarantine", is_flag=True, help="Flag to indicate session should be quarantined.")
@click.option("--trigger_pipelines", is_flag=True, help="Indicate that importing should trigger pipelines.")
@xnatpy_all_options
def experiment(
    folder, destination, project, subject, experiment, import_handler, quarantine, trigger_pipelines, **kwargs
):
    """Import experiment from the target folder to XNAT"""
    try:
        with connect_cli(no_parse_model=True, **kwargs) as session:
            session.services.import_dir(
                folder,
                quarantine=quarantine,
                destination=destination,
                trigger_pipelines=trigger_pipelines,
                project=project,
                subject=subject,
                experiment=experiment,
                import_handler=import_handler,
            )
            session.logger.info("Import complete!")
    except exceptions.XNATLoginFailedError:
        print(f"ERROR Failed to login")
