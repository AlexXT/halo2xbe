import struct, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
ds = x.read_va(0x333560, 0x2DFA0)
for target in (0x362570, 0x362120):
    pat = struct.pack("<I", target)
    i = ds.find(pat)
    print("=== the config's %08X in the D3D library: %s ===" % (target, "found" if i >= 0 else "NOT FOUND"))
    n = 0
    while i >= 0 and n < 4:
        va = 0x333560 + i
        print("   at 0x%08X" % va)
        i = ds.find(pat, i+1); n += 1
# the guest's own state block: look for the writes of a render state value near a base address
md = Cs(CS_ARCH_X86, CS_MODE_32)
print()
print("=== the guest's code around the config's D3D_RenderState ===")
i = ds.find(struct.pack("<I", 0x362570))
if i >= 0:
    start = max(0, i - 24)
    for ins in md.disasm(ds[start:i+24], 0x333560+start):
        print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
