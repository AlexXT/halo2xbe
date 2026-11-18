"""Fill the config's missing XDK bindings from the linker map.

Only the names the scan left at 0 are filled in: what the scan found is its own and
stays. The map names the image's functions; the XDK's headers name the classes, so
the name in the config is the class and the method with an underscore between them.
"""
import re, glob, os

MAP = r"D:\mygame\game\halo2debug.map"
CFG = r"D:\mygame\halo2xbe\config\game.toml"
HAND = r"D:\mygame\halo2xbe\config\game_hand.toml"
RUNTIME = r"D:\mygame\XboxXBE-Recomp-fork\runtime"
SECTIONS = {1: 0x11000, 2: 0x333560, 3: 0x3678E0, 4: 0x36C700,
            5: 0x392980, 6: 0x3A6940, 7: 0x3D0480, 8: 0x3DA0C0}

def candidates(mangled):
    if not mangled.startswith("?"): return []
    parts = mangled[1:].split("@")
    if len(parts) < 2: return []
    method, cls = parts[0], parts[1]
    path = [cls] + parts[2:-1] if len(parts) > 3 else [cls]
    return {"%s_%s" % (path[0], method), "%s_%s" % ("_".join(reversed(path)), method)}

syms = {}
for line in open(MAP, encoding="latin-1"):
    m = re.match(r"\s*([0-9a-f]{4}):([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        base = SECTIONS.get(int(m.group(1), 16))
        if base is None: continue
        syms.setdefault(m.group(3), base + int(m.group(2), 16))
byname = {}
for mangled, addr in syms.items():
    for c in candidates(mangled): byname.setdefault(c, addr)

host = set()
for f in glob.glob(os.path.join(RUNTIME, "**", "*.cpp"), recursive=True):
    for line in open(f, encoding="latin-1"):
        m = re.match(r"\s*HLE_(?:STDCALL|FASTCALL)\((\w+)\s*,", line)
        if m: host.add(m.group(1))

gen = open(CFG, encoding="utf-8", errors="replace").read()
hand = open(HAND, encoding="utf-8", errors="replace").read()
# what the scan found, and what the hand file already says
values = {}
for t in (gen, hand):
    for m in re.finditer(r"^\s*(\w+)\s*=\s*(0x[0-9A-Fa-f]+|0)\s*$", t, re.M):
        values[m.group(1)] = m.group(2)

want = {}
for n in sorted(host):
    if values.get(n, "0") != "0": continue      # the scan found it, or the hand file says
    if n in byname: want[n] = byname[n]

print("filling %d names the scan left at 0:" % len(want))
for n in sorted(want): print("   %-44s = 0x%X" % (n, want[n]))
if not want:
    print("   (none)")
for n in sorted(want):
    entry = "%s = 0x%X" % (n, want[n])
    if re.search(r"^\s*%s\s*=" % re.escape(n), hand, re.M):
        hand = re.sub(r"^\s*%s\s*=.*$" % re.escape(n), entry, hand, flags=re.M)
    else:
        hand = hand.rstrip() + "\n" + entry + "\n"
open(HAND, "w", encoding="utf-8", newline="\n").write(hand)
print("written to", HAND)
