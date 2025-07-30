import os
import sys
from dektools.file import remove_path, read_file
from dektools.shell import shell_wrapper, shell_exitcode
from dekvenv.active import dir_name_venv, activate_venv
from dekmedia.image.core import resize_image
from dekmedia.image.svg import load_svg

builder = "python -m nuitka"
name_for_entry = 'main'
path_for_res = 'res'
name_of_icon = name_for_entry

default_data = dict(
    name=name_for_entry
)


def build_target(path, data=None):
    data = default_data | (data or {})
    path_last = os.getcwd()
    os.chdir(path)
    activate_venv(os.path.join(path, dir_name_venv))
    if shell_exitcode(f"{builder} --help"):
        raise ChildProcessError(f"Nuitka is not found in target virtualenv.")
    for fn in ['build', 'dist']:
        remove_path(os.path.join(path, f"{data['name']}.{fn}"))
    command = [
        builder,
        f"{name_for_entry}.py",
        "--standalone",
        "--disable-console",
        f"--product-name={data['name']}",
        f"--output-filename={data['name']}"
    ]
    if 'version' in data:
        command.append(f"--product-version={data['version']}")
    if 'description' in data:
        command.append(f"--file-description={data['description']}")
    if os.path.isdir(os.path.join(path, path_for_res)):
        command.append(f"--include-package-data={path_for_res}")
    icon_svg = f"{name_of_icon}.svg"
    if sys.platform == "darwin":
        icon_src = f"{name_of_icon}.icns"
        if os.path.isfile(icon_svg):
            resize_image(load_svg(read_file(icon_svg)), icon_src, [(256, 256)])
        if os.path.isfile(icon_src):
            command.append(f"--macos-app-icon={icon_src}")
    elif sys.platform == 'win32':
        icon_src = f"{name_of_icon}.ico"
        if os.path.isfile(icon_svg):
            resize_image(load_svg(read_file(icon_svg)), icon_src, [(256, 256)])
        if os.path.isfile(icon_src):
            command.append(f"--windows-icon-from-ico={icon_src}")
    shell_wrapper(" ".join(command))
    os.chdir(path_last)
