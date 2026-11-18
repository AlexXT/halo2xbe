#!/usr/bin/env python3
"""Turn an MSVC linker MAP into a function catalog we can score against.

`tools/pe/map_names.py resolve` gives {va: name}. That is enough to *name*
things but not enough to *score* a recovered catalog against, and it throws
away the MAP's own `Lib:Object` column -- which is the single most useful
piece of the file for this project, because it says which object file each
function was linked from. `blamlibWin32Tag_Debug:rasterizer_dx8_stencilshadow
_environment.obj` is how we know exactly which bytes are the pstencil code.

So this parses the MAP directly and keeps three things per symbol:
the address, the mangled name, and the object file it came from.

    python map_ref.py MAP -o reference.json --objects objects.json

The reference is written in the shape `score_recovery.py` loads:

    {"functions": [{"start": 0x401000, "name": "...", "obj": "...", ...}]}

Only symbols the MAP flags as functions (`f`) go in as function starts; data
symbols are emitted separately under "data" so they are not mistaken for
recovery misses.
"""

import argparse
import json
import re
import sys

# " 0001:00000000       ?name@@YAXXZ     00401000 f   cseries_errors.obj"
#  0002:0000abac       ??_C@_07HJMDJJPB@... 0073ebac     lib:obj
#  0000:00000000       __except_list     00000000     <absolute>
SYM = re.compile(
    r"^\s*(?P<sect>[0-9a-f]{4}):(?P<off>[0-9a-f]{8})\s+"
    r"(?P<name>\S+)\s+"
    r"(?P<rva>[0-9a-f]{8})"
    r"(?P<rest>.*)$",
    re.IGNORECASE,
)


def parse(path):
    """-> (functions, data) where each entry is a dict."""
    functions = []
    data = []
    with open(path, "r", errors="replace") as f:
        for line in f:
            m = SYM.match(line)
            if not m:
                continue
            rest = m.group("rest")
            # The flags column is a variable run of single letters -- `f` for a
            # function, `f i` for an inlined one -- and then Lib:Object.
            tokens = rest.split()
            flags = []
            while tokens and tokens[0] in ("f", "i"):
                flags.append(tokens.pop(0))
            lib_obj = " ".join(tokens) if tokens else ""
            if "<absolute>" in lib_obj:
                continue
            va = int(m.group("rva"), 16)
            if va == 0:
                continue
            entry = {
                "start": va,
                "name": m.group("name"),
                "obj": lib_obj,
            }
            if flags:
                entry["flags"] = " ".join(flags)
            if "f" in flags:
                functions.append(entry)
            else:
                data.append(entry)
    functions.sort(key=lambda e: e["start"])
    data.sort(key=lambda e: e["start"])
    return functions, data


def object_summary(functions):
    """{object file: [entries]} for everything that is not plain CRT/library."""
    by_obj = {}
    for e in functions:
        obj = e["obj"]
        if not obj:
            obj = "<no object>"
        by_obj.setdefault(obj, []).append(e)
    return by_obj


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map")
    ap.add_argument("-o", "--out", help="write the reference catalog here")
    ap.add_argument("--objects", help="write the per-object breakdown here")
    ap.add_argument("--grep", help="only list objects whose name matches this regex")
    ap.add_argument("--seeds",
                    help="write a disasm32 --seed-functions list here: every "
                         "address the MAP says is a function")
    args = ap.parse_args(argv)

    functions, data = parse(args.map)
    if not functions:
        print("no function symbols found -- is this an MSVC MAP?", file=sys.stderr)
        return 1

    if args.out:
        with open(args.out, "w") as f:
            json.dump({"functions": functions}, f, indent=1)
        print(f"[*] {len(functions):,} function symbols -> {args.out}")

    by_obj = object_summary(functions)
    if args.objects:
        with open(args.objects, "w") as f:
            json.dump(by_obj, f, indent=1)
        print(f"[*] {len(by_obj):,} distinct objects -> {args.objects}")

    # The MAP is ground truth, so it is also the best possible seed list:
    # every address it calls a function is a function whether or not a
    # recursive-descent scan can find it. Seeding with it is how the recall
    # gap gets closed -- Havok's heavily-templated code and the linker's
    # import jump-thunks are exactly what a call-graph scan misses and
    # exactly what a symbol table knows.
    if args.seeds:
        seeds = sorted({e["start"] for e in functions})
        with open(args.seeds, "w") as f:
            json.dump(seeds, f)
        print(f"[*] {len(seeds):,} distinct function addresses -> {args.seeds}")

    # A quick look at what the binary is made of, by object file.
    print(f"[*] {len(functions):,} functions, {len(data):,} data symbols, "
          f"{len(by_obj):,} objects")

    if args.grep:
        import re as _re
        pat = _re.compile(args.grep, _re.IGNORECASE)
        for obj in sorted(by_obj):
            if pat.search(obj):
                print(f"  {obj}: {len(by_obj[obj])} functions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
