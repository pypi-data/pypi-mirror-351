import typer
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)


@app.command()
def serve(port: Annotated[str, typer.Argument()] = ''):
    from ..core.v2ray import run_server
    run_server(port)


@app.command()
def clean():
    from ..core.v2ray import clean_server
    clean_server()
