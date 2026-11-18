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

def blob_of(name):
    for s in secs:
        if s[0] == name: return d[s[3]:s[3]+s[4]], s[1]
    return None, None

# 1. does the map's DSOUND offset conversion hold?
ds, dsva = blob_of("DSOUND")
print("DSOUND section: VA 0x%08X rsize 0x%X" % (dsva, len(ds)))
for nm, off in (("CDirectSoundStream::~", 0x16cd), ("XMediaObject::ctor", 0x16ca),
                ("CDirectSoundStream::AddRef", 0x170b), ("CDirectSoundStream::Release", 0x1752)):
    b = ds[off:off+8]
    print("   map %-28s off 0x%05X -> image 0x%08X: %s" % (nm, off, dsva+off, " ".join("%02X"%c for c in b)))

# 2. the candidate vtable runs in .rdata
rdata, rva = blob_of(".rdata")
dslo, dshi = dsva, dsva + len(ds)
runs = []
cur = []
for o in range(0, len(rdata)-3, 4):
    v = struct.unpack_from("<I", rdata, o)[0]
    if dslo <= v < dshi: cur.append((rva+o, v))
    else:
        if len(cur) >= 8: runs.append(cur)
        cur = []
if len(cur) >= 8: runs.append(cur)

# 3. who references each run's start?
code = b"".join(blob_of(s[0])[0] or b"" for s in secs if s[0] in (".text","D3D","D3DX","DSOUND","XNET","XONLINE","XPP"))
for r in runs:
    start = r[0][0]
    pat = struct.pack("<I", start)
    refs = []
    i = 0
    while True:
        i = code.find(pat, i)
        if i < 0: break
        refs.append(i); i += 1
    print("   vtable 0x%08X: %d entries, %d references from the code" % (start, len(r), len(refs)))
