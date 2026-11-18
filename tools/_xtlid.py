import struct
d = open(r"D:\mygame\halo2xbe\assets\halo2debug.xbe","rb").read()
base = struct.unpack_from("<I", d, 0x104)[0]
n = struct.unpack_from("<I", d, 0x11C)[0]
sh = struct.unpack_from("<I", d, 0x120)[0] - base
for i in range(n):
    o = sh + i*56
    fl, va, vs, raw, rs, nm = struct.unpack_from("<6I", d, o)
    name = d[nm-base:nm-base+16].split(b"\x00")[0].decode()
    if name == ".XTLID":
        blob = d[raw:raw+rs]
        print("   the .XTLID section: %d bytes, %d export ids" % (rs, rs//8))
        for k in range(0, min(rs, 64), 8):
            eid, eaddr = struct.unpack_from("<II", blob, k)
            print("      id %08X -> %08X" % (eid, eaddr))
