"""Shared helpers: platform detection, finding pdflatex, compiling, workspace paths.

Pure standard library so env_check.py can import it before any dependency is installed.
"""
from __future__ import annotations

import glob
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace", **kw)


# --------------------------------------------------------------- locations
def data_dir() -> Path:
    """Per-user tool data (venv). Never inside the plugin, which is replaced on update."""
    if IS_WIN:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "resume-skill"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "resume-skill"


def config_path() -> Path:
    return Path.home() / ".config" / "resume-skill" / "config.json"


def load_config() -> dict:
    try:
        return json.loads(config_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_config(cfg: dict) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def workspace() -> Path | None:
    """RESUME_HOME, then the saved config, else None (not set up yet)."""
    env = os.environ.get("RESUME_HOME")
    if env:
        return Path(env).expanduser()
    ws = load_config().get("workspace")
    return Path(ws).expanduser() if ws else None


def is_sandbox() -> bool:
    """claude.ai code-execution sandbox (Linux, /mnt/user-data present)."""
    return Path("/mnt/user-data").exists()


# ------------------------------------------------------------------ LaTeX
def find_pdflatex() -> str | None:
    p = shutil.which("pdflatex")
    if p:
        return p
    cands: list[str] = []
    if IS_WIN:
        la = os.environ.get("LOCALAPPDATA", "")
        pf = [os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", "")]
        cands += [os.path.join(la, "Programs", "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe")]
        cands += [os.path.join(x, "MiKTeX", "miktex", "bin", "x64", "pdflatex.exe") for x in pf if x]
        scoop = os.environ.get("SCOOP", str(Path.home() / "scoop"))
        cands += [os.path.join(scoop, "apps", app, "current", "texmfs", "install", "miktex", "bin", "x64", "pdflatex.exe")
                  for app in ("miktex", "latex")]  # scoop portable MiKTeX ('latex' is the old name)
        cands += sorted(glob.glob(r"C:\texlive\*\bin\windows\pdflatex.exe"), reverse=True)
        cands += sorted(glob.glob(r"C:\texlive\*\bin\win32\pdflatex.exe"), reverse=True)
    elif IS_MAC:
        cands += ["/Library/TeX/texbin/pdflatex", "/opt/homebrew/bin/pdflatex", "/usr/local/bin/pdflatex"]
    else:
        cands += sorted(glob.glob("/usr/local/texlive/*/bin/*/pdflatex"), reverse=True)
    for c in cands:
        if c and os.path.isfile(c):
            return c
    return None


def tex_distribution(pdflatex: str) -> str:
    v = run([pdflatex, "--version"]).stdout
    if "MiKTeX" in v:
        return "MiKTeX"
    if "TeX Live" in v:
        return "TeX Live"
    return "unknown"


def compile_tex(tex: Path, outdir: Path, passes: int = 2):
    """Compile tex as outdir/r.tex. Returns (pdf_path | None, log_text, error_lines)."""
    pdflatex = find_pdflatex()
    if not pdflatex:
        return None, "", ["pdflatex not found: run the setup check (resumectl doctor)"]
    outdir.mkdir(parents=True, exist_ok=True)
    work = outdir / "r.tex"
    shutil.copy(tex, work)
    for stale in ("r.pdf", "r.aux", "r.out"):
        (outdir / stale).unlink(missing_ok=True)
    cmd = [pdflatex, "-interaction=nonstopmode", "-halt-on-error"]
    if tex_distribution(pdflatex) == "MiKTeX":
        cmd.append("-enable-installer")  # fetch missing packages instead of prompting
    cmd.append(work.name)
    log = ""
    for _ in range(passes):  # 2 passes so hyperref outlines settle
        p = run(cmd, cwd=outdir)
        logf = outdir / "r.log"
        log = logf.read_text(errors="replace") if logf.exists() else p.stdout
        if p.returncode != 0:
            errs = [l for l in log.splitlines() if l.startswith("!")][:3]
            return None, log, errs or ["pdflatex failed (see r.log)"]
    pdf = outdir / "r.pdf"
    return (pdf if pdf.exists() else None), log, ([] if pdf.exists() else ["no PDF produced"])


def os_label() -> str:
    if IS_WIN:
        return f"Windows {platform.release()}"
    if IS_MAC:
        return f"macOS {platform.mac_ver()[0]}"
    name = ""
    try:
        txt = Path("/etc/os-release").read_text()
        m = re.search(r'^PRETTY_NAME="?([^"\n]+)', txt, re.M)
        name = m.group(1) if m else ""
    except OSError:
        pass
    return f"Linux {name}".strip()


def linux_family() -> str:
    try:
        txt = Path("/etc/os-release").read_text().lower()
    except OSError:
        return "unknown"
    ids = " ".join(re.findall(r"^(?:id|id_like)=\"?([^\"\n]+)", txt, re.M))
    for fam, keys in (("debian", ("debian", "ubuntu")), ("fedora", ("fedora", "rhel", "centos")),
                      ("arch", ("arch",)), ("suse", ("suse",))):
        if any(k in ids for k in keys):
            return fam
    return "unknown"
