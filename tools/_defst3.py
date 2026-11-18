import struct, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
ds = x.read_va(0x333560, 0x2DFA0)
pat = struct.pack("<I", 0x41AD0)
i = 0
n = 0
while n < 6:
    i = ds.find(pat, i)
    if i < 0: break
    va = 0x333560 + i
    print("   0x%08X" % va)
    i += 1; n += 1
# the code around the first one
i = ds.find(pat)
start = max(0, i - 40)
md = Cs(CS_ARCH_X86, CS_MODE_32)
print("=== the code around it ===")
for ins in md.disasm(ds[start:i+30], 0x333560+start):
    print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
