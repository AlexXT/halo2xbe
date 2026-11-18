"""Write the 5455 build's state numbering into the fork's state_numbering.h.

The runtime keeps one generation's numbers (5659) and translates where it reads or
writes the title's tables; this build's numbers are the ones the Xbox's D3DRS_ and
D3DTSS_ lists give.
"""
import re

XBOX = r"D:\mygame\xbox trunk\xbox\public\xdk\inc\d3d8types.h"
HOST = r"D:\mygame\XboxXBE-Recomp-fork\runtime\gpu\state.h"
FORK = r"D:\mygame\XboxXBE-Recomp-fork\runtime\xdk\state_numbering.h"

text = open(XBOX, encoding="latin-1").read()

def xbox_enum(pattern):
    m = re.search(pattern, text, re.S)
    out = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"\s*(D3D(?:RS|TSS)_\w+)\s*=\s*(\d+)", line)
        if mm: out[mm.group(1)] = int(mm.group(2))
    return out

rs = xbox_enum(r"typedef enum _D3DRENDERSTATETYPE\s*\{(.*?)\}")
ts = xbox_enum(r"typedef enum _D3DTEXTURESTAGESTATETYPE\s*\{(.*?)\}")

host = open(HOST, encoding="latin-1").read()

def host_enum(prefix):
    out, index = [], 0
    for line in host.splitlines():
        if not re.search(r"\bk%s\w*" % prefix, line): continue
        for m in re.finditer(r"\bk%s(\w*)\s*(?:=\s*(\d+))?\s*(,|$)" % prefix, line):
            if m.group(2): index = int(m.group(2))
            out.append((m.group(1), index))
            index += 1
    return out

def key(s): return s.upper().replace("_", "")

# the Xbox's names by their key; the host's names that differ a little
rs_by_key = {key(k[len("D3DRS_"):]): v for k, v in rs.items()}
ts_by_key = {key(k[len("D3DTSS_"):]): v for k, v in ts.items()}
# the host's name for the texture stage's mip LOD bias is shorter than the Xbox's
if "MIPMAPLODBIAS" in ts_by_key: ts_by_key["MIPLODBIAS"] = ts_by_key.pop("MIPMAPLODBIAS")

rs_lines, ts_lines = [], []
for name, index in host_enum("Rs"):
    if name in ("DeferredFirst", "ComplexFirst", "Max"): continue
    k = key(name)
    if k in rs_by_key: rs_lines.append((name, rs_by_key[k]))
for name, index in host_enum("Tss"):
    if name == "Count": continue
    k = key(name)
    if k in ts_by_key: ts_lines.append((name, ts_by_key[k]))

count = max(rs_by_key.values()) + 1
code = """// 5455 (the XDK the Halo 2 beta links): 82 simple, 35 deferred and 29 complex states, the deferred ones as
// 4039's (the fog states and the lighting) and the complex ones from PsTextureModes on. The texture stage states
// are the Xbox's own list: the address modes and the filters first, the combiner states from ColorOp on.
constexpr Numbering Make5455() {
    Numbering n{82, %d, {}, {}};
    for (auto& r : n.rs) r = kNone;
""" % count
for name, guest in rs_lines:
    code += "    n.rs[gpu::kRs%s] = %d;\n" % (name, guest)
code += "    for (auto& t : n.tss) t = kNone;\n"
for name, guest in ts_lines:
    code += "    n.tss[gpu::kTss%s] = %d;\n" % (name, guest)
code += "    return n;\n}\n\n"

text = open(FORK, encoding="utf-8").read()
text = text.replace("constexpr Numbering kNumbering = XDK_StateNumbering == 3948   ? Make3948()",
                    code + "constexpr Numbering kNumbering = XDK_StateNumbering == 3948   ? Make3948()")
text = text.replace("""                                 : XDK_StateNumbering == 4039 ? Make4039()
                                                               : Make5659();""",
                    """                                 : XDK_StateNumbering == 4039 ? Make4039()
                                 : XDK_StateNumbering == 5455 ? Make5455()
                                                               : Make5659();""")
text = text.replace('static_assert(XDK_StateNumbering == 5659 || XDK_StateNumbering == 3948 || XDK_StateNumbering == 4039,\n'
                    '              "layout.toml StateNumbering: 5659, 4039 or 3948 (a new generation needs its table in xdk/state_numbering.h)");',
                    'static_assert(XDK_StateNumbering == 5659 || XDK_StateNumbering == 3948 || XDK_StateNumbering == 4039 ||\n'
                    '                  XDK_StateNumbering == 5455,\n'
                    '              "layout.toml StateNumbering: 5659, 5455, 4039 or 3948 (a new generation needs its table in xdk/state_numbering.h)");')
open(FORK, "w", encoding="utf-8", newline="\n").write(text)
print("the 5455 table is in the fork (%d render states, %d texture stage states)" % (len(rs_lines), len(ts_lines)))
