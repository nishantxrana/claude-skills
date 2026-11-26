---
name: tailor
description: Tailor the resume to a job description - extract JD terms, compare, propose honest changes, build a company-specific one-page version, and run the ATS score loop.
argument-hint: "<JD text, file path or job URL> [company]"
disable-model-invocation: true
allowed-tools: Bash(resumectl *)
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0.

Job: $ARGUMENTS

Run JD mode (core Steps 1, 3, 6, 4, 5, 5b, 7):
- Company folder `<workspace>/jobs/<Company>/` with `jd.txt` (verbatim), `keywords.txt`, `resume.tex` (copy of the master), notes.
- Show the "JD match" block and get approval before editing. Ask once about absent terms that might be true.
- Hard requirements (years, degree, location, work type) are reported, never worded around.
- Deliver with `resumectl ws deliver --company <Company>`. Report keyword coverage and ATS score before and after.
