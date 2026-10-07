import os
import subprocess
import sys
import click
from flask import Blueprint

bp = Blueprint('cli', __name__, cli_group=None)

@bp.cli.group()
def translate():
    """Translation and localization commands."""


def run_babel(*args):
    subprocess.run(
        [sys.executable, '-m', 'babel.messages.frontend', *args],
        check=True,
    )


@translate.command()
def update():
    """Update all languages."""
    run_babel('extract', '-F', 'babel.cfg', '-k', '_l', '-o', 'messages.pot', '.')
    run_babel('update', '-i', 'messages.pot', '-d', 'app/translations')
    os.remove('messages.pot')

@translate.command()
def compile():
    """Compile all languages."""
    run_babel('compile', '-d', 'app/translations')

@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    run_babel('extract', '-F', 'babel.cfg', '-k', '_l', '-o', 'messages.pot', '.')
    run_babel('init', '-i', 'messages.pot', '-d', 'app/translations', '-l', lang)
    os.remove('messages.pot')






    