import struct
d = open(r"D:\mygame\halo2xbe\assets\halo2debug.xbe","rb").read()
base = struct.unpack_from("<I", d, 0x104)[0]
n = struct.unpack_from("<I", d, 0x11C)[0]
sh = struct.unpack_from("<I", d, 0x120)[0] - base
secs = []
for i in range(n):
    o = sh + i*56
    fl, va, vs, raw, rs, nm = struct.unpack_from("<6I", d, o)
    name = d[nm-base:nm-base+16].split(b"\x00")[0].decode()
    secs.append((name, va, vs, raw, rs))
for s in secs: print("   section %-10s VA 0x%08X vsize 0x%06X rsize 0x%06X" % (s[0], s[1], s[2], s[4]))
# the DSOUND section's range
ds = [s for s in secs if s[0] == "DSOUND"][0]
lo, hi = ds[1], ds[1] + ds[4]
# find runs of dwords pointing into DSOUND, in every section
for name, va, vs, raw, rs in secs:
    blob = d[raw:raw+rs]
    runs = []
    cur = []
    for o in range(0, len(blob) - 3, 4):
        v = struct.unpack_from("<I", blob, o)[0]
        if lo <= v < hi:
            cur.append((va + o, v))
        else:
            if len(cur) >= 8: runs.append(cur)
            cur = []
    if len(cur) >= 8: runs.append(cur)
    for r in runs:
        print("   %-8s 0x%08X: %d entries into DSOUND, first 0x%08X" % (name, r[0][0], len(r), r[0][1]))
