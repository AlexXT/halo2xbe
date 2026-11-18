import re, sys, bisect, os
P = r'D:\mygame\halo2xbe'
sys.path.insert(0, P + r'\tools')
import map_ref
from name_pstencil import Xbe, build_string_index, build_push_index, literal_pattern, load_lifted

which = sys.argv[1] if len(sys.argv) > 1 else 'stencilshadow_draw'
mapfile = sys.argv[2] if len(sys.argv) > 2 else r'F:\Games\Halo 2 Beta\tools\bin\halo2tagdebug.map'
xbefile = sys.argv[3] if len(sys.argv) > 3 else P + r'\assets\halo2tagdebug.xbe'
funcsfile = sys.argv[4] if len(sys.argv) > 4 else P + r'\generated\tag\x86_func_mapping.cpp'
which_re = re.compile(which)

funcs, data = map_ref.parse(mapfile)
objs = {}
for e in funcs:
    objs.setdefault(e['obj'], {'fn': [], 'str': []})['fn'].append(e)
for e in data:
    objs.setdefault(e['obj'], {'fn': [], 'str': []})['str'].append(e)

xbe = Xbe(xbefile)
strings = build_string_index(xbe)
pushes = build_push_index(xbe)
lifted = load_lifted(funcsfile)

for obj, v in sorted(objs.items()):
    if not which_re.search(obj):
        continue
    v['fn'].sort(key=lambda e: e['start'])
    anchors = []
    matched = 0
    for e in v['str']:
        rp = literal_pattern(e['name'])
        if not rp:
            continue
        # the __FILE__ path is referenced by every assert in the file, so it
        # anchors nothing: a hundred functions of the object push it
        if '\\prophets\\source\\' in e['name'] or '?2prophets?2source' in e['name']:
            continue
        rx = re.compile(rp)
        best = None
        for text, sva in strings:
            if rx.match(text) and (best is None or len(text) > len(best[0])):
                best = (text, sva)
        if best is None:
            continue
        matched += 1
        for code in pushes.get(best[1], []):
            i = bisect.bisect_right(lifted, code) - 1
            if i >= 0:
                anchors.append((e['start'], lifted[i], best[0][:50]))
    anchors.sort()
    print('=== %s : %d fn, %d strings, %d matched, %d anchors'
          % (obj, len(v['fn']), len(v['str']), matched, len(anchors)))
    prev = -1
    mono = True
    for a, x, t in anchors:
        if x <= prev:
            mono = False
        prev = x
        print('    mapstr 0x%08X -> xbe 0x%08X  delta %+10d  %r' % (a, x, x - a, t))
    print('    order-preserving:', mono)
    print()
    print('    the object\'s map functions, in address order:')
    for e in v['fn']:
        print('      0x%08X  %s' % (e['start'], e['name'][:90]))
    print()
