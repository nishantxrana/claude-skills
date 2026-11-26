#!/usr/bin/env python3
"""snap.py - edit history for the resume (save before every edit, diff, restore).

  python snap.py save resume.tex --note "before ToolDock update"
  python snap.py list
  python snap.py diff [SNAP] [--against resume.tex]     # default: latest snapshot vs current file
  python snap.py restore SNAP resume.tex                # saves the current file first, then restores

SNAP is a snapshot file name or its number from `list` (1 = newest).
Snapshots live in <workspace>/history (or --dir).
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import workspace  # noqa: E402


def hist_dir(arg):
    if arg:
        return Path(arg)
    ws = workspace()
    if not ws:
        sys.exit("workspace not set: pass --dir or run workspace.py init")
    return ws / "history"


def snaps(h: Path):
    return sorted(h.glob("*.tex"), reverse=True)


def pick(h: Path, ref: str | None) -> Path:
    all_ = snaps(h)
    if not all_:
        sys.exit("no snapshots yet")
    if ref is None:
        return all_[0]
    if ref.isdigit():
        return all_[int(ref) - 1]
    p = h / ref
    return p if p.exists() else sys.exit(f"no snapshot {ref}")


def save(h: Path, tex: Path, note: str | None) -> Path:
    h.mkdir(parents=True, exist_ok=True)
    tag = re.sub(r"[^A-Za-z0-9]+", "-", note or "edit").strip("-")[:40]
    dst = h / f"{datetime.now():%Y%m%d-%H%M%S}_{tag}.tex"
    shutil.copy(tex, dst)
    print(f"saved {dst.name}")
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("save"); s.add_argument("tex"); s.add_argument("--note")
    sub.add_parser("list")
    d = sub.add_parser("diff"); d.add_argument("snap", nargs="?"); d.add_argument("--against")
    r = sub.add_parser("restore"); r.add_argument("snap"); r.add_argument("tex")
    a = ap.parse_args()
    h = hist_dir(a.dir)
    if a.cmd == "save":
        save(h, Path(a.tex), a.note)
    elif a.cmd == "list":
        for n, p in enumerate(snaps(h), 1):
            print(f"{n:>3}. {p.name}")
    elif a.cmd == "diff":
        old = pick(h, a.snap)
        cur = Path(a.against) if a.against else ((workspace() or Path(".")) / "resume.tex")
        diff = difflib.unified_diff(old.read_text(encoding="utf-8").splitlines(),
                                    cur.read_text(encoding="utf-8").splitlines(),
                                    fromfile=old.name, tofile=cur.name, lineterm="", n=0)
        print("\n".join(diff) or "no differences")
    else:
        src = pick(h, a.snap)
        tex = Path(a.tex)
        save(h, tex, "before-restore")
        shutil.copy(src, tex)
        print(f"restored {src.name} -> {tex}")


if __name__ == "__main__":
    main()
