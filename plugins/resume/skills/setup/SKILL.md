---
name: setup
description: Set up the resume skill on this machine - check and (with consent) install Python packages and LaTeX, create the resume workspace, import the current resume, seed the profile and fact ledger.
argument-hint: "[path to current resume .tex or .pdf] [workspace dir]"
disable-model-invocation: true
allowed-tools: Bash(resumectl *)
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0.

Task: the Setup section of the core skill.
1. `resumectl doctor`. Explain what is missing in plain words (what, from where, roughly how big, admin or not) and ask once before `resumectl doctor --install`. Never install without a yes. Re-run until READY or the user declines.
2. Workspace: use the directory in the arguments, else ask (suggest `~/resume`). `resumectl ws init --path <dir> --tex <file>`.
3. If only a PDF was given, rebuild its content into the bundled template and show it for approval; never claim it matches the original look.
4. Fill `profile.md` and seed `ledger.md` from the resume and what the user has said.
5. `resumectl check <workspace>/resume.tex`, view the PNG, report.

Arguments: $ARGUMENTS
