"""Find the code the lift is missing, from the guest's own pointer tables.

The recompiler discovers functions by following calls, code pointers and the
gaps between known ones. A function reached only through a pointer *table*
that it does not recognise -- a vtable, a callback struct -- is found or not
found by luck, and a missed one traps at run time with:

    error: indirect call to 00310389 has no recompiled function
    error: add 0x310389 to [functions] in the image's config/*.toml and rebuild

The runtime stops at the first, and each rebuild is minutes, so it is worth
finding them all at once. Every pointer into the code section that is not in
the dispatch table is a candidate: the guest holds it somewhere, and the
guest calling it means the guest needs it.

    python find_missing_entries.py assets/halo2debug.xbe generated/game \\
        -o missing_entries.txt
"""

import argparse
import os
import re
import struct
import sys


def load_dispatch(gen_dir):
    """{va: name} from the lift's function mapping."""
    path = os.path.join(gen_dir, 'x86_func_mapping.cpp')
    out = {}
    with open(path, errors='replace') as f:
        for line in f:
            m = re.match(r'\s*\{0x([0-9A-Fa-f]+)u, (\w+)\},', line)
            if m:
                out[int(m.group(1), 16)] = m.group(2)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("xbe")
    ap.add_argument("gendir")
    ap.add_argument("-o", "--out")
    args = ap.parse_args(argv)

    d = open(args.xbe, 'rb').read()
    base = struct.unpack_from('<I', d, 0x104)[0]
    n = struct.unpack_from('<I', d, 0x11C)[0]
    sh = struct.unpack_from('<I', d, 0x120)[0] - base
    secs = []
    for i in range(n):
        o = sh + i * 56
        _f, va, vsize, raw, rsize, nm = struct.unpack_from('<6I', d, o)
        secs.append((d[nm - base:nm - base + 16].split(b'\x00')[0].decode(),
                     va, vsize, raw, rsize))

    dispatch = load_dispatch(args.gendir)
    print('[*] dispatch: %d functions' % len(dispatch))

    # the code sections: where a function can be
    code = []
    for nm2, va, vsize, raw, rsize in secs:
        if nm2 in ('.text', 'D3D', 'D3DX', 'DSOUND', 'XNET', 'XONLINE', 'XPP'):
            code.append((nm2, va, vsize))
    lo = min(c[1] for c in code)
    hi = max(c[1] + c[2] for c in code)
    print('[*] code range: 0x%08X - 0x%08X' % (lo, hi))

    def in_code(va):
        for _nm, v, vs in code:
            if v <= va < v + vs:
                return True
        return False

    # every dword in the image that points into the code
    hits = {}
    for nm2, va, vsize, raw, rsize in secs:
        if nm2 in ('.text', 'D3D', 'D3DX', 'DSOUND', 'XNET', 'XONLINE', 'XPP'):
            continue
        blob = d[raw:raw + rsize]
        for i in range(0, len(blob) - 3, 4):
            v = struct.unpack_from('<I', blob, i)[0]
            if in_code(v) and v not in dispatch:
                hits.setdefault(v, []).append((nm2, va + i))

    # classify: a pointer that falls between two known functions is an
    # ALTERNATE entry into one of them (the case the runtime traps on); a
    # pointer that falls in a hole is a function the discovery never reached.
    addrs = sorted(dispatch)
    import bisect

    def looks_like_start(va):
        b = xbe_bytes(va, 16)
        if not b:
            return False
        if b[:3] == b'\x55\x8b\xec':      # push ebp; mov ebp, esp
            return True
        if b[:2] == b'\x83\xec' or b[:2] == b'\x81\xec':
            return True
        if b[0] in (0x55, 0x56, 0x57, 0x53, 0x51, 0x52, 0x50, 0x8B, 0x6A):
            return True
        return False

    def xbe_bytes(va, k):
        for nm2, v, vs, r, rs in secs:
            if v <= va < v + vs:
                off = r + (va - v)
                return d[off:off + k]
        return None

    alt, new = [], []
    for v in sorted(hits):
        i = bisect.bisect_right(addrs, v)
        inside = i > 0 and addrs[i - 1] < v < (addrs[i] if i < len(addrs) else 1 << 32)
        (alt if inside else new).append(v)

    print('[*] %d pointers with no recompiled function:' % len(hits))
    print('    %d fall between two known functions (alternate entries)' % len(alt))
    print('    %d fall in a hole (functions the discovery never reached)' % len(new))
    for v in sorted(hits):
        where = hits[v][:2]
        kind = 'ALT' if v in alt else 'NEW'
        print('    %s 0x%08X  <- %s' % (kind, v, ', '.join('%s+0x%X' % (w, off) for w, off in where)))

    if args.out:
        with open(args.out, 'w') as f:
            for v in sorted(hits):
                f.write('0x%08X\n' % v)
        print('[*] wrote %s' % args.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
