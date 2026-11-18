import re
F = r"D:\mygame\xbox trunk\xbox\public\xdk\inc\d3d8types.h"
text = open(F, encoding="latin-1").read()
m = re.search(r"typedef enum _D3DRENDERSTATETYPE \{(.*?)\} D3DRENDERSTATETYPE", text, re.S)
if not m:
    m = re.search(r"_D3DRENDERSTATETYPE\s*\{(.*?)\}", text, re.S)
body = m.group(1)
states = []
for line in body.splitlines():
    mm = re.match(r"\s*(D3DRS_\w+)\s*=\s*(\d+)", line)
    if mm: states.append((int(mm.group(2)), mm.group(1)))
for n, name in states:
    if 95 <= n <= 115: print("   %3d  %s" % (n, name))
print("   ... %d states in all" % len(states))
