#!/usr/bin/env python3
"""Read an XBE's export table into (name, address) pairs.

The Halo 2 debug builds export every one of their functions -- that is what
makes them "debug" builds -- and `halo2debug.xbe` carries 65,643 names. They
are the only ground truth for names that matches the XBE's own layout: the
linker maps in tools/bin describe a *PE* link of the same sources, and the
XBE lays its sections out differently, so an address from a map lands
somewhere else entirely.

The XBE's export directory lives at the start of the .XTLID section and is a
PE export directory, except that every RVA in it is relative to the XBE's
image base (0x10000) rather than to the section.

    python xbe_exports.py halo2debug.xbe -o exports.txt

One line per export: the name, then the address, hex.
"""

import argparse
import struct
import sys


class Xbe:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.d = f.read()
        d = self.d
        self.base = struct.unpack_from("<I", d, 0x104)[0]
        n = struct.unpack_from("<I", d, 0x11C)[0]
        sh = struct.unpack_from("<I", d, 0x120)[0] - self.base
        self.sections = []
        for i in range(n):
            o = sh + i * 56
            _flags, va, vsize, raw, rsize, name = struct.unpack_from("<6I", d, o)
            nm = d[name - self.base:name - self.base + 16].split(b"\x00")[0].decode()
            self.sections.append((nm, va, vsize, raw, rsize))

    def read_va(self, va, count):
        """Bytes at a virtual address, or None."""
        for _nm, sva, vsize, raw, rsize in self.sections:
            if sva <= va < sva + vsize:
                off = raw + (va - sva)
                if off + count > len(self.d):
                    return None
                return self.d[off:off + count]
        return None

    def section(self, name):
        for s in self.sections:
            if s[0] == name:
                return s
        return None

    def va_to_rva(self, va):
        return va - self.base


def exports(xbe):
    """[(name, va)] from the .XTLID export directory."""
    xt = xbe.section(".XTLID")
    if not xt:
        return []
    _nm, sva, vsize, raw, rsize = xt
    ed = xbe.d[raw:raw + 40]
    if len(ed) < 40:
        return []
    nfun = struct.unpack_from("<I", ed, 0x14)[0]
    nname = struct.unpack_from("<I", ed, 0x18)[0]
    names_rva = struct.unpack_from("<I", ed, 0x20)[0]
    ords_rva = struct.unpack_from("<I", ed, 0x24)[0]
    funcs_rva = struct.unpack_from("<I", ed, 0x1C)[0]

    names_tab = xbe.read_va(xbe.base + names_rva, 4 * nname)
    ords_tab = xbe.read_va(xbe.base + ords_rva, 2 * nname)
    funcs_tab = xbe.read_va(xbe.base + funcs_rva, 4 * nfun)
    if not names_tab or not ords_tab or not funcs_tab:
        return []

    out = []
    for i in range(nname):
        name_rva = struct.unpack_from("<I", names_tab, 4 * i)[0]
        ordinal = struct.unpack_from("<H", ords_tab, 2 * i)[0]
        if ordinal >= nfun:
            continue
        func_rva = struct.unpack_from("<I", funcs_tab, 4 * ordinal)[0]
        if func_rva == 0:
            continue
        b = xbe.read_va(xbe.base + name_rva, 256)
        if not b:
            continue
        name = b.split(b"\x00")[0].decode("latin1")
        if not name:
            continue
        out.append((name, xbe.base + func_rva))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xbe")
    ap.add_argument("-o", "--out")
    ap.add_argument("--grep", help="print only the names matching this regex")
    args = ap.parse_args(argv)

    xbe = Xbe(args.xbe)
    ex = exports(xbe)
    print("[*] %s: %d exports" % (args.xbe, len(ex)))

    if args.grep:
        import re
        pat = re.compile(args.grep, re.I)
        for name, va in ex:
            if pat.search(name):
                print("  0x%08X  %s" % (va, name))
        return 0

    if args.out:
        with open(args.out, "w") as f:
            for name, va in sorted(ex, key=lambda e: e[1]):
                f.write("0x%08X %s\n" % (va, name))
        print("[*] wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
