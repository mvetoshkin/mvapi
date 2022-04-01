import click

from mvapi.web.libs.appfactory import create_app


@click.command('run', short_help='Run a development server')
@click.option('--host', '-h', help='The interface to bind to')
@click.option('--port', '-p', help='The port to bind to')
def run_(host, port):
    app = create_app()
    app.run(host=host, port=port, load_dotenv=False)
