import re, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
best = None
for line in open(r"D:\mygame\game\halo2debug.map", encoding="latin-1"):
    m = re.match(r"\s*0002:([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        off = int(m.group(1), 16)
        if off <= 0x7CA and (best is None or off > best[0]): best = (off, m.group(2))
print("the function at 0x333D2A is", best[1])
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
md = Cs(CS_ARCH_X86, CS_MODE_32)
print("=== the code around 0x333D2A ===")
for ins in md.disasm(x.read_va(0x333D00, 0x60), 0x333D00):
    mark = "   <<<" if ins.address == 0x333D2A else ""
    print("   0x%08X  %-8s %s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
