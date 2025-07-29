import os
import typing
import toml
import typer
from typing_extensions import Annotated
from dektools.typer import multi_options_to_dict
from dektools.file import read_text
from ..core.pyinstaller.core import build_target as pyinstaller_build_target
from ..core.nuitka.core import build_target as nuitka_build_target

app = typer.Typer(add_completion=False)


@app.command()
def pyinstaller(
        path: Annotated[str, typer.Argument()] = '',
        kw: typing.Optional[typing.List[str]] = typer.Option(None)
):
    if not path:
        path = os.getcwd()
    kwargs = multi_options_to_dict(kw)
    pyinstaller_build_target(path, get_meta_info(path) | kwargs)


@app.command()
def nuitka(
        path: Annotated[str, typer.Argument()] = '',
        kw: typing.Optional[typing.List[str]] = typer.Option(None)
):
    if not path:
        path = os.getcwd()
    kwargs = multi_options_to_dict(kw)
    nuitka_build_target(path, get_meta_info(path) | kwargs)


def get_meta_info(path):
    data = toml.loads(read_text(os.path.join(path, 'pyproject.toml')))
    return dict(
        name=data['project']['name'],
        version=data['project']['version'],
        description=data['project']['description'],
    )
