import re, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
# the map's name for the function at 0x33B439
best = None
for line in open(r"D:\mygame\game\halo2debug.map", encoding="latin-1"):
    m = re.match(r"\s*0002:([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        off = int(m.group(1), 16)
        if off <= 0x7ED9 and (best is None or off > best[0]): best = (off, m.group(2))
print("the function at 0x33B439 is", best[1])
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
md = Cs(CS_ARCH_X86, CS_MODE_32)
print("=== the code around the compare ===")
for ins in md.disasm(x.read_va(0x33B420, 0x40), 0x33B420):
    print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
