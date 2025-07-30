import subprocess
from pathlib import Path
from typing import Literal, Iterable


_which_proc: str  # set by __init__.py


def starter(
        mode: Literal["open", "save", "dir", "folder"] = "open",
        multiple: bool = False,
        confirm_overwrite: bool = True,
        initial_dir: str | Path = Path.home(),
        initial_file: str = "",
        file_filter_opts: str | Iterable[str] = None,
        title: str = None,
):
    cmd = [_which_proc, "--file-selection"]

    match mode:
        case "open":
            pass
        case "save":
            cmd.append("--save")
        case "dir":
            cmd.append("--directory")
        case "folder":
            cmd.extend(("--directory", "--save"))
        case _:
            raise ValueError(f"Invalid mode: {mode}")

    if multiple:
        cmd.append("--multiple")

    if confirm_overwrite:
        cmd.append("--confirm-overwrite")

    cmd.extend(("--filename", str(Path(initial_dir, initial_file))))

    if file_filter_opts:
        if isinstance(file_filter_opts, str):
            file_filter_opts = [file_filter_opts]
        for f in file_filter_opts:
            cmd.extend(("--file-filter", f))

    if title is not None:
        cmd.extend(("--title", title))

    r = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    if not r:
        return None
    elif multiple:
        return [Path(_r) for _r in r.split("|")]
    else:
        return Path(r)
