# claude-skills

Personal Claude Code plugin marketplace (`nishant-skills`). Private.

## Plugins

| Plugin | What it does | Commands |
|---|---|---|
| `resume` | One-page LaTeX resume builder: edits content only (never the look), local multi-engine ATS audit, ResumeNext score loop, JD tailoring, fact ledger, interview prep, edit history. Windows, Linux, macOS, claude.ai. | `/resume:setup`, `/resume:update`, `/resume:tailor`, `/resume:ats`, `/resume:check`, `/resume:review`, `/resume:mine`, `/resume:prep`, `/resume:history` |

## Install on a machine

Needs git access to this private repo (`gh auth login` or your git credentials).

```
claude plugin marketplace add nishantxrana/claude-skills
claude plugin install resume@nishant-skills
```

Then, in Claude Code, `/resume:setup` checks Python and LaTeX for that OS (installs only after you agree) and asks where your resume workspace lives.

## Update

After pushing a change (bump `version` in the plugin's `.claude-plugin/plugin.json`):

```
claude plugin marketplace update nishant-skills
claude plugin update resume@nishant-skills
```

Then `/reload-plugins` or start a new session.

## Add a plugin

1. `plugins/<name>/.claude-plugin/plugin.json` (`name`, `version`, `description`) and `plugins/<name>/skills/<skill>/SKILL.md`.
2. Add `{ "name": "<name>", "source": "./plugins/<name>", "description": "..." }` to `.claude-plugin/marketplace.json`.
3. `claude plugin validate .` then commit and push.

## claude.ai

claude.ai takes a single skill zip, not the plugin. Zip `plugins/resume/skills/resume` and upload it as a skill (slash commands are Claude Code only).

## Personal data

Resumes, ledger and profile live in the workspace on each machine (outside this repo). `plugins/resume/skills/resume/references/profiles/` holds a preferences fallback for claude.ai; keep this repo private or move that file out before making it public.
