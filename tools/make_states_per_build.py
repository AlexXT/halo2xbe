"""Make the fork's render state indices per XDK build.

The Xbox's D3DRS_ indices differ between builds (the programmable pipeline's states
came later and moved everything after them), so the host's list of states cannot be
fixed: each build's layout gives the index of every state the host reads.
"""
import re

HOST = r"D:\mygame\XboxXBE-Recomp-fork\runtime\gpu\state.h"
LAYOUT_H = r"D:\mygame\XboxXBE-Recomp-fork\runtime\xdk\layout.h"

states = []
for line in open(HOST, encoding="latin-1"):
    m = re.match(r"\s*(kRs\w+)\s*=\s*(\d+),", line)
    if m: states.append((m.group(1), int(m.group(2))))

# the defaults in layout.h: the XDK 5849 build the host's list was taken from
block = ["// the render state indices are per XDK build: the programmable pipeline's states came later and moved",
         "// everything after them, so each build's layout gives the index of every state the host reads"]
for name, index in states:
    block.append("#ifndef XDK_%s\n#define XDK_%s %du\n#endif" % (name, name, index))
block.append("")
text = open(LAYOUT_H, encoding="utf-8").read()
marker = "#ifndef XDK_CDevice_RenderTarget"
if "XDK_RsLighting" not in text:
    text = text.replace(marker, "\n".join(block) + "\n" + marker, 1)
    open(LAYOUT_H, "w", encoding="utf-8", newline="\n").write(text)
    print("the defaults are in layout.h")

# state.h: the enum takes the index from the layout
text = open(HOST, encoding="utf-8").read()
out = []
for line in text.splitlines(True):
    m = re.match(r"\s*(kRs\w+)\s*=\s*(\d+),\s*$", line)
    if m:
        out.append("    %s = XDK_%s,\n" % (m.group(1), m.group(1)))
    else:
        out.append(line)
text = "".join(out)
if '#include "xdk/layout.h"' not in text:
    text = text.replace('#include "gpu/state.h"', '#include "gpu/state.h"', 1)
    # the include goes after the other includes
    lines = text.splitlines(True)
    for i, l in enumerate(lines):
        if l.startswith("#include"):
            last = i
    lines.insert(last + 1, '#include "xdk/layout.h"\n')
    text = "".join(lines)
open(HOST, "w", encoding="utf-8", newline="\n").write(text)
print("state.h takes its indices from the layout")
