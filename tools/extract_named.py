"""Pull the named functions out of a lift into one readable file.

The lift writes ~36,000 functions across 130 files as `sub_XXXXXXXX`, and the
pstencil ones as their real names. This collects the named ones -- and the
handful of `sub_` functions that surround them -- into one file, so the
algorithm can be read without grepping 340 MB.

    python extract_named.py generated/tag pstencil pstencil_named.cpp
"""

import glob
import os
import re
import sys

DEF = re.compile(r'^\s*X86_(?:FUNC|WEAK_FUNC)\((?:__imp__)?(\w+)')


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    gendir = argv[0]
    pattern = argv[1] if len(argv) > 1 else 'stencil|shadow'
    out = argv[2] if len(argv) > 2 else 'pstencil_named.cpp'
    rx = re.compile(pattern, re.I)

    chunks = []
    for path in sorted(glob.glob(os.path.join(gendir, 'x86_recomp.*.cpp'))):
        with open(path, 'r', errors='replace') as f:
            lines = f.readlines()
        i = 0
        n = len(lines)
        while i < n:
            m = DEF.match(lines[i])
            if not m:
                i += 1
                continue
            name = m.group(1)
            # the body runs to the matching close brace at column 0
            j = i
            depth = 0
            while j < n:
                depth += lines[j].count('{') - lines[j].count('}')
                if depth <= 0 and j > i:
                    break
                j += 1
            body = lines[i:j + 1]
            if rx.search(name):
                chunks.append((name, os.path.basename(path), i + 1, body))
            i = j + 1

    with open(out, 'w') as f:
        f.write('/*\n')
        f.write(' * The named functions of the lift, gathered from %s.\n' % gendir)
        f.write(' *\n')
        f.write(' * The names come from the linker map (%s) and were placed on the\n'
                % 'halo2tagdebug.map')
        f.write(' * XBE by aligning each object file: an object\'s string constants are\n')
        f.write(' * the same text in both links, and an object\'s code is laid out in\n')
        f.write(' * source order in both, so the map\'s function list and the XBE\'s\n')
        f.write(' * function list line up.\n')
        f.write(' */\n\n')
        for name, fname, line, body in chunks:
            f.write('/* ===== %s   (%s:%d) ===== */\n' % (name, fname, line))
            f.writelines(body)
            f.write('\n\n')

    print('[*] %d functions -> %s' % (len(chunks), out))
    for name, fname, line, _b in chunks:
        print('    %-70s %s:%d' % (name, fname, line))
    return 0


if __name__ == '__main__':
    sys.exit(main())
