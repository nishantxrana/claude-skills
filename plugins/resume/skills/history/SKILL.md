---
name: history
description: Resume edit history - list snapshots, show what changed, or restore an earlier version.
argument-hint: "[list | diff N | restore N]"
disable-model-invocation: true
allowed-tools: Bash(resumectl *)
---
Follow the core resume skill: read `${CLAUDE_PLUGIN_ROOT}/skills/resume/SKILL.md` first if it is not already loaded in this session, including its Step 0.

Request: $ARGUMENTS (if empty: list)

Run `resumectl snap list`, `resumectl snap diff N`, or `resumectl snap restore N <workspace>/resume.tex`. Explain the diff in plain words. A restore saves the current file first; recompile and check after restoring.
