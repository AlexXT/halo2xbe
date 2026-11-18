import sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
b = x.read_va(0x31035F, 0x60)
md = Cs(CS_ARCH_X86, CS_MODE_32)
for i in md.disasm(b, 0x31035F):
    mark = ""
    if i.address == 0x310389: mark = "   <<<< the callback"
    print("   0x%08X  %-8s %-30s%s" % (i.address, i.mnemonic, i.op_str, mark))
    if i.address >= 0x3103A0: break
