from typing import Literal, Iterable
from pathlib import Path
try:
    try:
        import tkinter.filedialog as tkf
        from tkinter import Tk
    except ImportError:
        import Tkinter.filedialog as tkf
        from Tkinter import Tk
except ImportError as e:
    from traceback import print_exception
    print_exception(e)
    print("^" * 100 + """
Something went wrong when importing Tkinter.

Make sure that Tkinter is installed for the Python interpreter you are using.

Quick help:

  - Ubuntu
      sudo apt-get install python3-tk 
  - Fedora
      sudo dnf install python3-tkinter
  - MacOS
      brew install python-tk

  python.. -m pip install tk
""")
    exit(1)


def starter(
        mode: Literal["open", "save", "dir", "folder"] = "open",
        multiple: bool = False,
        confirm_overwrite: bool = True,
        initial_dir: str | Path = Path.home(),
        initial_file: str = "",
        file_filter_opts: str | Iterable[str] = None,
        title: str = None,
):
    root = Tk()
    root.withdraw()

    if file_filter_opts:
        if isinstance(file_filter_opts, str):
            file_filter_opts = [file_filter_opts]
        file_filter_opts = [(f, f.replace("*", "")) for f in file_filter_opts]
    else:
        file_filter_opts = []

    match mode:
        case "open":
            if multiple:
                r = tkf.askopenfilenames(initialdir=initial_dir, initialfile=initial_file, title=title, filetypes=file_filter_opts)
            else:
                r = tkf.askopenfilename(initialdir=initial_dir, initialfile=initial_file, title=title, filetypes=file_filter_opts)
        case "save":
            r = tkf.asksaveasfilename(initialdir=initial_dir, initialfile=initial_file, title=title, filetypes=file_filter_opts, confirmoverwrite=confirm_overwrite)
        case "dir":
            r = tkf.askdirectory(initialdir=initial_dir, mustexist=True, title=title)
        case "folder":
            r = tkf.askdirectory(initialdir=initial_dir, mustexist=False, title=title)
        case _:
            raise ValueError(f"Invalid mode: {mode}")

    if not r:
        return None
    elif multiple:
        return [Path(_r) for _r in r]
    else:
        return Path(r)
