import re
M = r"D:\mygame\game\halo2debug.map"
syms = []
for line in open(M, encoding="latin-1"):
    m = re.match(r"\s*([0-9a-f]{4}):([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        syms.append((int(m.group(1), 16), int(m.group(2), 16), m.group(3)))
base = {1: 0x11000, 2: 0x333560, 3: 0x3678E0, 4: 0x36C700, 5: 0x392980, 6: 0x3A6940, 7: 0x3D0480, 8: 0x3DA0C0}
def name_of(va):
    best = None
    for sec, off, nm in syms:
        b = base.get(sec)
        if b is None: continue
        a = b + off
        if a <= va and (best is None or a > best[0]): best = (a, nm)
    return best[1] if best else "?"
for va in (0x336A78, 0x33E842, 0x336535, 0x989680, 0x98D1B, 0x363A78):
    print("   0x%08X  %s" % (va, name_of(va)))
