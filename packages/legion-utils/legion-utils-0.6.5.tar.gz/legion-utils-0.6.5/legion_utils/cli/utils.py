from pathlib import Path
from platform import system

from beartype import beartype
from environs import env as ENV

ENV.read_env()


@beartype
def _data_dir_default() -> Path:
    match system():
        case "Linux":
            return Path.home() / '.local' / 'share'
        case "Darwin":
            return Path.home() / 'Library'


@beartype
def xdg_data_dir(create: bool = False) -> Path:
    data_dir = ENV.path('XDG_DATA_HOME', default=_data_dir_default())
    if create and not data_dir.is_dir():
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@beartype
def legion_data_dir(create: bool = False) -> Path:
    data_dir = xdg_data_dir(create=create)
    if create and not data_dir.is_dir():
        data_dir.mkdir(parents=True, exist_ok=True)
        data_dir.chmod(mode=0o700)
    return data_dir
