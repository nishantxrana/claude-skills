---
name: ats
description: Score the resume for applicant tracking systems (local multi-engine audit plus the ResumeNext ATS tool, optionally against a JD) and raise the score as far as honesty allows.
argument-hint: "[JD text or file] [report-only]"
disable-model-invocation: true
allowed-tools: Bash(resumectl *)
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0.

Input: $ARGUMENTS

Run core Steps 5 and 5b on the master resume (or a company copy if a company is named).
- "report-only" in the input: score and explain, change nothing.
- Otherwise loop: fix honestly, snapshot, recompile, re-score (3 to 6 rounds). Stop at 100 or when only fact-blocked gaps remain; list those as one grouped question.
- Report the score before and after by category, what moved it, and what remains and why.
