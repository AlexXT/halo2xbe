import re
M = r"D:\mygame\game\halo2debug.map"
syms = []
for line in open(M, encoding="latin-1"):
    m = re.match(r"\s*([0-9a-f]{4}):([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        sec = int(m.group(1), 16)
        off = int(m.group(2), 16)
        syms.append((sec, off, m.group(3)))
# the image's sections and where the map's sections start (from the map's section list)
base = {"0001": 0x11000, "0002": 0x333560, "0003": 0x3678E0, "0004": 0x36C700,
        "0005": 0x392980, "0006": 0x3A6940, "0007": 0x3D0480, "0008": 0x3DA0C0}
def name_of(va):
    best = None
    for sec, off, nm in syms:
        b = base.get("%04X" % sec)
        if b is None: continue
        a = b + off
        if a <= va and (best is None or a > best[0]): best = (a, nm)
    return best[1] if best else "?"
for va in (0x3625C0, 0x33E121, 0x337706, 0x17301D, 0x914D1, 0x159D5, 0x15C3E, 0x3AD8D,
           0x15AEE, 0x15C66, 0x4630C, 0xAB06A, 0x463F9, 0x3055FE):
    print("   0x%08X  %s" % (va, name_of(va)))
