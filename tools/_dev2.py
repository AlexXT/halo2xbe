import struct
d = open(r"D:\mygame\halo2xbe\assets\halo2debug.xbe","rb").read()
base = struct.unpack_from("<I", d, 0x104)[0]
n = struct.unpack_from("<I", d, 0x11C)[0]
sh = struct.unpack_from("<I", d, 0x120)[0] - base
secs = []
for i in range(n):
    o = sh + i*56
    fl, sva, vs, raw, rs, nm = struct.unpack_from("<6I", d, o)
    secs.append((d[nm-base:nm-base+16].split(b"\x00")[0].decode(), sva, vs, raw, rs))
def read(va, count):
    for name, sva, vs, raw, rs in secs:
        if sva <= va < sva + rs:
            return d[raw + va - sva: raw + va - sva + count], name
        if sva <= va < sva + vs:
            return b"\x00" * count, name + " (zero filled)"
    return None, None
b, sec = read(0x3F800000, 16)
print("0x3F800000 in", sec, ":", " ".join("%02X" % c for c in b))
print("   as dwords:", [hex(struct.unpack_from("<I", b, i)[0]) for i in range(0, 16, 4)])
b, sec = read(0x363BB4, 8)
print("CDevice+0x15F4 (0x363BB4) in", sec, ":", " ".join("%02X" % c for c in b))
