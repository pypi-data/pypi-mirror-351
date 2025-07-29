import click

from .helpers import connect_cli, xnatpy_login_options


@click.group(name="rest")
def rest():
    """
    Perform various REST requests to the target XNAT.
    """


@rest.command()
@click.argument("path")
@click.option("--query", multiple=True, help="The values to be added to the query string in the URI.")
@click.option("--headers", multiple=True, help="HTTP headers to include.")
@xnatpy_login_options
def get(path, query, headers, **kwargs):
    """Perform GET request to the target XNAT."""
    if query:
        query = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), headers)}

    with connect_cli(no_parse_model=True, **kwargs) as session:
        result = session.get(path, query=query, headers=headers, timeout=kwargs.get("timeout"))
        click.echo("Result: {text}".format(text=result.text))
        click.echo("Path {path} {user}".format(path=path, user=kwargs.get("user")))


@rest.command()
@click.argument("path")
@click.option("--query", multiple=True, help="The values to be added to the query string in the URI.")
@click.option("--headers", multiple=True, help="HTTP headers to include.")
@xnatpy_login_options
def head(path, query, headers, **kwargs):
    """Perform HEAD request to the target XNAT."""
    if query:
        query = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), headers)}

    with connect_cli(no_parse_model=True, **kwargs) as session:
        result = session.head(path, query=query, headers=headers)
        click.echo("Result: {text}".format(text=result.text))
        click.echo("Path {path} {user}".format(path=path, user=kwargs.get("user")))


@rest.command()
@click.argument("path")
@click.option("--jsonpath", "-j", help="JSON payload file location.")
@click.option("--datapath", "-d", help="Data payload file location.")
@click.option("--query", multiple=True, help="The values to be added to the query string in the URI.")
@click.option("--headers", multiple=True, help="HTTP headers to include.")
@xnatpy_login_options
def post(path, jsonpath, datapath, query, headers, **kwargs):
    """Perform POST request to the target XNAT."""
    if jsonpath is not None:
        with open(jsonpath, "r") as json_file:
            json_payload = json_file.read()
    else:
        json_payload = None

    if datapath is not None:
        with open(datapath, "r") as data_file:
            data_payload = data_file.read()
    else:
        data_payload = None

    if query:
        query = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), headers)}

    with connect_cli(no_parse_model=True, **kwargs) as session:
        result = session.post(path, json=json_payload, data=data_payload, query=query, headers=headers)
        click.echo("Result: {text}".format(text=result.text))
        click.echo("Path {path} {user}".format(path=path, user=kwargs.get("user")))


@rest.command()
@click.argument("path")
@click.option("--jsonpath", "-j", help="JSON payload file location.")
@click.option("--datapath", "-d", help="Data payload file location.")
@click.option("--query", multiple=True, help="The values to be added to the query string in the URI.")
@click.option("--headers", multiple=True, help="HTTP headers to include.")
@xnatpy_login_options
def put(path, jsonpath, datapath, query, headers, **kwargs):
    """Perform PUT request to the target XNAT."""
    if jsonpath is not None:
        with open(jsonpath, "r") as json_file:
            json_payload = json_file.read()
    else:
        json_payload = None

    if datapath is not None:
        with open(datapath, "r") as data_file:
            data_payload = data_file.read()
    else:
        data_payload = None

    if query:
        query = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), headers)}

    with connect_cli(no_parse_model=True, **kwargs) as session:
        result = session.put(path, json=json_payload, data=data_payload, query=query, headers=headers)
        click.echo("Result: {text}".format(text=result.text))
        click.echo("Path {path} {user}".format(path=path, user=kwargs.get("user")))


@rest.command()
@click.argument("path")
@click.option("--query", multiple=True, help="The values to be added to the query string in the URI.")
@click.option("--headers", multiple=True, help="HTTP headers to include.")
@xnatpy_login_options
def delete(path, query, headers, **kwargs):
    """Perform DELETE request to the target XNAT."""
    if query:
        query = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), query)}

    if headers:
        headers = {arg[0]: arg[1] for arg in map(lambda x: x.split("="), headers)}

    with connect_cli(no_parse_model=True, **kwargs) as session:
        result = session.delete(path, query=query, headers=headers)
        click.echo("Result: {text}".format(text=result.text))
        click.echo("Path {path} {user}".format(path=path, user=kwargs.get("user")))
