from pathlib import Path
from dektools.shell import shell_wrapper
from dektools.cfg import ObjectCfg
from dektools.file import remove_path

path_server = Path(__file__).parent / 'server.pysh'

workdir = ObjectCfg(__name__, 'v2ray', module=True).path_dir


def run_server(port=None):
    shell_wrapper(f'dekshell rf {path_server} "{workdir}" {port or ""}')


def clean_server():
    remove_path(workdir)
