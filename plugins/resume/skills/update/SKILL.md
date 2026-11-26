---
name: update
description: Make a targeted change to the resume (add, remove, reword or reorder a line or section), keep it one page, recompile and re-check.
argument-hint: "<what to change>"
disable-model-invocation: true
allowed-tools: Bash(resumectl *)
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0.

Change requested: $ARGUMENTS

1. `resumectl snap save <workspace>/resume.tex --note "<short change name>"`.
2. Use facts from the conversation and `ledger.md` only. New facts go into the ledger with source "user, <today>". Anything unclear: one grouped question.
3. Edit content only (Rule zero). If the page overflows, trim the weakest words or bullet and say what was cut.
4. `resumectl check <workspace>/resume.tex --outdir <workspace>/out/.check`, view the PNG, fix any WARN the change caused.
5. Show before/after of the changed lines and the check summary. Then `resumectl ws deliver` for the PDF.
