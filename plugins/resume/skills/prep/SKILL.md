---
name: prep
description: Build an interview prep sheet from the resume - likely questions and talking points for every claim, deeper probes for numbers, and a study checklist for conceptual skills.
argument-hint: "[role or company] [JD]"
disable-model-invocation: true
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0.

For: $ARGUMENTS (if empty: a general sheet).

Write `<workspace>/jobs/<Company or general>/interview-prep.md`:
- Every bullet and project: the 2-minute story (situation, what the user did, how, result) from `ledger.md`; 3 likely questions (how, why this way, what went wrong, how it was measured); facts the user should recall before the interview.
- Every Skills term with no bullet behind it, and every conceptual item in the profile (for example Jenkins): what interviewers probe, as a short study checklist.
- With a JD: its must-have terms the user is weakest on.

Do not edit the resume.
