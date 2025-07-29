import click

from .helpers import connect_cli, xnatpy_all_options


@click.group(name="prearchive")
def prearchive():
    """
    Commands for prearchive management.
    """


@prearchive.command()
@xnatpy_all_options
def list(**kwargs):
    """
    List all sessions currently in prearchive.
    """
    with connect_cli(no_parse_model=True, **kwargs) as session:
        for sess in session.prearchive.sessions():
            click.echo(sess.cli_str())


@prearchive.command()
@click.option("--project", "-p", help="Project the session belongs to.")
@click.option("--label", "-l", help="Session label.")
@click.option("--subject", "-s", help="Session subject.")
@click.option("--status", help="Session status.")
@xnatpy_all_options
def delete(project, label, subject, status, **kwargs):
    """Delete selected prearchive sessions."""
    with connect_cli(**kwargs) as session:
        selected_sessions = session.prearchive.find(project=project, subject=subject, label=label, status=status)
        if not selected_sessions:
            session.logger.warning("No prearchive sessions have been selected based on your criteria!")
        else:
            for sess in selected_sessions:
                session.logger.debug("Deleting session {}".format(session.label))
                sess.delete()
            session.logger.debug("Finished deleting selected prearchive sessions!")


@prearchive.command()
@click.option("--project", "-p", help="Project the sessions currently belong to.")
@click.option("--dest-project", help="Destination project.")
@click.option("--label", "-l", "Session label.")
@click.option("--subject", "-s", "Session subject.")
@click.option("--status", "Session status.")
@xnatpy_all_options
def move(project, dest_project, label, subject, status, **kwargs):
    """Move selected prearchive sessions."""
    with connect_cli(**kwargs) as session:
        selected_sessions = session.prearchive.find(project=project, subject=subject, label=label, status=status)
        if not selected_sessions:
            session.logger.warning("No prearchive sessions have been selected based on your criteria!")
        else:
            for sess in selected_sessions:
                session.logger.debug("Moving session {}".format(session.label))
                sess.move(dest_project)
            session.logger.debug("Finished moving selected prearchive sessions!")


@prearchive.command()
@click.argument("--sessionid")
@click.argument("--project")
@click.option("--subject", help="The subject in the archive to assign the content to.")
@click.option("--experiment", help="The experiment in the archive to assign the session content to.")
@click.option("--overwrite", help="Action to take in case data already exists. Possible values: none, append, delete.")
@click.option("--quarantine", is_flag=True, help="Indicate whether the session should be quarantined.")
@click.option("--trigger-pipelines", is_flag=True, help="Indicate whether archiving should trigger pipelines.")
@xnatpy_all_options
def archive(sessionid, project, subject, experiment, overwrite, quarantine, trigger_pipelines, **kwargs):
    """Archive selected prearchive session."""
    with connect_cli(**kwargs) as session:
        selected_session = None
        for sess in session.prearchive.sessions:
            if sess.id == sessionid:
                selected_session = sess
                break

        if not selected_session:
            session.logger.warning("No prearchive sessions have been selected based on your criteria!")
        else:
            session.logger.debug("Archiving session {}".format(session.label))
            sess.archive(
                project=project,
                subject=subject,
                experiment=experiment,
                overwrite=overwrite,
                quarantine=quarantine,
                trigger_pipelines=trigger_pipelines,
            )
            session.logger.debug("Finished archiving!")


prearchive.command()


@click.option("--project", "-p", help="Project the session belongs to.")
@click.option("--label", "-l", help="Session label.")
@click.option("--subject", "-s", help="Session subject.")
@click.option("--status", help="Session status.")
@click.option("--overwrite", help="Action to take in case data already exists. Possible values: none, append, delete.")
@click.option("--quarantine", is_flag=True, help="Indicate whether the session should be quarantined.")
@click.option("--trigger-pipelines", is_flag=True, help="Indicate whether archiving should trigger pipelines.")
@xnatpy_all_options
def bulk_archive(project, label, subject, status, overwrite, quarantine, trigger_pipelines, **kwargs):
    """Archive multiple selected prearchive sessions."""
    with connect_cli(**kwargs) as session:
        selected_sessions = session.prearchive.find(project=project, subject=subject, label=label, status=status)
        if not selected_sessions:
            session.logger.warning("No prearchive sessions have been selected based on your criteria!")
        else:
            for sess in selected_sessions:
                session.logger.debug("Archiving session {}".format(session.label))
                sess.archive(overwrite=overwrite, quarantine=quarantine, trigger_pipelines=trigger_pipelines)
            session.logger.debug("Finished archiving selected prearchive sessions!")
