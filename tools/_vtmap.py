import struct, re
# the map's DSOUND symbols -> image addresses
M = r"D:\mygame\game\halo2debug.map"
DS_BASE = 0x36C700
byaddr = {}
for line in open(M, encoding="latin-1"):
    m = re.match(r"\s*0004:([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        off = int(m.group(1), 16)
        name = m.group(2)
        byaddr[DS_BASE + off] = name
# the vtable at 0x460D44
d = open(r"D:\mygame\halo2xbe\assets\halo2debug.xbe","rb").read()
base = struct.unpack_from("<I", d, 0x104)[0]
n = struct.unpack_from("<I", d, 0x11C)[0]
sh = struct.unpack_from("<I", d, 0x120)[0] - base
secs = []
for i in range(n):
    o = sh + i*56
    fl, va, vs, raw, rs, nm = struct.unpack_from("<6I", d, o)
    nm2 = d[nm-base:nm-base+16].split(b"\x00")[0].decode()
    secs.append((nm2, va, vs, raw, rs))
def read(va, count):
    for s in secs:
        if s[1] <= va < s[1]+s[4]:
            off = s[3] + va - s[1]
            return d[off:off+count]
    return b""
print("=== the CDirectSoundStream vtable at 0x460D44 ===")
for i in range(0, 96, 4):
    v = struct.unpack_from("<I", read(0x460D44+i, 4), 0)[0]
    nm = byaddr.get(v, "")
    print("   +0x%02X  0x%08X  %s" % (i, v, nm))
