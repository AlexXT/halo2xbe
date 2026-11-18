import struct, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
target = 0x36EB51
md = Cs(CS_ARCH_X86, CS_MODE_32)
for sec, va, size in ((".text", 0x11000, 0x322550), ("DSOUND", 0x36C700, 0x25FF4)):
    b = x.read_va(va, size)
    i = 0
    while True:
        i = b.find(b"\xE8", i)
        if i < 0: break
        if i + 5 <= len(b):
            rel = struct.unpack_from("<i", b, i+1)[0]
            if va + i + 5 + rel == target:
                call = va + i
                print("=== the call to 0x%08X at 0x%08X (%s) ===" % (target, call, sec))
                start = max(0, i - 40)
                for ins in md.disasm(b[start:i+20], va+start):
                    mark = "   <<<" if ins.address == call else ""
                    print("   0x%08X  %-8s %s%s" % (ins.address, ins.mnemonic, ins.op_str, mark))
        i += 1
