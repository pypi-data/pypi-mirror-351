import typer
from getpass import getpass
from .base import get_cfg, default_cluster
from .djcreator import app as djcreator_app
from .dekspider import app as dekspider_app

app = typer.Typer(add_completion=False)

app.add_typer(djcreator_app, name='djcreator')
app.add_typer(dekspider_app, name='dekspider')


@app.command()
def login(host, port: int = 6443, token='', cluster=default_cluster):
    token = token or getpass('Please input a token:')
    get_cfg(cluster).update(dict(host=host, token=token, port=port))
