import struct, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
ds = x.read_va(0x36C700, 0x25FF4)
pat = bytes.fromhex("C706440D4600C707380D4600")
i = ds.find(pat)
md = Cs(CS_ARCH_X86, CS_MODE_32)
while i >= 0:
    va = 0x36C700 + i
    print("=== the vtable store at 0x%08X ===" % va)
    # walk back to the function start
    j = i
    while j > 0 and ds[j] not in (0xC3, 0xCC):
        j -= 1
    start = j + 1
    for ins in md.disasm(ds[start:start+120], 0x36C700+start):
        print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
        if ins.mnemonic == "ret": break
    print()
    i = ds.find(pat, i+1)
