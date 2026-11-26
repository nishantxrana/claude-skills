# Setup and platforms

The skill needs four things. `resumectl doctor` checks all of them and prints the install plan for the machine it runs on. Nothing is installed until the user says yes.

| Part | Why | Required |
|---|---|---|
| Python 3.8+ | runs every script | yes |
| PyMuPDF, pypdfium2, Pillow | read, render and audit the PDF (two independent text engines) | yes |
| pdfLaTeX + the template's packages (titlesec, enumitem, preprint/fullpage, marvosym, fancyhdr, hyperref, cm-super fonts) | compile the resume exactly like Overleaf | yes |
| poppler (`pdftotext`) | a third text extractor | optional |

No `qpdf` or `pdfplumber` any more (v2 needed them).

## Per platform

### Windows (Claude Code, Git Bash)
- **Python**: the `python` on PATH may be the Microsoft Store stub that only prints "Python was not found". `resumectl` skips it and finds `%LOCALAPPDATA%\Programs\Python\Python3*\python.exe` or `py -3`. If none: `winget install -e --id Python.Python.3.13` or `scoop install python`.
- **LaTeX**: MiKTeX. With scoop: `scoop install miktex` (portable, no admin; older name `latex`). Otherwise `winget install --id MiKTeX.MiKTeX -e`. Then `initexmf --set-config-value=[MPM]AutoInstall=1` so missing packages download on first compile (the checker also passes `-enable-installer`). The first compile can take a minute while packages download.
- `pdflatex` need not be on PATH: the scripts look in the usual MiKTeX and TeX Live folders.
- Python packages: `python -m pip install --user pymupdf pypdfium2 pillow`.
- Optional: `scoop install poppler`.

### Linux
- Debian/Ubuntu: `sudo apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended cm-super lmodern` (about 400 MB).
- Fedora: `sudo dnf install -y texlive-scheme-medium texlive-cm-super`. Arch: `sudo pacman -S --needed texlive-basic texlive-latex texlive-latexrecommended texlive-latexextra texlive-fontsrecommended`.
- Python packages: `pip install --user ...`. On an "externally managed" Python (PEP 668, recent Debian/Ubuntu), `doctor --install` creates a private venv at `~/.local/share/resume-skill/venv`; `resumectl` uses it automatically.
- sudo with a password cannot be typed by Claude. The user runs the printed command (in Claude Code: `! sudo apt-get ...`).

### macOS
- `brew install --cask basictex`, then `sudo tlmgr install titlesec enumitem preprint marvosym fancyhdr cm-super lm`. Full MacTeX also works.

### claude.ai sandbox
- Linux, usually root, so apt-get works without a password: `apt-get install -y texlive-latex-extra texlive-fonts-recommended cm-super lmodern` and `pip install pymupdf pypdfium2 pillow`.
- No workspace persists between chats: read `references/profiles/`, write deliverables to `/mnt/user-data/outputs/`.
- Run scripts as `python3 scripts/<name>.py` from the skill folder.

## Workspace
`resumectl ws init --path <dir> --tex <resume.tex>` creates it and records it in `~/.config/resume-skill/config.json`. `RESUME_HOME` overrides. Keep personal data (profile, ledger, resumes) there, not inside the plugin: plugin updates replace the plugin folder.

## Installing the plugin in Claude Code
From the folder that contains `.claude-plugin/marketplace.json`:
```
claude plugin marketplace add <path-to-resume-v3>
claude plugin install resume@nishant-skills
```
or inside a session: `/plugin marketplace add <path>` then `/plugin install resume@nishant-skills`, and `/reload-plugins` after edits. Commands appear as `/resume:setup`, `/resume:tailor`, and so on.

## Uploading to claude.ai
Upload the zip of `plugins/resume/skills/resume` (the core skill only). Its frontmatter uses only portable fields; the slash-command skills are Claude Code only.

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `File 'titlesec.sty' not found` | package missing | MiKTeX: AutoInstall on, re-run; TeX Live: install `texlive-latex-extra` |
| Type 3 fonts reported | cm-super missing | install cm-super; never change the template's fonts |
| `(cid:NN)` in text | missing Unicode maps | keep `\input{glyphtounicode}` and `\pdfgentounicode=1` |
| Python "was not found" on Windows | Store alias | use `resumectl` (skips it) or turn off the alias in Settings > Apps > App execution aliases |
| first MiKTeX compile slow | packages downloading | wait; later compiles are fast |
