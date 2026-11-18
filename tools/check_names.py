import re, sys, bisect, struct
P = r'D:\mygame\halo2xbe'
sys.path.insert(0, P + r'\tools')
from name_pstencil import Xbe, build_string_index, load_lifted

XBE = P + r'\assets\halo2tagdebug.xbe'
FUNCS = P + r'\generated\tag\x86_func_mapping.cpp'

d = open(XBE, 'rb').read()
xbe = Xbe(XBE)
strings = build_string_index(xbe)
lifted = load_lifted(FUNCS)
names = {}
for line in open(P + r'\work_pstencil_names.txt'):
    va, nm = line.split(None, 1)
    names[int(va, 16)] = nm.strip()

base = xbe.base
n = struct.unpack_from('<I', d, 0x11C)[0]
sh = struct.unpack_from('<I', d, 0x120)[0] - base
secs = []
for i in range(n):
    o = sh + i * 56
    _f, va, vsize, raw, rsize, nm = struct.unpack_from('<6I', d, o)
    secs.append((d[nm - base:nm - base + 16].split(b'\x00')[0].decode(), va, vsize, raw, rsize))


def fn_of(code):
    i = bisect.bisect_right(lifted, code) - 1
    return lifted[i] if i >= 0 else None


def refs(target):
    """Every in-place reference to a VA in the image."""
    pat = struct.pack('<I', target)
    out = []
    i = 0
    while True:
        i = d.find(pat, i)
        if i < 0:
            break
        for nm2, v, vs, r, rs in secs:
            if r <= i < r + rs:
                out.append((v + (i - r), nm2, d[max(0, i - 2):i + 6]))
                break
        i += 1
    return out


probes = ['static_data', 'stencil static', "it's bernie reverse or nuttin",
          'overflowed shared edge bitvector', 'bad shadow volumes',
          'stencil code blew the maximum strip', 'WARN tried to draw too many',
          'soft_planes', 'shared_edge_carmack_bitvector', 'node_indices',
          'adjacent_cluster_index', 'first_subcluster_offset',
          'unexpected rasterizer path taken', 'strip_index', 'skinned_vertices',
          'vertex_to_point_map', 'cluster_shared_edge_offsets']
for probe in probes:
    hits = [(t, v) for t, v in strings if probe.lower() in t.lower()]
    if not hits:
        print('%-38s (no such string in the XBE)' % probe)
        continue
    text, sva = hits[0]
    rs = refs(sva)
    print('%-38s VA 0x%08X  %r' % (probe[:38], sva, text[:44]))
    if not rs:
        print('      (no in-place reference -- dead or relocated)')
    for code, sec, ctx in rs[:3]:
        f = fn_of(code)
        print('      ref at 0x%08X (%s) %s' % (code, sec, ctx.hex(' ')))
        print('        -> function 0x%08X  %s' % (f, names.get(f, '(UNNAMED)')))
