import subprocess
from pathlib import Path
from typing import Literal, Iterable


_which_proc: str  # set by __init__.py


def starter(
        mode: Literal["open", "save", "dir"] = "open",
        multiple: bool = False,
        confirm_overwrite=...,
        initial_dir: str | Path = Path.home(),
        initial_file=...,
        file_filter_opts: str | Iterable[str] = None,
        title: str = None,
):
    cmd = [_which_proc]

    match mode:
        case "open":
            cmd.append("--getopenfilename")
        case "save":
            cmd.append("--getsavefilename")
        case "dir":
            cmd.append("--getexistingdirectory")
        case _:
            raise ValueError(f"Invalid mode: {mode}")

    cmd.append(str(initial_dir))

    if multiple:
        cmd.append("--multiple")

    if file_filter_opts:
        if isinstance(file_filter_opts, str):
            file_filter_opts = [file_filter_opts]
        cmd.append("\"" + "|".join(file_filter_opts) + "\"")

    if title is not None:
        cmd.extend(("--title", title))

    r = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    if not r:
        return None
    elif multiple:
        return [Path(_r) for _r in r.split(" ")]
    else:
        return Path(r)
