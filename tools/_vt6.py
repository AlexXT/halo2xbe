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
def read(va, count):
    for s in secs:
        if s[1] <= va < s[1]+s[4]:
            off = s[3] + va - s[1]
            return d[off:off+count]
    return b""
print("=== the XPP record at 0x3D080C (device type, current, changed, previous) ===")
for i in range(0, 32, 4):
    v = struct.unpack_from("<I", read(0x3D080C+i, 4), 0)[0]
    print("   +0x%02X: 0x%08X" % (i, v))
print()
print("=== the CDirectSoundStream vtable at 0x460D44 (the first entries) ===")
for i in range(0, 28, 4):
    v = struct.unpack_from("<I", read(0x460D44+i, 4), 0)[0]
    print("   +0x%02X: 0x%08X" % (i, v))
print()
print("=== the secondary vtable at 0x460D38 ===")
for i in range(0, 12, 4):
    v = struct.unpack_from("<I", read(0x460D38+i, 4), 0)[0]
    print("   +0x%02X: 0x%08X" % (i, v))
