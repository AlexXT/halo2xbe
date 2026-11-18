import sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
md = Cs(CS_ARCH_X86, CS_MODE_32)
print("=== the code at 0x33E43C (the other path) ===")
for ins in md.disasm(x.read_va(0x33E43C, 0x60), 0x33E43C):
    print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
    if ins.mnemonic == "ret": break
