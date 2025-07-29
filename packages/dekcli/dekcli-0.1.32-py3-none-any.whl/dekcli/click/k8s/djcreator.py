import typer
from .base.django import backup, restore, default_cluster

app = typer.Typer(add_completion=False)

default_suffix = 'djcreator-project-backend'


@app.command(name='backup')
def _backup(scope, name, dest, suffix=default_suffix, cluster=default_cluster):
    backup(f"{scope}-{name}", f"{name}-{suffix}", dest, cluster)


@app.command(name='restore')
def _restore(scope, name, src, suffix=default_suffix, cluster=default_cluster):
    restore(f"{scope}-{name}", f"{name}-{suffix}", src, cluster)
