import re, sys, bisect, os, json

P = r'D:\mygame\halo2xbe'
sys.path.insert(0, P + r'\tools')
import map_ref
from name_pstencil import Xbe, build_string_index, build_push_index, literal_pattern, load_lifted, demangle

MAP = sys.argv[2] if len(sys.argv) > 2 else r'F:\Games\Halo 2 Beta\tools\bin\halo2tagdebug.map'
XBE = sys.argv[3] if len(sys.argv) > 3 else P + r'\assets\halo2tagdebug.xbe'
FUNCS = sys.argv[4] if len(sys.argv) > 4 else P + r'\generated\tag\x86_func_mapping.cpp'
OUT = sys.argv[5] if len(sys.argv) > 5 else P + r'\work_pstencil_names.txt'
WHICH = re.compile(sys.argv[1] if len(sys.argv) > 1 else 'stencilshadow')

funcs, data = map_ref.parse(MAP)
objs = {}
for e in funcs:
    objs.setdefault(e['obj'], {'fn': [], 'str': []})['fn'].append(e)
for e in data:
    objs.setdefault(e['obj'], {'fn': [], 'str': []})['str'].append(e)

# The D3D8I library's stubs are linked into the game's objects but live in
# the XBE's own D3D section, not in .text next to the object that lists them.
# Keeping them in the count shifts the whole alignment, so they go.
IMPORT_THUNK = re.compile(r'^_IDirect3D|^__imp__|^_\$E')


def is_thunk(name):
    return bool(IMPORT_THUNK.match(name))

xbe = Xbe(XBE)
strings = build_string_index(xbe)
pushes = build_push_index(xbe)
lifted = load_lifted(FUNCS)


def fn_of(code):
    i = bisect.bisect_right(lifted, code) - 1
    return lifted[i] if i >= 0 else None


named = {}
for obj, v in sorted(objs.items()):
    # an object counts if its FILE name matches, or if any of its FUNCTIONS
    # do: the per-pass stencil variants live in rasterizer_xbox_models.obj and
    # rasterizer_xbox_environment.obj, whose file names say nothing about
    # pstencil.
    hit = WHICH.search(obj)
    if not hit:
        hit = any(WHICH.search(e['name']) for e in v['fn'])
    if not hit:
        continue
    v['fn'].sort(key=lambda e: e['start'])
    v['fn'] = [e for e in v['fn'] if not is_thunk(e['name'])]
    v['str'].sort(key=lambda e: e['start'])

    # the object's source file: the __FILE__ string it contributed
    file_str = None
    for e in v['str']:
        if '?2prophets?2source' in e['name'] or '\\prophets\\source\\' in e['name']:
            file_str = e
            break

    # every XBE function that pushes one of the object's strings
    cand = {}
    for e in v['str']:
        rp = literal_pattern(e['name'])
        if not rp:
            continue
        rx = re.compile(rp)
        best = None
        for text, sva in strings:
            if rx.match(text) and (best is None or len(text) > len(best[0])):
                best = (text, sva)
        if best is None:
            continue
        for code in pushes.get(best[1], []):
            f = fn_of(code)
            if f is not None:
                cand.setdefault(f, set()).add(best[0])

    # the object's code is contiguous in the XBE too: take the cluster of
    # candidate functions that are close together (a stray pattern match
    # thousands of bytes away would otherwise stretch the run)
    if not cand:
        print('[!] %s: no candidates' % obj)
        continue
    cs = sorted(cand)
    clusters = [[cs[0]]]
    for f in cs[1:]:
        if f - clusters[-1][-1] > 0x1000:
            clusters.append([f])
        else:
            clusters[-1].append(f)
    cluster = max(clusters, key=len)
    i0 = bisect.bisect_left(lifted, cluster[0])
    run = lifted[i0:i0 + len(v['fn'])]
    print('=== %s' % obj)
    print('    map: %d functions, %d strings' % (len(v['fn']), len(v['str'])))
    print('    xbe: %d candidate functions, cluster of %d, run %d functions'
          % (len(cand), len(cluster), len(run)))
    if file_str:
        print('    source file: %s' % file_str['name'][:70])

    if len(run) == len(v['fn']):
        for e, x in zip(v['fn'], run):
            nm = demangle(e['name'])
            if nm:
                named[x] = nm
        print('    aligned %d functions by order' % len(run))
    else:
        print('    counts differ (%d vs %d): aligning on the cluster'
              % (len(run), len(v['fn'])))
        for e, x in zip(v['fn'], run):
            nm = demangle(e['name'])
            if nm:
                named[x] = nm

print()
print('[*] named %d functions' % len(named))
out = OUT
with open(out, 'w') as f:
    for va in sorted(named):
        f.write('0x%08X %s\n' % (va, named[va]))
print('[*] wrote %s' % out)
for va in sorted(named)[:30]:
    print('    0x%08X  %s' % (va, named[va]))
