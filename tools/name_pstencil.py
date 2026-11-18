#!/usr/bin/env python3
"""Name the Xbox pstencil functions in a lifted XBE, using the linker MAP.

The problem
----------
The linker maps in `F:\\Games\\Halo 2 Beta\\tools\\bin` describe a *PE* link of
the Halo 2 sources. The XBEs are a different link of the same sources: the
same code, laid out differently. So a map address lands somewhere else in an
XBE, and the best constant offset between the two matches only about a fifth
of the functions.

The fix
-------
Match by content, not by address.

A linker map lists, per object file, the functions AND the string constants
that object contributed, each with an address. A string constant's *text* is
the same in the PE and in the XBE, so:

  1. find each of the object's string constants in the XBE's .rdata, by text;
  2. find the code in the XBE that pushes that string's address;
  3. that is one function of the object. An object's code is contiguous in
     the link, so with several anchors the whole object maps linearly.

The map encodes a string literal's text inside the mangled symbol
(`??_C@_0BM@MBGELAOF@read_file_success@`), with the characters that are not
alphanumeric written as `?X` -- `?5` is a space, `?2` is a slash. The
encoding is not decoded here: the encoded text becomes a *pattern* (`?X`
matches any one character) and the pattern is matched against the XBE's
strings. A literal long enough to be unique picks itself out.

The result is a list of (xbe_address, map_name) pairs, which the
recompiler's config takes as `[names]`.

    python name_pstencil.py --map halo2debug.map --xbe halo2debug.xbe \\
        --funcs generated/game/x86_func_mapping.cpp --objects stencilshadow \\
        -o names.txt
"""

import argparse
import bisect
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import map_ref  # the validated map parser


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
            _f, va, vsize, raw, rsize, name = struct.unpack_from("<6I", d, o)
            nm = d[name - self.base:name - self.base + 16].split(b"\x00")[0].decode()
            self.sections.append((nm, va, vsize, raw, rsize))

    def read_va(self, va, count):
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


def demangle(mangled):
    """A C-safe, readable name for an MSVC mangled symbol.

    `?rasterizer_xbox_stencilshadow_draw_initialize@@YAXXZ` becomes
    `rasterizer_xbox_stencilshadow_draw_initialize_YAXXZ`: the qualified name
    is kept whole, and the encoding is appended so overloads stay apart.
    """
    if not mangled:
        return None
    if not mangled.startswith("?"):
        return re.sub(r"[^A-Za-z0-9_]", "_", mangled)
    body = mangled[1:]
    end = body.find("@@")
    if end < 0:
        return None
    qual = body[:end].replace("@@", "_").replace("@", "_")
    enc = re.sub(r"[^A-Za-z0-9_]", "_", body[end + 2:])
    name = qual + ("_" + enc if enc else "")
    name = re.sub(r"_+", "_", name).strip("_")
    if not name or not re.match(r"^[A-Za-z_]", name):
        return None
    return name


def literal_pattern(symbol):
    """The text inside a MSVC string-literal symbol, as a regex.

    `??_C@_0BM@MBGELAOF@read_file_success@` -> `read_file_success`.
    Characters the linker wrote as `?X` become `.`, one character, so the
    pattern matches the decoded text in the XBE without decoding it here.
    """
    if not symbol.startswith("??_C@"):
        return None
    # the literal is the last '@'-separated field, minus the trailing '@'
    body = symbol[:-1] if symbol.endswith("@") else symbol
    parts = body.split("@")
    if len(parts) < 3:
        return None
    text = parts[-1]
    if len(text) < 4:
        return None
    out = []
    i = 0
    while i < len(text):
        c = text[i]
        if c == "?" and i + 1 < len(text):
            out.append(".")
            i += 2
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out)


def build_string_index(xbe):
    """[(text, va)] for the printable strings in .rdata."""
    rdata = xbe.section(".rdata")
    if not rdata:
        return []
    _nm, va, vsize, raw, rsize = rdata
    blob = xbe.d[raw:raw + rsize]
    out = []
    for m in re.finditer(rb"[ -~]{6,300}\x00", blob):
        out.append((m.group()[:-1].decode("latin1"), va + m.start()))
    return out


