import struct, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
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
rdata, rva = blob(".rdata")
ds, dsva = blob("DSOUND")
dslo, dshi = dsva, dsva+len(ds)
print("=== .rdata 0x460D28..0x460D60 ===")
for a in range(0x460D28, 0x460D60, 4):
    off = a - rva
    v = struct.unpack_from("<I", rdata, off)[0]
    kind = "code" if dslo <= v < dshi else "rtti/data"
    print("   0x%08X: 0x%08X  %s" % (a, v, kind))
# the constructor that stores 0x460D44 and 0x460D38
dsb = ds
pat = bytes.fromhex("C706") + struct.pack("<I", 0x460D44)
i = dsb.find(pat)
print("=== the constructor at 0x%08X ===" % (dsva + i))
md = Cs(CS_ARCH_X86, CS_MODE_32)
start = dsva + i
# walk back to the function start: look for a preceding ret/padding
lo = max(0, i - 64)
for j in range(i, lo, -1):
    if dsb[j] in (0xC3, 0xCC, 0x90):
        j += 1
        break
for ins in md.disasm(dsb[j:j+96], dsva + j):
    print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
    if ins.mnemonic == "ret": break
