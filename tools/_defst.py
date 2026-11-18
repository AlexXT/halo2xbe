import sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
md = Cs(CS_ARCH_X86, CS_MODE_32)
for a in (0x334740, 0x334860):
    print("=== the code at 0x%08X ===" % a)
    for ins in md.disasm(x.read_va(a, 0x60), a):
        print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
