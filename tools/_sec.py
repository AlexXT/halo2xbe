import struct
d = open(r"D:\mygame\halo2xbe\assets\halo2debug.xbe","rb").read()
base = struct.unpack_from("<I", d, 0x104)[0]
n = struct.unpack_from("<I", d, 0x11C)[0]
sh = struct.unpack_from("<I", d, 0x120)[0] - base
for i in range(n):
    o = sh + i*56
    fl, va, vs, raw, rs, nm = struct.unpack_from("<6I", d, o)
    name = d[nm-base:nm-base+16].split(b"\x00")[0].decode()
    if va <= 0x3F800000 < va+vs:
        print("   section %-8s VA 0x%08X vsize 0x%X raw 0x%X rsize 0x%X flags 0x%X" % (name, va, vs, raw, rs, fl))
        off = raw + 0x3F800000 - va
        print("   bytes at 0x3F800000: " + " ".join("%02X" % c for c in d[off:off+16]))
        break
