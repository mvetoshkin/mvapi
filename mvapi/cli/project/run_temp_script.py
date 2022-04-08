import click
import importlib
import sys
import os


@click.command('run-temp-script')
@click.argument('path')
def run_temp_script(path):
    """Run a script from the temp category"""

    sys.path.append(os.getcwd())
    mod = importlib.import_module(f'temp.{path}')
    func = getattr(mod, path.split('.')[-1])
    func()
