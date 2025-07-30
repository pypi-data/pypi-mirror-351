import sys
import shutil
from pathlib import Path
from typing import Iterable, Callable, Literal

STARTERID: Literal["zenity", "kdialog", "tkinter", "windows", "mac"]

if sys.platform == "linux":
    if __which_proc := shutil.which("zenity"):
        from . import linux_zenity
        linux_zenity._which_proc = __which_proc
        _starter = linux_zenity.starter
        STARTERID = "zenity"
    elif __which_proc := shutil.which("kdialog"):
        from . import linux_kdialog
        linux_kdialog._which_proc = __which_proc
        _starter = linux_kdialog.starter
        STARTERID = "kdialog"
    else:
        from .tkinter import starter as _starter
        STARTERID = "tkinter"
elif sys.platform == "win32":
    from .windows import starter as _starter
    STARTERID = "windows"
else:
    from .mac import starter as _starter
    STARTERID = "mac"


def askfile(
        initial_dir: str | Path = Path.home(),
        file_filter_opts: str | Iterable[str] | dict = None,
        title: str = None,
        _starter_: Callable = _starter,
) -> None | Path:
    return _starter_(
        mode="open",
        multiple=False,
        confirm_overwrite=...,
        initial_dir=initial_dir,
        initial_file="",
        file_filter_opts=file_filter_opts,
        title=title
    )


def askfiles(
        initial_dir: str | Path = Path.home(),
        file_filter_opts: str | Iterable[str] | dict = None,
        title: str = None,
        _starter_: Callable = _starter,
) -> None | list[Path]:
    return _starter_(
        mode="open",
        multiple=True,
        confirm_overwrite=...,
        initial_dir=initial_dir,
        initial_file="",
        file_filter_opts=file_filter_opts,
        title=title
    )


def asksave(
        initial_dir: str | Path = Path.home(),
        initial_file: str = "",
        file_filter_opts: str | Iterable[str] | dict = None,
        title: str = None,
        _starter_: Callable = _starter,
) -> None | Path:
    return _starter_(
        mode="save",
        multiple=False,
        confirm_overwrite=...,
        initial_dir=initial_dir,
        initial_file=initial_file,
        file_filter_opts=file_filter_opts,
        title=title
    )


def askdir(
        title: str = None,
        _starter_: Callable = _starter,
) -> None | Path:
    return _starter_(
        mode="dir",
        title=title
    )

