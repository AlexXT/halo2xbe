import re, glob, os
files = [
  r"D:\mygame\xbox trunk\xbox\public\xdk\inc\d3d8types.h",
  r"D:\mygame\xbox trunk\xbox\public\sdk\inc\d3d8types.h",
  r"D:\mygame\xbox trunk\xbox\private\inc\aug01\d3d8types.h",
  r"D:\mygame\xbox trunk\xbox\public\wsdk\inc\dx8\d3d8types.h",
]
for f in files:
    if not os.path.exists(f): 
        print("  (missing) %s" % f); continue
    text = open(f, encoding="latin-1").read()
    m = re.search(r"typedef enum _D3DRENDERSTATETYPE \{(.*?)\}", text, re.S)
    if not m:
        print("  (no enum) %s" % f); continue
    st = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"\s*(D3DRS_\w+)\s*=\s*(\d+)", line)
        if mm: st[int(mm.group(2))] = mm.group(1)
    print("  %s" % f.replace(r"D:\mygame\xbox trunk\xbox", ""))
    print("     92=%s 93=%s 102=%s 105=%s 110=%s 115=%s 118=%s" % (st.get(92), st.get(93), st.get(102), st.get(105), st.get(110), st.get(115), st.get(118)))
    print("     %d states" % len(st))
