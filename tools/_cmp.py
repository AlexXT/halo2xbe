import re
gen = open(r"D:\mygame\halo2xbe\config\game.toml", encoding="utf-8", errors="replace").read()
hand = open(r"D:\mygame\halo2xbe\config\game_hand.toml", encoding="utf-8", errors="replace").read()
gv = {m.group(1): m.group(2) for m in re.finditer(r"^\s*(\w+)\s*=\s*(0x[0-9A-Fa-f]+|0)\s*$", gen, re.M)}
hv = {m.group(1): m.group(2) for m in re.finditer(r"^\s*(\w+)\s*=\s*(0x[0-9A-Fa-f]+|0)\s*$", hand, re.M)}
diff = []
for n, v in sorted(hv.items()):
    if n in gv and gv[n] != "0" and gv[n].lower() != v.lower():
        diff.append((n, gv[n], v))
print("the hand file says %d names; %d differ from the scan" % (len(hv), len(diff)))
for n, a, b in diff: print("   %-44s scan %s  hand %s" % (n, a, b))
