import re
F = r"D:\mygame\xbox trunk\xbox\public\xdk\inc\d3d8types.h"
text = open(F, encoding="latin-1").read()
m = re.search(r"typedef enum _D3DRENDERSTATETYPE \{(.*?)\}", text, re.S)
xbox = {}
for line in m.group(1).splitlines():
    mm = re.match(r"\s*(D3DRS_\w+)\s*=\s*(\d+)", line)
    if mm: xbox[int(mm.group(2))] = mm.group(1)
# the host's list
host = {}
for line in open(r"D:\mygame\XboxXBE-Recomp-fork\runtime\gpu\state.h", encoding="latin-1"):
    mm = re.match(r"\s*(kRs\w+)\s*=\s*(\d+),", line)
    if mm: host[int(mm.group(2))] = mm.group(1)
print("   idx  the XDK's (this build)                  the host's (5849)")
for i in range(88, 122):
    x = xbox.get(i, "-")
    h = host.get(i, "-")
    mark = "  <<<" if x.replace("D3DRS_","") != h.replace("kRs","") and h != "-" and x != "-" else ""
    print("   %3d  %-38s %s%s" % (i, x, h, mark))
