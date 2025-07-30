from sys import argv


def run():
    from filedialogs import askfile, askfiles, asksave, askdir
    
    action = argv[1] if len(argv) > 1 else None
    
    match action:
        case "open":
            print(str(askfile() or ""))
        case "multi":
            print(str("\n").join(str(r) for r in askfiles() or ()))
        case "save":
            print(str(asksave() or ""))
        case "dir":
            print(str(askdir() or ""))
        case _:
            print("Usage: askfile open|multi|save|dir")
            return 1
    return 0


if __name__ == "__main__":
    exit(run())
