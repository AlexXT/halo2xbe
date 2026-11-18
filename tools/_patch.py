import re, glob, os
f = r"D:\mygame\halo2xbe\tools\fill_hand.py"
s = open(f, encoding="utf-8").read()
s = s.replace('''        m = re.match(r"\\s*HLE_(?:STDCALL|FASTCALL)\\\((\\w+)\\s*,", line)
        if m: host.add(m.group(1))''',
'''        m = re.match(r"\\s*HLE_(?:STDCALL|FASTCALL)\\((\\w+)\\s*,", line)
        if m:
            host.add(m.group(1))
            continue
        # the stream and buffer methods are made by a macro, so their names are in its uses
        m = re.match(r"\\s*(?:STREAM|BUFFER)\\((\\w+)\\s*,", line)
        if m:
            host.add(("CDirectSoundStream_" if m.group(0).lstrip().startswith("STREAM") else "IDirectSoundBuffer_") + m.group(1))''')
open(f, "w", encoding="utf-8", newline="\n").write(s)
print("the script now sees the macro's methods")
