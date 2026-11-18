import re, os, glob
N = r"D:\mygame\XboxXBE-Recomp-fork\runtime"
names = set()
for f in glob.glob(os.path.join(N, "**", "*.cpp"), recursive=True):
    for line in open(f, encoding="latin-1"):
        m = re.match(r"\s*HLE_(?:STDCALL|FASTCALL)\((\w+)\s*,", line)
        if m: names.add(m.group(1))
print("the host implements %d functions" % len(names))
cfg = r"D:\mygame\halo2xbe\config\game.toml"
text = open(cfg, encoding="utf-8", errors="replace").read()
have = {}
for m in re.finditer(r"^\s*(\w+)\s*=\s*(0x[0-9A-Fa-f]+|0)\s*$", text, re.M):
    have[m.group(1)] = m.group(2)
missing = sorted(n for n in names if have.get(n, "0") == "0")
absent = sorted(n for n in names if n not in have)
print("  named in the config but at 0: %d" % len(missing))
print("  not in the config at all: %d" % len(absent))
print("  the first 40 that are 0:")
for n in missing[:40]: print("    " + n)
