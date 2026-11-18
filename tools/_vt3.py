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

# every dword-aligned position in .rdata whose value points into DSOUND
starts = []
for o in range(0, len(rdata)-3, 4):
    v = struct.unpack_from("<I", rdata, o)[0]
    if dslo <= v < dshi: starts.append((rva+o, v))
startset = {a for a,_ in starts}

# references from the code sections
code = [(s[0], blob(s[0])[0], s[1]) for s in secs if s[0] in (".text","D3D","D3DX","DSOUND","XNET","XONLINE","XPP")]
refs = {}
for name, b, va in code:
    for i in range(0, len(b)-3):
        if b[i] in (0xB8,0xB9,0xBA,0xBB,0xBC,0xBD,0xBE,0xBF,0xC7,0x68):
            v = struct.unpack_from("<I", b, i+1)[0]
            if v in startset:
                refs.setdefault(v, []).append((name, va+i, b[i]))
for v in sorted(refs):
    print("0x%08X  <- %s" % (v, ", ".join("%s+0x%X (op %02X)" % (r[0], r[1], r[2]) for r in refs[v])))
