import copy
import click

import os
import sys
import pathlib
from types import ModuleType

from archtool.dependency_injector import DependencyInjector

# DIRECTORY_PATH = pathlib.Path.cwd()
# os.chdir((DIRECTORY_PATH / "dp").as_posix())
# sys.path.insert(1, (DIRECTORY_PATH / "dp").as_posix())

# TODO: вернуть
# initial_folder = copy.copy(pathlib.Path.cwd().as_posix())
# TODO: убрать

initial_folder = pathlib.Path("/var/dpod")
if not initial_folder.exists():
    initial_folder.mkdir(parents=True, exist_ok=True)

DIRECTORY_PATH = pathlib.Path(__file__).parent.parent
os.chdir(DIRECTORY_PATH.as_posix())
sys.path.insert(1, DIRECTORY_PATH.as_posix())


from dpod.archtool_conf.bundle_project import bundle
from dpod.core.deps import USER_PATH_LOCATION


def create_app() -> tuple[DependencyInjector]:
    injector = bundle(initial_folder)
    return injector


# if __name__ == "__main__":
injector = create_app()
cli = injector.get_dependency(click.Group)
cli()
