"""The hand kept entries for halo2debug.xbe: the extra entry points, names and XDK
functions the scan could not place.

The scan found most of the XDK's own functions; the ones it left at 0 are here, taken
from the linker map: the XDK's libraries are the D3D, D3DX, DSOUND, XNET, XONLINE and
XPP sections of the image, and the map names the functions in them. The game's own
.text has functions with the same names, so only the library sections are looked at.
"""
import re, glob, os

MAP = r"D:\mygame\game\halo2debug.map"
CFG = r"D:\mygame\halo2xbe\config\game.toml"
HAND = r"D:\mygame\halo2xbe\config\game_hand.toml"
RUNTIME = r"D:\mygame\XboxXBE-Recomp-fork\runtime"
# the map's sections and where they start in the image; the game's own .text is 1
SECTIONS = {2: 0x333560, 3: 0x3678E0, 4: 0x36C700, 5: 0x392980, 6: 0x3A6940, 7: 0x3D0480}

def candidates(mangled):
    if not mangled.startswith("?"): return []
    parts = mangled[1:].split("@")
    if len(parts) < 2: return []
    method, cls = parts[0], parts[1]
    path = [cls] + parts[2:-1] if len(parts) > 3 else [cls]
    return {"%s_%s" % (path[0], method), "%s_%s" % ("_".join(reversed(path)), method)}

byname = {}
for line in open(MAP, encoding="latin-1"):
    m = re.match(r"\s*([0-9a-f]{4}):([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if not m: continue
    base = SECTIONS.get(int(m.group(1), 16))
    if base is None: continue
    for c in candidates(m.group(3)): byname.setdefault(c, base + int(m.group(2), 16))

host = set()
for f in glob.glob(os.path.join(RUNTIME, "**", "*.cpp"), recursive=True):
    for line in open(f, encoding="latin-1"):
        m = re.match(r"\s*HLE_(?:STDCALL|FASTCALL)\((\w+)\s*,", line)
        if m:
            host.add(m.group(1))
            continue
        # the stream and buffer methods are made by a macro, so their names are in its uses
        m = re.match(r"\s*(STREAM|BUFFER)\((\w+)\s*,", line)
        if m:
            host.add(("CDirectSoundStream_" if m.group(1) == "STREAM" else "IDirectSoundBuffer_") + m.group(2))

gen = open(CFG, encoding="utf-8", errors="replace").read()
values = {m.group(1): m.group(2) for m in re.finditer(r"^\s*(\w+)\s*=\s*(0x[0-9A-Fa-f]+|0)\s*$", gen, re.M)}

want = {}
for n in sorted(host):
    if values.get(n, "0") != "0": continue
    if n in byname: want[n] = byname[n]

# the data the scan cannot place: the XPP device type record and the two vtable
# pointers of the DirectSound stream object
want["XPP_GamepadType"] = 0x3D080C
want["DSound_StreamVtable"] = 0x460D44
want["DSound_StreamVtable2"] = 0x460D38

print("%d names the scan left at 0 are placed from the map:" % len(want))
for n in sorted(want): print("   %-44s = 0x%X" % (n, want[n]))

text = """# The hand kept entries for halo2debug.xbe.
#
# config/game.toml is the scan output: xbe_symbols writes it and rewrites it on
# every build, so it is never edited. This file includes it and adds what the scan
# could not find, which is read after the file it includes, so an entry here wins
# over the scan's.
includes = ["game.toml"]

# The XDK's own functions the scan could not place, from the linker map (the XDK's
# libraries are the D3D, D3DX, DSOUND, XNET, XONLINE and XPP sections of the image).
#
# The XAPI XPP device type record: the game passes its address to XInputOpen
# (`push 0x3D080C` before the call), and the runtime keeps the ports' state in it.
#
# The two vtable pointers of the DirectSound stream object: the guest's own
# CDirectSoundStream destructor writes them (`mov dword ptr [esi], 0x460D44` and
# `mov dword ptr [esi+4], 0x460D38`), so the object the host makes looks the way
# the guest's own does.
[symbols]
"""
for n in sorted(want):
    text += "%s = 0x%X\n" % (n, want[n])
text += """
# Extra entry points: an address the guest calls through a pointer, so no scan
# finds it.
#
#   0x310389 = ""
#
# A [[function]] entry splits a function at an address: "end" is where the
# decode of the function at "at" stops (exclusive).
#
#   [[function]]
#   at = 0x31035F
#   end = 0x310389
#
# A [names] entry gives the generated code the game's own name for a function,
# so the code reads as the engine's source rather than as addresses:
#
#   [names]
#   shadow_strip_builder = 0x2F80A
"""
open(HAND, "w", encoding="utf-8", newline="\n").write(text)
print("written to", HAND)
