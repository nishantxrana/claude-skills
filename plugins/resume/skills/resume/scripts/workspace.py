#!/usr/bin/env python3
"""workspace.py - where the user's resume files live (outside the plugin, so updates never touch them).

  python workspace.py show                       # JSON: path and which files exist
  python workspace.py init --path ~/resume [--tex current.tex] [--pdf current.pdf]
  python workspace.py deliver [--company Acme] [--name "First Last"]   # copy resume.tex + built PDF to out/

Layout:
  resume.tex     master resume (the template IS this file)
  profile.md     standing preferences (look rules, tone, choices like keeping a client name)
  ledger.md      fact ledger + bullet bank: every claim, its source and proof level
  jobs/          one folder per application: jd.txt, keywords.txt, notes
  history/       snapshots before every edit (snap.py)
  out/           delivered files: First_Last_Resume[_Company].tex/.pdf
Resolution order: $RESUME_HOME, then ~/.config/resume-skill/config.json, else not set.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import compile_tex, load_config, save_config, workspace  # noqa: E402

TEMPLATES = HERE.parent / "templates"


def show():
    ws = workspace()
    info = {"workspace": str(ws) if ws else None, "exists": bool(ws and ws.exists())}
    if ws and ws.exists():
        for f in ("resume.tex", "profile.md", "ledger.md"):
            info[f] = (ws / f).exists()
        info["jobs"] = sorted(p.name for p in (ws / "jobs").glob("*") if p.is_dir()) if (ws / "jobs").exists() else []
        info["snapshots"] = len(list((ws / "history").glob("*.tex"))) if (ws / "history").exists() else 0
        info["delivered"] = sorted(p.name for p in (ws / "out").glob("*.pdf")) if (ws / "out").exists() else []
    print(json.dumps(info, indent=2))


def init(path: str, tex: str | None, pdf: str | None):
    ws = Path(path).expanduser().resolve()
    for d in ("jobs", "history", "out"):
        (ws / d).mkdir(parents=True, exist_ok=True)
    if tex:
        dst = ws / "resume.tex"
        if dst.exists():
            print(f"kept existing {dst} (not overwritten)")
        else:
            shutil.copy(tex, dst)
            print(f"copied {tex} -> {dst}")
    elif not (ws / "resume.tex").exists():
        shutil.copy(TEMPLATES / "resume.tex", ws / "resume.tex")
        print("started resume.tex from the bundled template (placeholders to fill)")
    if pdf:
        shutil.copy(pdf, ws / "out" / Path(pdf).name)
    for name in ("profile.md", "ledger.md"):
        if not (ws / name).exists():
            shutil.copy(TEMPLATES / name, ws / name)
            print(f"created {ws / name}")
    cfg = load_config()
    cfg["workspace"] = str(ws)
    save_config(cfg)
    print(f"workspace set: {ws}")


def person_name(tex: Path) -> str:
    s = tex.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"pdfauthor=\{([^}]+)\}", s) or re.search(r"\\Large\s+([^}]+)\}", s)
    return m.group(1).strip() if m else "Resume"


def deliver(company: str | None, name: str | None):
    ws = workspace()
    if not ws:
        sys.exit("workspace not set: run init first")
    tex = ws / "resume.tex"
    if company:
        job_tex = ws / "jobs" / slug(company) / "resume.tex"
        if job_tex.exists():
            tex = job_tex
    base = "_".join((name or person_name(tex)).split()) + "_Resume" + (f"_{slug(company)}" if company else "")
    build = ws / "out" / ".build"
    pdf, _, errs = compile_tex(tex, build)
    if not pdf:
        sys.exit("compile failed: " + " | ".join(errs))
    shutil.copy(tex, ws / "out" / f"{base}.tex")
    shutil.copy(pdf, ws / "out" / f"{base}.pdf")
    print(json.dumps({"tex": str(ws / "out" / f"{base}.tex"), "pdf": str(ws / "out" / f"{base}.pdf")}, indent=2))


def slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", s.title())


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    i = sub.add_parser("init")
    i.add_argument("--path", required=True)
    i.add_argument("--tex")
    i.add_argument("--pdf")
    d = sub.add_parser("deliver")
    d.add_argument("--company")
    d.add_argument("--name")
    a = ap.parse_args()
    if a.cmd == "show":
        show()
    elif a.cmd == "init":
        init(a.path, a.tex, a.pdf)
    else:
        deliver(a.company, a.name)


if __name__ == "__main__":
    main()
