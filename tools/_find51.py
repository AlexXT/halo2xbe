import struct, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
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
pat = struct.pack("<I", 0x36EB51)
for nm2, va, vs, raw, rs in secs:
    blob = d[raw:raw+rs]
    i = 0
    while True:
        i = blob.find(pat, i)
        if i < 0: break
        a = va + i
        print("0x%08X (%s) holds 0x36EB51" % (a, nm2))
        # print the neighbours
        for k in range(-6, 7):
            v = struct.unpack_from("<I", read(a + k*4, 4), 0)[0]
            print("      %+0x%02X: 0x%08X" % (k*4, v))
        i += 1
