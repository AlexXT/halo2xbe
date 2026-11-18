import re, sys, bisect, os
P = r'D:\mygame\halo2xbe'
sys.path.insert(0, P + r'\tools')
import map_ref
from name_pstencil import Xbe, build_string_index, build_push_index, literal_pattern, load_lifted

MAP = r'F:\Games\Halo 2 Beta\tools\bin\halo2tagdebug.map'
XBE = P + r'\assets\halo2tagdebug.xbe'
FUNCS = P + r'\generated\tag\x86_func_mapping.cpp'

funcs, data = map_ref.parse(MAP)
xbe = Xbe(XBE)
strings = build_string_index(xbe)
pushes = build_push_index(xbe)
lifted = load_lifted(FUNCS)
names = {}
for line in open(P + r'\work_pstencil_names.txt'):
    va, nm = line.split(None, 1)
    names[int(va, 16)] = nm.strip()

# the map's string symbols, with the object they belong to
str_obj = {}
for e in data:
    str_obj.setdefault(e['name'], []).append(e['obj'])


def fn_of(code):
    i = bisect.bisect_right(lifted, code) - 1
    return lifted[i] if i >= 0 else None


def xbe_str(text_prefix):
    for text, sva in strings:
        if text_prefix.lower() in text.lower():
            return sva, text
    return None, None


# CHECK 1: the 'static_data' string belongs to rasterizer_xbox_stencilshadow_draw.obj,
# and the function that pushes it should be the one named
# rasterizer_xbox_stencilshadow_draw_initialize.
print('=== check: which function pushes "static_data", and what is it named? ===')
sva, text = xbe_str('static_data')
print('  XBE string %r at VA 0x%08X' % (text, sva))
for code in pushes.get(sva, []):
    f = fn_of(code)
    print('  pushed at 0x%08X -> function 0x%08X  named: %s'
          % (code, f, names.get(f, '(unnamed)')))

print()
print('=== check: the "stencil static" string ===')
sva, text = xbe_str('stencil static')
print('  XBE string %r at VA 0x%08X' % (text, sva))
for code in pushes.get(sva, []):
    f = fn_of(code)
    print('  pushed at 0x%08X -> function 0x%08X  named: %s'
          % (code, f, names.get(f, '(unnamed)')))

print()
print('=== check: "it s bernie reverse or nuttin" (the draw object) ===')
for pref in ('it s bernie', 'it?5s?5bernie'):
    sva, text = xbe_str(pref)
    if sva:
        print('  XBE string %r at VA 0x%08X' % (text, sva))
        for code in pushes.get(sva, []):
            f = fn_of(code)
            print('    pushed at 0x%08X -> function 0x%08X  named: %s'
                  % (code, f, names.get(f, '(unnamed)')))
        break

print()
print('=== check: "overflowed shared edge bitve" (the compute object) ===')
sva, text = xbe_str('overflowed shared edge')
if sva:
    print('  XBE string %r at VA 0x%08X' % (text, sva))
    for code in pushes.get(sva, []):
        f = fn_of(code)
        print('    pushed at 0x%08X -> function 0x%08X  named: %s'
              % (code, f, names.get(f, '(unnamed)')))
