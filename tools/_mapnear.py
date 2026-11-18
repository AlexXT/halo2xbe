import re
M = r"D:\mygame\game\halo2debug.map"
best = {}
for line in open(M, encoding="latin-1"):
    m = re.match(r"\s*0002:([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        off = int(m.group(1), 16)
        for target in (0xC0E0, 0x11F00):
            if off <= target and (target not in best or off > best[target][0]):
                best[target] = (off, m.group(2))
DS = 0x333560
for t in (0xC0E0, 0x11F00):
    off, nm = best[t]
    print("0x%08X is in %s (map 0002:%08X)" % (DS + t, nm, off))
