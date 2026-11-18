"""The 5455 build's render state indices, from the Xbox's own header.

The Xbox's D3DRS_ list (the XDK's public header) gives the index of every state
this build has; the fork's defaults are the 5849 build's, where the programmable
pipeline's states had moved everything after them.
"""
import re

XBOX = r"D:\mygame\xbox trunk\xbox\public\xdk\inc\d3d8types.h"
LAYOUT = r"D:\mygame\XboxXBE-Recomp-fork\xdk\5455\layout.toml"
HOST = r"D:\mygame\XboxXBE-Recomp-fork\runtime\gpu\state.h"

text = open(XBOX, encoding="latin-1").read()
m = re.search(r"typedef enum _D3DRENDERSTATETYPE \{(.*?)\}", text, re.S)
xbox = {}
for line in m.group(1).splitlines():
    mm = re.match(r"\s*(D3DRS_\w+)\s*=\s*(\d+)", line)
    if mm:
        xbox[mm.group(1).upper()[len("D3DRS_"):].replace("_", "")] = int(mm.group(2))

host = []
for line in open(HOST, encoding="latin-1"):
    mm = re.match(r"\s*(kRs\w+)\s*=\s*XDK_Rs\w+,\s*$", line)
    if mm: host.append(mm.group(1))

# the ones the host names itself: the first deferred state, the first complex one
# and the count of the states the device's block holds
special = {"kRsDeferredFirst": xbox.get("FOGENABLE"), "kRsComplexFirst": xbox.get("PSTEXTUREMODES"),
           "kRsMax": max(xbox.values()) + 1}

lines = []
for name in host:
    key = name[3:].upper().replace("_", "")
    if name in special:
        v = special[name]
        note = ""
    elif key in xbox:
        v, note = xbox[key], ""
    else:
        v, note = None, "  # not in this build's list"
    if v is None:
        continue
    lines.append("Rs%s = %d%s" % (name[3:], v, note))

block = ("# the render state indices of this build: the Xbox's own D3DRS_ list (the programmable pipeline's states\n"
         "# came later and moved everything after them, so the host's defaults are another build's)\n")
block += "\n".join(lines) + "\n"

text = open(LAYOUT, encoding="utf-8").read()
text = re.sub(r"\n# the render state indices of this build.*\Z", "\n", text, flags=re.S)
text = text.rstrip() + "\n\n" + block
open(LAYOUT, "w", encoding="utf-8", newline="\n").write(text)
print("%d render states for the 5455 build" % len(lines))
for l in lines[:6]: print("   " + l)
print("   ...")
for l in lines[-4:]: print("   " + l)
