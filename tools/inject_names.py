"""Put the recovered pstencil names into a recompiler config as [names].

The names come from name_by_order.py, which aligns the linker MAP's object
files against the XBE by content: an object's string constants are the same
text in both, and an object's code is laid out in source order in both, so
the map's function list and the XBE's function list line up.

    python inject_names.py --names work_pstencil_names.txt config/tag.toml config/game.toml
"""

import argparse
import re
import sys

IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--names", required=True)
    ap.add_argument("configs", nargs="+")
    args = ap.parse_args(argv)

    pairs = []
    for line in open(args.names):
        line = line.strip()
        if not line:
            continue
        va, nm = line.split(None, 1)
        nm = nm.strip()
        if not IDENT.match(nm):
            print("[!] not an identifier, skipped: %r" % nm)
            continue
        pairs.append((int(va, 16), nm))

    # one name per address, and one address per name: a duplicate would be a
    # duplicate definition in the generated C++
    by_va = {}
    by_nm = {}
    for va, nm in pairs:
        if va in by_va or nm in by_nm:
            continue
        by_va[va] = nm
        by_nm[nm] = va
    print("[*] %d names" % len(by_va))

    for path in args.configs:
        text = open(path, encoding="utf-8", errors="replace").read()
        # drop a previous [names] section (its header may be indented)
        text = re.sub(r"\n\s*\[names\][^\[]*", "\n", text)
        body = "\n".join('"%s" = 0x%X' % (nm, va) for va, nm in sorted(by_va.items()))
        text = text.rstrip() + "\n\n# the game's own functions, by name: the generated code calls\n# them by name rather than by address\n[names]\n" + body + "\n"
        open(path, "w", encoding="utf-8", newline="").write(text)
        print("[*] wrote %d names into %s" % (len(by_va), path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
