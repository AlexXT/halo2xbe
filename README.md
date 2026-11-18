# halo2xbe — the Halo 2 May 2003 Xbox builds, recompiled and named

The Xbox side of project 2. The PC side (the `blam.exe` / `sapien.exe` tools
from the same 2003 build) is a separate project: an XBE is not a PE, so the
Xbox builds use an XBE recompiler and the PC tools need a PE one.

The aim here is the *pstencil* module — the "spicy" stencil shadow volumes
Bungie cut before retail. The beta debug build still carries all of it, so
recompiling it makes the algorithm static C that can actually be read.

The toolbox is the
[hk21x fork of TGP482/XboxXBERecomp](https://github.com/AlexXT/XboxXBERecomp),
forked here with the Halo 2 fixes on top (upstream:
[TGP482/XboxXBERecomp](https://github.com/TGP482/XboxXBERecomp)).

---

## What is here

Committed:

```
config/
  game.toml           the recompiler's input for halo2debug.xbe
  game_hand.toml      the hand-maintained config that includes it
  tag.toml            ... and for halo2tagdebug.xbe
src/
  common/game_info.cpp
  game/hooks.cpp
tools/                the project's own tools (see below)
docs/, scripts/, launcher/, .github/
```

Produced locally and gitignored:

```
assets/               the two XBEs and the game's data folders — supply your own
generated/
  game/               33,756 functions lifted, 117 files
  tag/                36,414 functions lifted, 133 files
out/build/release/    Game.exe, the running recompiled game
```

---

## Building and running

```bat
build.bat            configure, lift both XBEs, build Game.exe
build.bat clean      the same, with the CMake cache removed first
```

`CMakeLists.txt` takes `SDK` (the path to your checkout of the patched fork)
and the optional local dependency-cache paths as CMake cache variables.

The game needs its XBE and its data folders beside the exe. Without the data
it opens a window and shows black: the recomp works, the content is missing.

`logs/halo2.log` is the runtime's own log — it names the XBE, the D3D12
adapter, the render thread, and every error.

---

## The tools here

| | |
|---|---|
| `name_by_order.py` | places the linker map's names on the XBE |
| `inject_names.py` | writes them into the config as `[names]` |
| `check_names.py` | checks the naming against the code's own assert strings |
| `find_missing_entries.py` | finds the code pointers with no recompiled function |
| `fix_entries.py` | drives the runtime's "add this to [functions]" loop |
| `extract_named.py` | gathers the named functions into one file |
| `diag_align.py` | the alignment diagnostic, per object |

### Why the names needed work

The recompiler writes every function as `sub_XXXXXXXX`. The names exist — in
the linker map — but the map describes a **PE link** and the XBE is a
**different link of the same sources**, so a map address lands elsewhere.
Measured: the best constant offset between them matches 19% of the functions.

So the names are placed by content instead. A linker map lists, per object
file, the functions **and the string constants that object contributed**. The
constants are the same text in both links, and an object's code is laid out
in **source order** in both, so the map's function list and the XBE's
function list line up by order.

The map encodes a literal's text inside the mangled symbol
(`??_C@_0BM@MBGELAOF@read_file_success@`), with the characters that are not
alphanumeric written as `?X` — `?5` is a space, `?2` is a slash. The
encoding is not decoded: the encoded text becomes a *pattern* and is matched
against the XBE's strings as a prefix, because the map truncates long literals.

Checked against the code's own assertions:

| the assert the function pushes | the name it was given |
|---|---|
| `stencil code blew the maximum strip size` | `shadow_strip_builder` |
| `skinned_vertices` | `section_skin_from_rigid_point_groups` |
| `vertex_to_point_map[vertex_index]>=0` | `..._isq_cluster_shadow_draw_submit_shared_edges` |
| `unexpected rasterizer path taken` | `append_stitch_quad_to_list_explicit` |
| `it's bernie reverse or nuttin` | `rasterizer_draw_shadow_stitches_internal` |
| `###WARN tried to draw too many stitch quads` | `rasterizer_render_model_draw_shadow_caps` |

Six for six.

### What the fork carries

The patched fork has an upstream `[names]` feature the original `hk21x` fork
did not carry, plus two things ported from an older working tree:

* `tools/recomp/analysis.h` — `Config::named_functions`
* `tools/recomp/main.cpp` — read a `[names]` table from the config
* `tools/recomp/codegen.cpp` — `FuncName` consults it before falling back
  to `sub_%08X`
* the `xbdm.dll` host (the Xbox debug connection)
* the **XDK 5455 signatures** — the XDK build the Halo 2 beta is, which
  neither the original fork nor upstream ships

---

## The two defects fixed on the way

**The host's image base.** The host was linked at `/BASE:0x70000000`. Its
image is 124 MB, so it spans `0x70000000`–`0x7768DFFF`, and on 64-bit
Windows a 32-bit process has its system DLLs mapped at `0x77000000` and
above. The loader rejected the image with `ERROR_INVALID_EXE_START` before
`main()` ran. It read as a link-flag problem because a 60 KB test executable
at the same base runs perfectly — it is an *address* problem, and the size is
what reached the system DLLs. Now `/BASE:0x20000000`.

**The physical memory.** The debug build asks for 53 MB of contiguous
physical memory in one block, and the fork's 64 MB guest pool does not fit
it. The old tree had solved this and its comment says why:

    // The physical memory a development kit had: a debug build takes most of it for one
    // block (Halo 2's takes 54 MB), so the host keeps room for its own buffers.

That comment is *Halo 2 specific* — it was written for this game. The fork's
64 MB scheme replaced it. The fix keeps the fork's structure and restores the
size: 128 MB for the title, 64 MB for the host's own buffers.

**The lesson**: when two forks of the same toolkit disagree, the one with
the *specific* comment is usually the one that was debugged against the thing
in front of you. Read the diff before taking a side.