def build_push_index(xbe):
    """{immediate: [code addresses]} for the code that names a .rdata address.

    Not only `push imm32` (0x68): the compiler also reaches a string with
    `mov reg, imm32` (0xB8+r), `mov [mem], imm32` (0xC7) and
    `lea reg, [disp32]` (0x8D). The `?static_data` string of the pstencil
    draw object is reached by one of those, so scanning for pushes alone
    misses it.
    """
    out = {}
    text = xbe.section(".text")
    if not text:
        return out
    _nm, va, vsize, raw, rsize = text
    blob = xbe.d[raw:raw + rsize]

    def add(imm, at):
        out.setdefault(imm, []).append(at)

    i = 0
    n = len(blob)
    while i < n - 5:
        b = blob[i]
        if b == 0x68:                       # push imm32
            add(struct.unpack_from("<I", blob, i + 1)[0], va + i)
            i += 5
            continue
        if 0xB8 <= b <= 0xBF:               # mov r32, imm32
            add(struct.unpack_from("<I", blob, i + 1)[0], va + i)
            i += 5
            continue
        if b == 0xC7:                       # mov r/m32, imm32
            add(struct.unpack_from("<I", blob, i + 2)[0], va + i)
            i += 7
            continue
        if b == 0x8D:                       # lea reg, [disp32] (no SIB)
            add(struct.unpack_from("<I", blob, i + 2)[0], va + i)
            i += 6
            continue
        i += 1
    return out


def load_lifted(path):
    addrs = []
    for line in open(path, errors="replace"):
        m = re.match(r"\s*\{\s*(0x[0-9A-Fa-f]+)", line)
        if m:
            addrs.append(int(m.group(1), 16))
    return sorted(set(addrs))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--map", required=True)
    ap.add_argument("--xbe", required=True)
    ap.add_argument("--funcs", help="x86_func_mapping.cpp: the lifted function list")
    ap.add_argument("--objects", default="stencilshadow",
                    help="regex over the map's object file names")
    ap.add_argument("-o", "--out")
    args = ap.parse_args(argv)

    pat = re.compile(args.objects, re.I)
    funcs, data = map_ref.parse(args.map)

    objs = {}
    for e in funcs:
        if pat.search(e["obj"]):
            objs.setdefault(e["obj"], {"fn": [], "str": []})["fn"].append(e)
    for e in data:
        if pat.search(e["obj"]):
            objs.setdefault(e["obj"], {"fn": [], "str": []})["str"].append(e)

    print("[*] objects matching %r:" % args.objects)
    for o, v in sorted(objs.items()):
        print("    %-68s %3d functions, %3d strings"
              % (o, len(v["fn"]), len(v["str"])))

    xbe = Xbe(args.xbe)
    strings = build_string_index(xbe)
    pushes = build_push_index(xbe)
    lifted = load_lifted(args.funcs) if args.funcs else []
    print("[*] XBE: %d strings in .rdata, %d push sites, %d lifted functions"
          % (len(strings), len(pushes), len(lifted)))

    named = {}
    for o, v in sorted(objs.items()):
        v["fn"].sort(key=lambda e: e["start"])
        anchors = []
        matched = 0
        for e in v["str"]:
            rp = literal_pattern(e["name"])
            if not rp:
                continue
            rx = re.compile(rp)
            # The map truncates long literals, so the pattern is matched as a
            # PREFIX: "?5overflowed?5shared?5edge?5bitve" is the symbol for
            # " overflowed shared edge bitvector". The longest match wins.
            best = None
            for text, sva in strings:
                if rx.match(text):
                    if best is None or len(text) > len(best[0]):
                        best = (text, sva)
            if best is None:
                continue
            matched += 1
            for code in pushes.get(best[1], []):
                anchors.append((e["start"], code, best[0]))
        if not anchors:
            print("[!] no anchor for %s (%d/%d strings matched)"
                  % (o.split(":")[-1], matched, len(v["str"])))
            continue

        # each anchor pairs a map address with an XBE code address
        pairs = []
        for pe_addr, code, text in anchors:
            fx = None
            if lifted:
                i = bisect.bisect_right(lifted, code) - 1
                if i >= 0:
                    fx = lifted[i]
            if fx is not None:
                pairs.append((pe_addr, fx, text))
        if not pairs:
            print("[!] %s: %d anchors but none inside a lifted function"
                  % (o.split(":")[-1], len(anchors)))
            continue

        # the object's code is contiguous in both links: the offsets must agree
        deltas = {}
        for pe_a, xbe_a, _t in pairs:
            deltas.setdefault(xbe_a - pe_a, []).append((pe_a, xbe_a, _t))
        best = max(deltas.items(), key=lambda kv: len(kv[1]))
        delta, agree = best
        print("[*] %-44s %d anchors, delta %+d, %d agree"
              % (o.split(":")[-1], len(pairs), delta, len(agree)))

        for e in v["fn"]:
            xva = e["start"] + delta
            if xva in lifted:
                nm = demangle(e["name"])
                if nm:
                    named[xva] = nm

    print()
    print("[*] named %d functions" % len(named))
    if args.out:
        with open(args.out, "w") as f:
            for va in sorted(named):
                f.write("0x%08X %s\n" % (va, named[va]))
        print("[*] wrote %s" % args.out)
    for va in sorted(named)[:25]:
        print("    0x%08X  %s" % (va, named[va]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
