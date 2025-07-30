import typer
from .base.django import backup, restore, default_cluster

app = typer.Typer(add_completion=False)

default_namespace = 'pypi-dekspider'
default_suffix = 'dekspider-project'


@app.command(name='backup')
def _backup(name, dest, namespace=default_namespace, suffix=default_suffix, cluster=default_cluster):
    backup(namespace, f"{name}-{suffix}", dest, cluster)


@app.command(name='restore')
def _restore(name, src, namespace=default_namespace, suffix=default_suffix, cluster=default_cluster):
    restore(namespace, f"{name}-{suffix}", src, cluster)
