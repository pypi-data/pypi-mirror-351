from dektools.typer import command_version
from . import app
from .gitea import app as gitea_app
from .k8s import app as k8s_app
from .smb import app as smb_app
from .pybuild import app as pybuild_app
from .v2ray import app as v2ray_app

command_version(app, __name__)
app.add_typer(gitea_app, name='gitea')
app.add_typer(k8s_app, name='k8s')
app.add_typer(smb_app, name='smb')
app.add_typer(pybuild_app, name='pybuild')
app.add_typer(v2ray_app, name='v2ray')


def main():
    app()
