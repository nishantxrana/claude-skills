#!/usr/bin/env python3
"""env_check.py - check (and, only when asked, install) everything the resume skill needs.

  python env_check.py                 # report + install plan, changes nothing
  python env_check.py --json out.json
  python env_check.py --install       # run the plan (ONLY after the user approved it)
  python env_check.py --install --only python,latex

Required: pdflatex with the template's packages (TeX Live or MiKTeX), Python 3.8+,
PyMuPDF, pypdfium2, Pillow. Optional: poppler (a third text extractor).
Exit 0 = all required parts present, 1 = something required is missing.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (IS_MAC, IS_WIN, compile_tex, data_dir, find_pdflatex, is_sandbox,  # noqa: E402
                    linux_family, os_label, run, tex_distribution, workspace)

PY_PKGS = {"pymupdf": "pymupdf", "pypdfium2": "pypdfium2", "PIL": "pillow"}
PROBE_TEX = r"""\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[pdftex,colorlinks=true,urlcolor=black]{hyperref}
\usepackage{fancyhdr}
\input{glyphtounicode}
\pdfgentounicode=1
\begin{document}
\section*{\scshape Probe}
\begin{itemize}\item\small{fi fl -- \textbf{bold} \textit{italic} $\circ$ \href{https://example.com}{link}}\end{itemize}
\end{document}
"""

rows: list[tuple[str, str, str]] = []
plan: list[dict] = []


def add(status, item, detail=""):
    rows.append((status, item, detail))


def step(part, desc, cmd, needs_admin=False, manual=False):
    plan.append(dict(part=part, desc=desc, cmd=cmd, needs_admin=needs_admin, manual=manual))


def have(cmd):
    return shutil.which(cmd) is not None


def can_sudo():
    if IS_WIN:
        return False
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        return True
    return have("sudo") and run(["sudo", "-n", "true"]).returncode == 0


def sudo_prefix():
    return [] if (hasattr(os, "geteuid") and os.geteuid() == 0) else ["sudo"]


# ------------------------------------------------------------------ checks
def check_python():
    v = sys.version_info
    ok = v >= (3, 8)
    add("PASS" if ok else "FAIL", "python", f"{sys.version.split()[0]} at {sys.executable}")
    missing = []
    for mod, pkg in PY_PKGS.items():
        try:
            m = importlib.import_module(mod)
            add("PASS", f"python: {pkg}", getattr(m, "__version__", getattr(m, "VersionBind", "")) or "installed")
        except Exception:
            missing.append(pkg)
            add("FAIL", f"python: {pkg}", "missing")
    if missing:
        step("python", f"install Python packages: {', '.join(missing)}",
             [sys.executable, "-m", "pip", "install", "--user", *missing])
    return not missing


def latex_install_steps():
    if IS_WIN:
        if have("scoop"):
            step("latex", "install MiKTeX (portable, no admin) via scoop", ["scoop", "install", "miktex"])
        elif have("winget"):
            step("latex", "install MiKTeX via winget", ["winget", "install", "--id", "MiKTeX.MiKTeX", "-e",
                                                        "--accept-source-agreements", "--accept-package-agreements"])
        else:
            step("latex", "install MiKTeX from https://miktex.org/download (no package manager found)", [], manual=True)
        step("latex", "let MiKTeX fetch missing packages on first use",
             ["initexmf", "--set-config-value=[MPM]AutoInstall=1"])
        # vector fonts are not auto-fetched: without cm-super some glyphs become Type 3 bitmaps
        step("latex", "install the cm-super vector fonts", ["miktex", "packages", "install", "cm-super"])
        step("latex", "rebuild MiKTeX font maps", ["initexmf", "--mkmaps"])
    elif IS_MAC:
        step("latex", "install BasicTeX", ["brew", "install", "--cask", "basictex"])
        step("latex", "add the template's packages", ["sudo", "tlmgr", "install", "titlesec", "enumitem", "preprint",
                                                       "marvosym", "fancyhdr", "cm-super", "lm"], needs_admin=True)
    else:
        fam = linux_family()
        sp = sudo_prefix()
        if fam == "debian":
            step("latex", "install TeX Live (template packages + cm-super fonts)",
                 sp + ["apt-get", "install", "-y", "--no-install-recommends", "texlive-latex-base",
                       "texlive-latex-recommended", "texlive-latex-extra", "texlive-fonts-recommended",
                       "cm-super", "lmodern"], needs_admin=bool(sp))
        elif fam == "fedora":
            step("latex", "install TeX Live", sp + ["dnf", "install", "-y", "texlive-scheme-medium",
                                                    "texlive-cm-super"], needs_admin=bool(sp))
        elif fam == "arch":
            step("latex", "install TeX Live", sp + ["pacman", "-S", "--needed", "--noconfirm", "texlive-basic",
                                                    "texlive-latex", "texlive-latexrecommended", "texlive-latexextra",
                                                    "texlive-fontsrecommended"], needs_admin=bool(sp))
        else:
            step("latex", "install TeX Live with titlesec, enumitem, preprint (fullpage), marvosym, fancyhdr, "
                          "hyperref, cm-super, lmodern from your distro", [], manual=True)


def check_latex(deep: bool):
    pdflatex = find_pdflatex()
    if not pdflatex:
        add("FAIL", "pdflatex", "not found")
        latex_install_steps()
        return False
    dist = tex_distribution(pdflatex)
    add("PASS", "pdflatex", f"{dist}: {pdflatex}")
    if not deep:
        return True
    d = Path(tempfile.mkdtemp(prefix="resume_probe_"))
    src = d / "probe.tex"
    src.write_text(PROBE_TEX, encoding="utf-8")
    pdf, log, errs = compile_tex(src, d / "build", passes=1)
    if not pdf:
        missing = [l.split("`")[1].split("'")[0] for l in log.splitlines() if "File `" in l and "not found" in l]
        add("FAIL", "template packages", ("missing: " + ", ".join(missing)) if missing else " | ".join(errs))
        latex_install_steps()
        return False
    t3 = 0
    try:
        import pymupdf as fitz  # noqa: F401
    except ImportError:
        try:
            import fitz  # type: ignore
        except ImportError:
            fitz = None
    if fitz:
        doc = fitz.open(str(pdf))
        t3 = sum(1 for f in doc.get_page_fonts(0) if f[2] == "Type3")
    if t3:
        add("FAIL", "template packages", f"compiled, but {t3} Type 3 bitmap font(s): cm-super fonts missing")
        latex_install_steps()
        return False
    add("PASS", "template packages", "probe compiled with the template's preamble, vector fonts only")
    return True


def check_poppler():
    if have("pdftotext"):
        add("PASS", "poppler (optional)", "pdftotext found: used as a third extractor")
        return
    add("INFO", "poppler (optional)", "not found: checks use PyMuPDF and PDFium only (enough)")
    if IS_WIN:
        cmd = ["scoop", "install", "poppler"] if have("scoop") else ["winget", "install", "-e", "--id",
                                                                       "oschwartz10612.Poppler"]
    elif IS_MAC:
        cmd = ["brew", "install", "poppler"]
    else:
        fam = linux_family()
        pm = {"debian": ["apt-get", "install", "-y", "poppler-utils"], "fedora": ["dnf", "install", "-y", "poppler-utils"],
              "arch": ["pacman", "-S", "--needed", "--noconfirm", "poppler"]}.get(fam)
        cmd = (sudo_prefix() + pm) if pm else []
    step("poppler", "optional: install poppler (third text extractor)", cmd, needs_admin=bool(cmd and cmd[0] == "sudo"),
         manual=not cmd)


# ----------------------------------------------------------------- install
def pip_install(pkgs):
    """pip --user; on an externally-managed Python (PEP 668) fall back to a private venv."""
    p = run([sys.executable, "-m", "pip", "install", "--user", *pkgs])
    if p.returncode == 0:
        return True, "installed with pip --user"
    if "externally-managed" not in (p.stdout + p.stderr):
        if "No module named pip" in p.stderr:
            run([sys.executable, "-m", "ensurepip", "--user"])
            p = run([sys.executable, "-m", "pip", "install", "--user", *pkgs])
            if p.returncode == 0:
                return True, "installed with pip --user"
        return False, (p.stderr or p.stdout)[-400:]
    venv = data_dir() / "venv"
    r = run([sys.executable, "-m", "venv", str(venv)])
    if r.returncode != 0:
        return False, "could not create venv: " + r.stderr[-300:]
    vpy = venv / ("Scripts/python.exe" if IS_WIN else "bin/python")
    p = run([str(vpy), "-m", "pip", "install", *pkgs])
    return p.returncode == 0, f"installed into {venv} (resumectl uses it automatically)"


def do_install(only):
    for s in plan:
        if only and s["part"] not in only:
            continue
        print(f"\n>>> {s['desc']}")
        if s["manual"] or not s["cmd"]:
            print("    manual step: do this yourself, then re-run the check")
            continue
        if s["needs_admin"] and not can_sudo():
            print("    needs admin rights and sudo asks for a password. Run it yourself:")
            print("    " + " ".join(s["cmd"]))
            continue
        if s["part"] == "python":
            ok, msg = pip_install([a for a in s["cmd"][5:]])
            print(("    OK: " if ok else "    FAILED: ") + msg)
            continue
        cmd = list(s["cmd"])
        exe = shutil.which(cmd[0])
        if exe:
            cmd[0] = exe
        elif cmd[0] == "initexmf":
            pl = find_pdflatex()
            cand = Path(pl).with_name("initexmf.exe" if IS_WIN else "initexmf") if pl else None
            if cand and cand.exists():
                cmd[0] = str(cand)
        print("    $ " + " ".join(s["cmd"]))
        try:
            p = subprocess.run(cmd)
            print("    OK" if p.returncode == 0 else f"    FAILED (exit {p.returncode})")
        except FileNotFoundError:
            print(f"    FAILED: {cmd[0]} not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true", help="run the plan (only after the user approved it)")
    ap.add_argument("--only", help="comma list of parts to install: python,latex,poppler")
    ap.add_argument("--no-probe", action="store_true", help="skip the test compile")
    ap.add_argument("--json")
    a = ap.parse_args()

    add("INFO", "platform", os_label() + ("  (claude.ai sandbox)" if is_sandbox() else ""))
    ws = workspace()
    add("INFO" if ws else "WARN", "workspace", str(ws) if ws else "not set: run workspace.py init")
    py_ok = check_python()
    tex_ok = check_latex(deep=not a.no_probe)
    check_poppler()

    w = max(len(i) for _, i, _ in rows)
    print("\nResume skill environment\n" + "-" * 70)
    for s, i, d in rows:
        print(f"{s:<5} {i:<{w}}  {d}")
    print("-" * 70)
    required = [s for s in plan if s["part"] != "poppler"]
    if required or [s for s in plan if s["part"] == "poppler"]:
        print("Install plan (nothing has been changed):")
        for n, s in enumerate(plan, 1):
            tag = " [optional]" if s["part"] == "poppler" else ""
            tag += " [admin]" if s["needs_admin"] else ""
            tag += " [manual]" if s["manual"] else ""
            print(f"  {n}. {s['desc']}{tag}")
            if s["cmd"]:
                print("     " + " ".join(s["cmd"]))
    ready = py_ok and tex_ok
    print(f"RESULT: {'READY' if ready else 'NOT READY'}")
    if a.json:
        Path(a.json).write_text(json.dumps(dict(rows=rows, plan=plan, ready=ready), indent=2))
    if a.install:
        do_install(set(a.only.split(",")) if a.only else None)
        print("\nRe-run without --install to confirm.")
    sys.exit(0 if ready else 1)


if __name__ == "__main__":
    main()
