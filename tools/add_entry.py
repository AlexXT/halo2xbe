"""Add an entry point to a recompiler config's [functions] table.

The TOML this project uses has its section headers indented, so the section
has to be found by the stripped line, not the raw one -- getting that wrong
silently eats the table.

    python add_entry.py config/game.toml 0x310389
"""

import re
import sys


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    path = argv[0]
    addr = argv[1]

    text = open(path, encoding="utf-8", errors="replace").read()
    hexpart = addr[2:] if addr.lower().startswith("0x") else addr
    key = "0x" + hexpart.upper()
    if re.search(r"^\s*0x%s\s*=" % re.escape(hexpart), text, re.M | re.I):
        print("[*] %s is already there" % key)
        return 0

    lines = text.split("\n")
    out = []
    done = False
    for line in lines:
        out.append(line)
        if not done and line.strip() == "[functions]":
            out.append('%s = ""' % key)
            done = True
    if not done:
        print("[!] no [functions] section in %s" % path)
        return 1
    open(path, "w", encoding="utf-8", newline="").write("\n".join(out))
    print("[*] added %s to %s" % (key, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
