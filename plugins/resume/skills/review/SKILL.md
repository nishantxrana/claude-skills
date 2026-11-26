---
name: review
description: Recruiter-style strength review of the resume - 7-second scan, strength scorecard, and the three highest-impact improvements, using only true facts. Proposes changes; edits only after approval.
argument-hint: "[target role or JD]"
disable-model-invocation: true
allowed-tools: Bash(resumectl *)
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0. Then read `${CLAUDE_PLUGIN_ROOT}/skills/resume/references/strength-playbook.md`.

Target role or JD (optional): $ARGUMENTS

1. 7-second scan: what a recruiter takes away from the top third.
2. Scorecard (playbook section 13): each dimension 1-5 with one line of evidence.
3. Top 3 changes by expected gain, each as before/after text built only from the resume and `ledger.md`. Where a number would help, ask for it or suggest `/resume:mine`.
4. Claim-risk list (content-rules section 10).

Edit only after the user picks changes, then follow the `/resume:update` steps.
