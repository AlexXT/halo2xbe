"""Add the entries the runtime asks for, and rebuild, until it stops asking.

The runtime knows what it needs: when the guest calls something the lift
does not have, it says so and names the address.

    error: indirect call to 00310389 has no recompiled function
    error: add 0x310389 to [functions] in the image's config/*.toml and rebuild

This drives that loop: run the game, read the address out of the log, add it
to the config's [functions], rebuild, run again. The rebuild is cheap --
the recompiler only rewrites the generated files whose content changed, so
one extra entry rebuilds one or two of them.

    python fix_entries.py --config config/game.toml --exe Game.exe --rounds 40
"""

import argparse
import os
import re
import subprocess
import sys
import time

BUILD_DIR = r"D:\mygame\halo2xbe"
BUILD = 'build.bat'

ENV = {
    "PATH": (r"C:\Program Files\LLVM20\bin;"
             r"G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x86;"
             r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x86;"
             r"G:\Program Files\VisualStudio\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin;"
             r"G:\Program Files\VisualStudio\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja;"
             + os.environ.get("PATH", "")),
    "INCLUDE": (r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\ucrt;"
                r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\um;"
                r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\shared;"
                r"C:\Program Files (x86)\Windows Kits\10\Include\10.0.26100.0\winrt;"
                r"G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\include"),
    "LIB": (r"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0\um\x64;"
            r"C:\Program Files (x86)\Windows Kits\10\Lib\10.0.26100.0\ucrt\x64;"
            r"G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\lib\x64"),
}

WANT = re.compile(r"add 0x([0-9A-Fa-f]+) to \[functions\]")


def read_log(log):
    try:
        return open(log, errors="replace").read()
    except OSError:
        return ""


def add_functions(config, addrs):
    text = open(config, encoding="utf-8", errors="replace").read()
    lines = text.split("\n")
    out = []
    in_fn = False
    added = []
    for line in lines:
        # the TOML's section headers are indented, so strip before testing
        if line.strip() == "[functions]":
            in_fn = True
            out.append(line)
            for a in addrs:
                entry = '0x%X = ""' % a
                # do not write one that is already in the table
                if re.search(r"^\s*0x%X\s*=" % a, text, re.M):
                    continue
                out.append(entry)
                added.append(entry)
            continue
        if in_fn and line.strip().startswith("["):
            in_fn = False
        out.append(line)
    open(config, "w", encoding="utf-8", newline="").write("\n".join(out))
    return added


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--exe", required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--rounds", type=int, default=40)
    ap.add_argument("--run-seconds", type=int, default=25)
    args = ap.parse_args(argv)

    seen = set()
    for rnd in range(1, args.rounds + 1):
        env = dict(os.environ)
        env.update(ENV)
        try:
            os.remove(args.log)
        except OSError:
            pass
        p = subprocess.Popen([args.exe], cwd=os.path.dirname(os.path.abspath(args.exe)),
                             env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + args.run_seconds
        while time.time() < deadline and p.poll() is None:
            time.sleep(0.5)
        if p.poll() is None:
            p.kill()
            p.wait()
            print('[*] round %d: still running after %ds -- no missing entry'
                  % (rnd, args.run_seconds))
            return 0
        log = read_log(args.log)
        want = WANT.findall(log)
        if not want:
            print('[*] round %d: exited 0x%08X with no missing entry'
                  % (rnd, p.returncode & 0xFFFFFFFF))
            tail = [l for l in log.split("\n") if "error" in l or "warning" in l][-6:]
            for l in tail:
                print("    " + l)
            return 0
        addrs = []
        for w in want:
            a = int(w, 16)
            if a not in seen:
                seen.add(a)
                addrs.append(a)
        if not addrs:
            print('[*] round %d: the same entry again -- stopping' % rnd)
            return 1
        added = add_functions(args.config, addrs)
        print('[*] round %d: added %s' % (rnd, ', '.join(added)), flush=True)
        r = subprocess.run(["cmd", "/c", BUILD], cwd=BUILD_DIR, env=env,
                           capture_output=True, text=True)
        if r.returncode != 0:
            print('[!] the build failed (exit %d):' % r.returncode)
            print((r.stdout or '')[-2000:])
            return 1
        print('    rebuilt', flush=True)
    print('[*] gave up after %d rounds' % args.rounds)
    return 1


if __name__ == '__main__':
    sys.exit(main())
