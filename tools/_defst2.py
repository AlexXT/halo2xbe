import struct, sys
sys.path.insert(0, r"C:\Program Files\LLVM20\bin")
from capstone import *
sys.path.insert(0, r"D:\mygame\halo2xbe\tools")
from name_pstencil import Xbe
x = Xbe(r"D:\mygame\halo2xbe\assets\halo2debug.xbe")
ds = x.read_va(0x333560, 0x2DFA0)
# the default colour op (2) at the stage 0 offset 12: 0x362120 + 48 = 0x362150
for addr, val in ((0x362150, 2), (0x362120, 2), (0x362154, 2)):
    pat = b"\xC7\x05" + struct.pack("<I", addr) + struct.pack("<I", val)
    i = ds.find(pat)
    print("   mov dword ptr [%08X], %d : %s" % (addr, val, ("at 0x%08X" % (0x333560+i)) if i >= 0 else "not found"))
# the ambient colour (0xFFFFFFFF) at the render state 105: 0x362570 + 420 = 0x362704
for addr in (0x362704, 0x362570 + 420):
    pat = b"\xC7\x05" + struct.pack("<I", addr) + struct.pack("<I", 0xFFFFFFFF)
    i = ds.find(pat)
    print("   the ambient (0xFFFFFFFF) at %08X : %s" % (addr, ("at 0x%08X" % (0x333560+i)) if i >= 0 else "not found"))
