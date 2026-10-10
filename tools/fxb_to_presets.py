#!/usr/bin/env python3
"""Turn OB-Xd .fxb preset banks into vst/presets.json for the MPC port (MPC's PRESET menu).

  python3 tools/fxb_to_presets.py "<bank>.fxb" ["<bank2>.fxb" ...] [-o vst/presets.json] [--skip-unnamed]
  python3 tools/fxb_to_presets.py --local ~/obxd-files/opt/obxd/discoDSP/OB-Xd/Banks/*.fxb banks/*.fxb --skip-unnamed

--local writes vst/presets.local.json for YOUR OWN device only (build.sh then builds with it); it is git-ignored, so banks you
may not redistribute (such as discoDSP's factory banks) never end up in the repository or a public release.

Reads the banks you give it (from your own OB-Xd install); nothing is bundled. Handles OB-Xd's chunk banks
(FBCh, binary XML with Val_<n> attributes) and plain FxBk banks. Parameter numbers follow the 2.10 enum in
src/obxd/ParamsEnum.h; a bank that uses numbers beyond it is reported, and those values are ignored.
"""
import argparse, json, os, re, struct, sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def enum_names():
    s = open(os.path.join(ROOT, "src/obxd/ParamsEnum.h"), encoding="latin-1").read()
    s = s[s.index("enum ObxdParameters"):]
    s = s[s.index("{") + 1:s.index("}")]
    return re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", s)

def read_chunk_xml(d):
    # fxChunkSet: 'CcnK' size 'FBCh' ver id fxver nprog future[128] chunkSize chunk; chunk = JUCE binary XML
    csize = struct.unpack(">i", d[156:160])[0]
    chunk = d[160:160 + csize]
    magic, size = struct.unpack("<II", chunk[:8])
    if magic != 0x21324356:
        raise ValueError("chunk is not OB-Xd/JUCE binary XML")
    return chunk[8:8 + size].split(b"\0")[0].decode("utf-8", "replace")

def programs_from_fxbk(d):
    n = struct.unpack(">i", d[24:28])[0]
    off, out = 156, []
    for _ in range(n):
        if d[off:off + 4] != b"CcnK":
            raise ValueError("bad program header")
        bsz = struct.unpack(">i", d[off + 4:off + 8])[0]
        nparam = struct.unpack(">i", d[off + 24:off + 28])[0]
        name = d[off + 28:off + 56].split(b"\0")[0].decode("latin-1")
        vals = struct.unpack(">%df" % nparam, d[off + 56:off + 56 + 4 * nparam])
        out.append((name, {str(i): v for i, v in enumerate(vals)}, True))
        off += 8 + bsz
    return out

def load_bank(path):
    d = open(path, "rb").read()
    if d[:4] != b"CcnK":
        raise ValueError("not an fxb file")
    kind = d[8:12]
    if kind == b"FBCh":
        xml = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", read_chunk_xml(d))  # some banks have a bare & in a name
        xml = re.sub(r'(\s)(\d+)="', r'\1Val_\2="', xml)   # old banks number values without the Val_ prefix
        root = ET.fromstring(xml)
        out = []
        for e in root.iter("program"):
            new = "voiceCount" in e.attrib
            vals = {}
            for k, v in e.attrib.items():
                m = re.fullmatch(r"(?:Val_)?(\d+)", k)
                if m:
                    vals[m.group(1)] = float(v)
            out.append((e.attrib.get("programName", "Default"), vals, new))
        return out
    if kind == b"FxBk":
        return programs_from_fxbk(d)
    raise ValueError("unsupported bank type %r" % kind)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("banks", nargs="+")
    ap.add_argument("-o", "--out", default=os.path.join(ROOT, "vst/presets.json"))
    ap.add_argument("--local", action="store_true", help="write vst/presets.local.json (private, git-ignored) and leave vst.json alone")
    ap.add_argument("--skip-unnamed", action="store_true", help="drop programs still called Default/Init")
    a = ap.parse_args()
    if a.local:
        a.out = os.path.join(ROOT, "vst/presets.local.json")

    names = enum_names()
    params = json.load(open(os.path.join(ROOT, "vst/params.json")))["params"]
    order = [(p["key"], p) for p in params]
    idx = {n.lower(): i for i, n in enumerate(names)}
    presets, beyond = [], 0
    for path in a.banks:
        label = re.sub(r"^\d+\s*-\s*", "", os.path.splitext(os.path.basename(path))[0])
        for n, (pname, vals, new) in enumerate(load_bank(path)):
            if a.skip_unnamed and pname.strip().lower() in ("default", "init", ""):
                continue
            beyond += sum(1 for k in vals if int(k) >= len(names))
            out = {}
            for key, p in order:
                if key not in idx:      # not an OB-Xd engine parameter (master_hz): a preset leaves it alone
                    continue
                i = idx[key]
                v = vals.get(str(i), p.get("default", 0) if "options" not in p else p["default"])
                if key == "voice_count" and not new:
                    v *= 0.25
                v = min(1.0, max(0.0, float(v)))
                out[key] = ("On" if v > 0.5 else "Off") if "options" in p else round(v, 6)
            presets.append({"name": (pname.strip() or "Program %d" % (n + 1))[:28], "values": out})
    json.dump({"presets": presets}, open(a.out, "w"), indent=0)
    print("wrote %d presets to %s" % (len(presets), a.out))
    if a.local:
        print("private presets: build.sh will use vst/presets.local.json (not committed)")
        return
    cfg_path = os.path.join(ROOT, "vst/vst.json")      # make the build pick the file up (safe to repeat)
    cfg = json.load(open(cfg_path))
    if cfg.get("presets") != os.path.basename(a.out) and os.path.dirname(os.path.abspath(a.out)) == os.path.dirname(cfg_path):
        cfg["presets"] = os.path.basename(a.out)
        json.dump(cfg, open(cfg_path, "w"), indent=2)
        print('added "presets" to vst/vst.json')
    if beyond:
        print("note: %d values used parameter numbers beyond OB-Xd 2.10's list and were ignored" % beyond)

if __name__ == "__main__":
    main()
