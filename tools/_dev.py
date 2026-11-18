import struct
d = open(r"D:\mygame\halo2xbe\assets\halo2debug.xbe","rb").read()
base = struct.unpack_from("<I", d, 0x104)[0]
n = struct.unpack_from("<I", d, 0x11C)[0]
sh = struct.unpack_from("<I", d, 0x120)[0] - base
def read(va, count):
    for i in range(n):
        o = sh + i*56
        fl, sva, vs, raw, rs, nm = struct.unpack_from("<6I", d, o)
        if sva <= va < sva+rs:
            off = raw + va - sva
            return d[off:off+count], (d[nm-base:nm-base+16].split(b"\x00")[0].decode(), sva, vs, rs)
    return None, None
print("=== the CDevice at 0x3625C0: the fields around +0x15F4 ===")
for off in (0x154C, 0x15E4, 0x15E8, 0x15F0, 0x15F4, 0x15F8, 0x15FC):
    b, sec = read(0x3625C0 + off, 4)
    v = struct.unpack_from("<I", b, 0)[0]
    print("   CDevice+0x%04X (0x%08X) = 0x%08X" % (off, 0x3625C0+off, v))
print()
print("=== what is at 0x3F800000 in the image? ===")
b, sec = read(0x3F800000, 16)
print("   section", sec[0], "->", " ".join("%02X" % c for c in b))
print("   as dwords:", [hex(struct.unpack_from("<I", b, i)[0]) for i in range(0, 16, 4)])
