import re
M = r"D:\mygame\game\halo2debug.map"
best = None
for line in open(M, encoding="latin-1"):
    m = re.match(r"\s*0004:([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        off = int(m.group(1), 16)
        if off <= 0xC00 and (best is None or off > best[0]): best = (off, m.group(2))
print("the function at 0x334160ish:", best)
