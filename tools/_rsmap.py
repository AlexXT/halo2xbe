"""The render state numbering is per XDK build.

The Xbox's D3DRS_ indices differ between builds (the fog states came later and
moved everything after them), so the host's list of states cannot be fixed: each
build's layout gives the index of every state the host reads.
"""
import re, os

XBOX = r"D:\mygame\xbox trunk\xbox\public\xdk\inc\d3d8types.h"
HOST = r"D:\mygame\XboxXBE-Recomp-fork\runtime\gpu\state.h"

# the Xbox's states
text = open(XBOX, encoding="latin-1").read()
m = re.search(r"typedef enum _D3DRENDERSTATETYPE \{(.*?)\}", text, re.S)
xbox = {}
for line in m.group(1).splitlines():
    mm = re.match(r"\s*(D3DRS_\w+)\s*=\s*(\d+)", line)
    if mm: xbox[mm.group(1).upper()[len("D3DRS_"):]] = int(mm.group(2))

# the host's states
host = {}
for line in open(HOST, encoding="latin-1"):
    mm = re.match(r"\s*(kRs\w+)\s*=\s*(\d+),", line)
    if mm: host[mm.group(1)] = int(mm.group(2))

mapped, missing = {}, []
for name, index in host.items():
    if name in ("kRsDeferredFirst", "kRsComplexFirst", "kRsMax"): continue
    key = name[3:].upper()   # kRsFogEnable -> FOGENABLE
    if key in xbox: mapped[name] = xbox[key]
    else: missing.append((name, index))
print("mapped %d of the host's %d states to the Xbox's numbering" % (len(mapped), len(host)))
if missing:
    print("no counterpart in this build (the host keeps its own):")
    for n, i in missing: print("   %-34s = %d" % (n, i))
print()
print("the mapping:")
for n in host:
    if n in ("kRsDeferredFirst", "kRsComplexFirst", "kRsMax"): continue
    print("   %-34s 5849: %3d   this build: %3d" % (n, host[n], mapped.get(n, host[n])))
