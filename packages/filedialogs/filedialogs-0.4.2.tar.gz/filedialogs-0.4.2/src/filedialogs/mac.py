import subprocess
from pathlib import Path
from typing import Literal, Iterable


def starter(
        mode: Literal["open", "save", "dir", "folder"] = "open",
        multiple: bool = False,
        confirm_overwrite=...,
        initial_dir: str | Path = Path.home(),
        initial_file: str = "",
        file_filter_opts: str | Iterable[str] = None,
        title: str = None,
):
    match mode:
        case "open":
            cmd = "choose file"
        case "save":
            cmd = "choose file name"
            if initial_file:
                cmd += f' default name "{initial_file}"'
        case "dir":
            cmd = "choose folder"
        case "folder":
            cmd = "choose folder name"
            if initial_file:
                cmd += f' default name "{initial_file}"'
        case _:
            raise ValueError(f"Invalid mode: {mode}")

    if initial_dir:
        cmd += f' default location "{initial_dir}"'

    if title is not None:
        cmd += f' with prompt "{title}"'

    if file_filter_opts:
        if isinstance(file_filter_opts, str):
            file_filter_opts = [file_filter_opts]
        file_filter_opts = [f.lstrip("*.") for f in file_filter_opts]
        file_filter_opts = str(',').join("\"" + f + "\"" for f in file_filter_opts)
        cmd += f' of type {{{file_filter_opts}}}'

    if multiple:
        cmd += " with multiple selections allowed"

    r = subprocess.run(["osascript", "-"], input=cmd, text=True, capture_output=True).stdout.strip()
    r = [_r[_r.find(":"):].replace(":", "/") for _r in r.split(",")]

    if not r:
        return None
    elif multiple:
        return [Path(x) for x in r]
    else:
        return Path(r[0])
