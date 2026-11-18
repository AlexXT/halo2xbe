"""Fill the XDK DirectSound method addresses into the hand kept config.

The linker map of the Xbox build (halo2debug.map) names the XDK's dsound
library functions; the image links the same library, so a map offset in the
DSOUND section is the image's address with the section's base added.
"""
import re, sys

MAP = r"D:\mygame\game\halo2debug.map"
DSOUND_BASE = 0x36C700          # the image's DSOUND section
HAND = r"D:\mygame\halo2xbe\config\game_hand.toml"

# the names the host implements, from the runtime's STREAM() and BUFFER() lists
STREAM = "AddRef SetFormat Release GetInfo GetStatus Process Discontinuity Flush FlushEx Pause " \
         "SetVolume SetFrequency SetFilter SetHeadroom SetMixBinVolumes SetMixBins SetMode " \
         "SetRolloffCurve SetMaxDistance SetMinDistance SetDopplerFactor SetPosition SetVelocity " \
         "SetI3DL2Source".split()
BUFFER = "Release Unlock SetBufferData Play Pause PlayEx Stop StopEx SetPlayRegion SetLoopRegion " \
         "GetStatus GetCurrentPosition SetCurrentPosition Lock SetVolume SetFrequency SetPitch " \
         "GetVoiceProperties SetEG SetLFO SetConeAngles SetConeOutsideVolume SetDopplerFactor " \
         "Use3DVoiceData Set3DVoiceData SetFilter SetHeadroom SetMixBinVolumes SetMixBins " \
         "SetMaxDistance SetMode SetConeOrientation SetMinDistance SetPosition SetVelocity " \
         "SetI3DL2Source SetAllParameters SetRolloffCurve SetOutputBuffer SetFormat".split()

# the map's DSOUND symbols: offset -> mangled name
syms = {}
for line in open(MAP, encoding="latin-1"):
    m = re.match(r"\s*0004:([0-9a-f]{8})\s+(\S+)\s+([0-9a-f]{8})\s", line)
    if m:
        syms[int(m.group(1), 16)] = m.group(2)

# the methods of a class, by their mangled name
def find(method, cls):
    out = []
    for off, name in syms.items():
        if name.startswith("?%s@%s@" % (method, cls)):
            out.append((off, name))
    return out

wanted = {}
for m in STREAM:
    # the stream's own method, or the one it inherits from the voice
    hits = find(m, "CDirectSoundStream") or find(m, "CDirectSoundVoice")
    if hits:
        wanted["CDirectSoundStream_" + m] = DSOUND_BASE + hits[0][0]
for m in BUFFER:
    hits = find(m, "CDirectSoundBuffer") or find(m, "CDirectSoundVoice")
    if hits:
        wanted["IDirectSoundBuffer_" + m] = DSOUND_BASE + hits[0][0]

print("resolved %d names" % len(wanted))
for k in sorted(wanted):
    print("   %-44s = 0x%X" % (k, wanted[k]))

missing = [m for m in STREAM if "CDirectSoundStream_" + m not in wanted]
missing += ["IDirectSoundBuffer_" + m for m in BUFFER if "IDirectSoundBuffer_" + m not in wanted]
if missing:
    print("not in the map: " + ", ".join(missing))

# write them into the hand kept config
text = open(HAND, encoding="utf-8").read()
lines = []
for k in sorted(wanted):
    entry = "%s = 0x%X" % (k, wanted[k])
    if re.search(r"^\s*%s\s*=" % re.escape(k), text, re.M):
        text = re.sub(r"^(\s*)%s\s*=.*$" % re.escape(k), r"\1" + entry, text, flags=re.M)
    else:
        text = text.rstrip() + "\n" + entry + "\n"
open(HAND, "w", encoding="utf-8", newline="\n").write(text)
print("written to", HAND)
