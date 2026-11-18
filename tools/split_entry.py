"""Split an alternate entry out of the function that covers it.

0x310389 is an alternate entry into the function at 0x31035F: the guest
installs it as a callback at run time (`mov dword ptr [0xC60590], 0x310389`)
and calls it through a pointer, so no scan of the image finds it. The
disassembler's walk from 0x31035F runs straight over it, so the bytes are
already claimed and the entry can never be decoded.

Giving each its own end puts a boundary between them.

    python split_entry.py config/game.toml 0x31035F 0x310389 0x3103B3
"""

import re
import sys


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    path = argv[0]
    a = int(argv[1], 16)
    b = int(argv[2], 16)
    c = int(argv[3], 16) if len(argv) > 3 else 0

    text = open(path, encoding="utf-8", errors="replace").read()
    # drop a previous plain entry for the same address
    text = re.sub(r"^\s*0x%X\s*=.*\n" % b, "", text, flags=re.M)
    text = re.sub(r"^\s*0x%X\s*=.*\n" % a, "", text, flags=re.M)

    frag = ("\n# 0x%X is an alternate entry into the function at 0x%X: the guest installs\n"
            "# it as a callback at run time and calls it through a pointer, so no scan\n"
            "# of the image finds it, and the walk from 0x%X runs straight over it.\n"
            "# Giving each its own end puts a boundary between them.\n"
            "[[function]]\nat = 0x%X\nend = 0x%X\n" % (b, a, a, a, b))
    if c:
        frag += "\n[[function]]\nat = 0x%X\nend = 0x%X\n" % (b, c)
    text = text.rstrip() + "\n" + frag
    open(path, "w", encoding="utf-8", newline="").write(text)
    print("[*] %s: split 0x%X / 0x%X" % (path, a, b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
