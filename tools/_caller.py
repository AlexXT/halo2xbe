import sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
md = Cs(CS_ARCH_X86, CS_MODE_32)
print("=== the caller of sub_0036D5C6 (0x36EB86) ===")
for ins in md.disasm(x.read_va(0x36EB40, 0x70), 0x36EB40):
    mark = "   <<<" if ins.address == 0x36EB86 else ""
    print("   0x%08X  %-8s %-34s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
    if ins.address > 0x36EBA0: break
