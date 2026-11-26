---
name: check
description: Audit the resume (or any resume PDF) the way an ATS reads it - compile, page count, fonts, three text extractors, sections, contact, per-ATS rules, spellings, short lines, page fill, links, bullet lint. Report only, no edits.
argument-hint: "[path to .tex or .pdf]"
disable-model-invocation: true
allowed-tools: Bash(resumectl *)
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0.

Target: $ARGUMENTS (if empty: `<workspace>/resume.tex`; a `.pdf` path is audited with `--pdf`).

Run `resumectl check ...`, view the PNG, then explain each FAIL and WARN in one line with the fix the skill would make. Do not edit anything.
