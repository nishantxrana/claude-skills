---
name: mine
description: Achievement interview - ask targeted questions per bullet to uncover real numbers, scale and ownership, record answers in the fact ledger, and propose stronger bullets.
argument-hint: "[bullet, role or project to focus on]"
disable-model-invocation: true
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0. Then read `${CLAUDE_PLUGIN_ROOT}/skills/resume/references/strength-playbook.md` section 3.

Focus: $ARGUMENTS (if empty: bullets without a number or scale, weakest first).

- One bullet at a time, at most 3 questions per round, multiple choice where possible. Accept "don't know" and move on.
- Record every answer in `ledger.md` (source "user, <today>", proof level).
- After each bullet, show the stronger version and whether it still fits its line budget. Apply only on approval, via the `/resume:update` steps.
