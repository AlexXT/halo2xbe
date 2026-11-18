import re, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
def name_at(off):
    best = None
    for line in open(r"D:\mygame\game\halo2debug.map", encoding="latin-1"):
        m = re.match(r"\s*0002:([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
        if m:
            o = int(m.group(1), 16)
            if o <= off and (best is None or o > best[0]): best = (o, m.group(2))
    return best[1]
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
md = Cs(CS_ARCH_X86, CS_MODE_32)
for va in (0x33426E, 0x334BF3, 0x333DF6, 0x333E4B, 0x33A9BE):
    off = va - 0x333560
    print("=== 0x%08X is in %s ===" % (va, name_at(off)))
    for ins in md.disasm(x.read_va(va - 12, 30), va - 12):
        print("   0x%08X  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
