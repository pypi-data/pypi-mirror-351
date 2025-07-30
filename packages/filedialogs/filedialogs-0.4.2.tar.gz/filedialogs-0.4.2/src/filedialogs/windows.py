from pathlib import Path
from typing import Literal, Iterable

import win32con
import win32gui
from win32com.shell import shell, shellcon


def starter(
        mode: Literal["open", "save", "dir"] = "open",
        multiple: bool = False,
        confirm_overwrite: bool = True,
        initial_dir: str | Path = Path.home(),
        initial_file: str = "",
        file_filter_opts: str | Iterable[str] | dict = None,
        title: str = None,
):
    if mode == "dir":
        hwnd = win32gui.GetForegroundWindow()
        initial_pidl = shell.SHGetFolderLocation(hwnd, shellcon.CSIDL_DESKTOP, 0, 0)
        pidl, display_name, image_list = shell.SHBrowseForFolder(hwnd, initial_pidl, title, shellcon.ASSOCF_VERIFY, None, None)
        if pidl is not None:
            return Path(shell.SHGetPathFromIDListW(pidl))
        else:
            return None
    else:
        kwargs = dict()

        match mode:
            case "open":
                call = win32gui.GetOpenFileNameW
            case "save":
                call = win32gui.GetSaveFileNameW
                if confirm_overwrite:
                    kwargs["Flags"] = win32con.OFN_OVERWRITEPROMPT
            case _:
                raise ValueError(f"Invalid mode: {mode}")

        if initial_dir:
            kwargs["InitialDir"] = initial_dir

        if initial_file:
            kwargs["File"] = initial_file

        if title:
            kwargs["Title"] = title

        if file_filter_opts:
            if isinstance(file_filter_opts, str):
                kwargs["Filter"] = file_filter_opts + "\0" + file_filter_opts + "\0"
            elif isinstance(file_filter_opts, list):
                kwargs["Filter"] = str().join(f + "\0" + ";".join(f.split(" ")) + "\0" for f in file_filter_opts)
            elif isinstance(file_filter_opts, dict):
                kwargs["Filter"] = str().join(
                    f + "\0" + file_filter_opts[f] + "\0"
                    if isinstance(file_filter_opts[f], str) else
                    f + "\0" + ";".join(file_filter_opts[f]) + "\0"
                    for f in file_filter_opts
                )

        if multiple:
            kwargs["Flags"] = win32con.OFN_ALLOWMULTISELECT | win32con.OFN_EXPLORER | kwargs.get("Flags", 0)

        try:
            hwnd = win32gui.GetForegroundWindow()
            r = call(hwndOwner=hwnd, **kwargs)[0]
        except Exception as e:
            r = None

        if not r:
            return None
        elif multiple:
            r = r.split('\x00')
            dirname = r[0]
            return [Path(dirname, p) for p in r[1:]]
        else:
            return Path(r)
