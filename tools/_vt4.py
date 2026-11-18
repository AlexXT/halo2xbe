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
    secs.append([name, va, vs, raw, rs])
def blob(name):
    for s in secs:
        if s[0] == name: return d[s[3]:s[3]+s[4]], s[1]
    return b"", 0
ds, dsva = blob("DSOUND")
dslo, dshi = dsva, dsva+len(ds)
rdata, rva = blob(".rdata")
# the runs
runs = []; cur = []
for o in range(0, len(rdata)-3, 4):
    v = struct.unpack_from("<I", rdata, o)[0]
    if dslo <= v < dshi: cur.append(rva+o)
    else:
        if len(cur) >= 8: runs.append(cur)
        cur = []
if len(cur) >= 8: runs.append(cur)
code = [(s[0], blob(s[0])[0], s[1]) for s in secs if s[0] in (".text","D3D","D3DX","DSOUND","XNET","XONLINE","XPP")]
for r in runs:
    print("=== run at 0x%08X (%d entries) ===" % (r[0], len(r)))
    for a in r:
        pat = struct.pack("<I", a)
        for name, b, va in code:
            i = 0
            while True:
                i = b.find(pat, i)
                if i < 0: break
                ctx = b[max(0,i-6):i+8]
                print("   0x%08X <- %s  %s" % (a, name, " ".join("%02X"%c for c in ctx)))
                i += 1
