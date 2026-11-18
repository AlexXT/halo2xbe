import struct, sys
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
    name = d[nm-base:nm-base+16].split(b"\x00")[0].decode()
    secs.append((name, va, vs, raw, rs))
text = [s for s in secs if s[0] == ".text"][0]
name, va, vs, raw, rs = text
blob = d[raw:raw+rs]
lo, hi = va, va+rs
pushes, movmem, movreg = set(), set(), set()
i = 0
while i < len(blob)-5:
    b0 = blob[i]
    if b0 == 0x68:                      # push imm32
        pushes.add(struct.unpack_from("<I", blob, i+1)[0]); i += 5; continue
    if b0 == 0xC7 and blob[i+1] == 0x05:   # mov dword ptr [disp32], imm32
        movmem.add(struct.unpack_from("<I", blob, i+6)[0]); i += 10; continue
    if b0 == 0xA3:                      # mov moffs32, eax
        movmem.add(struct.unpack_from("<I", blob, i+1)[0]); i += 5; continue
    if 0xB8 <= b0 <= 0xBF:              # mov reg, imm32
        movreg.add(struct.unpack_from("<I", blob, i+1)[0]); i += 5; continue
    i += 1
def incode(v): return lo <= v < hi
print("push imm32      -> %d in .text" % len([v for v in pushes if incode(v)]))
print("mov [mem], imm  -> %d in .text" % len([v for v in movmem if incode(v)]))
print("mov reg, imm    -> %d in .text" % len([v for v in movreg if incode(v)]))
allv = sorted({v for v in (pushes|movmem|movreg) if incode(v)})
print("distinct code addresses named by an immediate: %d" % len(allv))
print("  0x310389 in the set:", 0x310389 in allv)
