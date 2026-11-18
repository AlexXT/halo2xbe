import struct
d = open(r"D:\mygame\halo2xbe\assets\halo2debug.xbe","rb").read()
base = struct.unpack_from("<I", d, 0x104)[0]
hdr  = struct.unpack_from("<I", d, 0x108)[0]
img  = struct.unpack_from("<I", d, 0x10C)[0]
print("base 0x%08X header size 0x%X image size 0x%X (0x%08X..0x%08X)" % (base, hdr, img, base, base+img))
print("0x3F800004 inside the image:", base <= 0x3F800004 < base + img)
