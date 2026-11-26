---
name: resume
description: "Use whenever the user wants to build, update, tailor, shorten, score, review or check a resume or CV, even if they do not say 'skill': sharing a resume (PDF, .tex, pasted text), pasting a job description (JD) or a Naukri/LinkedIn job link, 'optimize/tailor for this role', 'remove X', 'add Y', 'make it 1 page', 'is my resume ATS friendly', 'ATS score', 'make it 100', 'make my resume stronger', interview prep on resume claims, or sharing profile links. Edits the CONTENT of the user's LaTeX resume (never its look), keeps it strictly 1 page, verifies it with a local multi-engine ATS audit and the ResumeNext ATS tool, and delivers .tex plus PDF. Works on Windows, Linux, macOS (Claude Code) and the claude.ai sandbox; checks and installs its tools only after the user agrees. Resume only: NOT cover letters, LinkedIn profiles or portfolio sites."
---

# Resume Builder v3

v3 (2026-11-26): cross-platform tooling with a consent-first installer, a workspace outside the plugin, edit history, three-engine ATS parse audit with per-ATS checks, automatic short-line detection, JD term extraction, strength playbook, achievement mining, interview claim prep, and slash commands. Rules from v2 (template untouched, 1 page, Summary, one body size, honesty) are unchanged.

## Rule zero: the template is the user's design

The user hand-curated the look. **Never change** fonts, paper size, margins, heading layout, section styling, bullet glyphs, spacing commands or macros. The user's `.tex` IS the template; edit its content in place. `templates/resume.tex` is that template with content stripped, for a fresh build only.

Allowed template edits are exactly these two invisible kinds, proven with `resumectl diff before.tex after.tex` (must print `IDENTICAL`):
1. `\input{glyphtounicode}` + `\pdfgentounicode=1`
2. `pdftitle` / `pdfauthor` inside the existing `hyperref` options

The file must keep compiling with plain **pdfLaTeX** so the user can edit it on Overleaf.

### House rules (set by the user; override "never change the look" only here)
1. **Strictly 1 page** unless the user explicitly allows more (`--max-pages 2`). Fit by trimming words, never fonts, margins or spacing.
2. **One body font size** (`\small`): Summary, Skills rows, bullets, Projects, Certifications, role/date lines. Only the name (`\Large`) and section headings are larger.
3. **A Summary section is required** (first, 120 to 600 characters, about 3 lines) unless the user opts out (`--no-summary`).

## Tools: how to run them

| Where | How to call a script |
|---|---|
| Claude Code with this plugin | `resumectl <cmd> ...` (the plugin's `bin/` is on the Bash PATH). If not found: `bash "${CLAUDE_PLUGIN_ROOT}/bin/resumectl" <cmd> ...` |
| claude.ai sandbox or a bare copy of this skill | `python3 scripts/<script>.py ...` from this skill's folder (Windows: `python` or `py -3`) |

| Command | Script | Purpose |
|---|---|---|
| `doctor [--install]` | `env_check.py` | What is installed, the exact install plan for this OS, and (only with consent) running it |
| `check <tex> [opts]` | `resume_check.py` | Compile + audit: page count, fonts, 3 text extractors, contact, sections, Summary, dates, per-ATS rules, tool spellings, short last lines, page fill, links, bullet lint, JD coverage. `--pdf file.pdf` audits any PDF. `--text-out` writes the plain text for the ATS tool |
| `diff <a> <b>` | `pixel_diff.py` | Proves a change did not move a pixel |
| `jd <jd.txt> [--resume txt] [--out kw.txt]` | `jd_terms.py` | Ranked JD terms (must / normal / nice), which the resume lacks, hard requirements (years, degree, location, work type) |
| `snap save/list/diff/restore` | `snap.py` | History: snapshot before every edit; undo |
| `ws show/init/deliver` | `workspace.py` | The user's files and delivery to `out/` |

Platform details, install commands and troubleshooting: `references/setup.md`.

## Step 0: Start of every resume task

1. **Workspace.** `resumectl ws show`. The workspace (outside the plugin, survives updates) holds `resume.tex` (master), `profile.md` (standing preferences), `ledger.md` (facts and bullet bank), `jobs/<Company>/`, `history/`, `out/`. Not set: run Setup (below). In the claude.ai sandbox there is no workspace: use the uploaded files, `references/profiles/`, and write outputs to `/mnt/user-data/outputs/`.
2. **Load context:** `profile.md` then `ledger.md` (claude.ai: `references/profiles/<name>.md`). They override the defaults here.
3. **Environment.** `resumectl doctor`. If it says `NOT READY`, stop and do the consent flow:
   - Show the user, in plain words, what is missing, what will be installed (name, source, rough size), and whether it needs admin rights.
   - Ask once. Install only after an explicit yes (`resumectl doctor --install`, or `--only python,latex`). Never install silently, never "just this one package".
   - A step marked `[admin]` where sudo needs a password: give the user the exact command to run themselves (in Claude Code they can type `! <command>`).
   - If they decline: do content work only, say plainly that nothing was compiled or audited, and never claim a check passed.
   - Re-run `resumectl doctor` until READY.
   Quality is not negotiable: no build is delivered without `check` passing on a real compile.

## Setup (first run, or `/resume:setup`)
1. `resumectl doctor`, consent flow above.
2. Ask where the workspace should live (suggest `~/resume`), then `resumectl ws init --path <dir> --tex <current.tex> [--pdf <current.pdf>]`. Existing files are never overwritten.
3. Fill `profile.md` from what the user has said (look rules, tone, choices such as naming a client) and seed `ledger.md` from the resume: one row per claim with its proof level.
4. `resumectl check <workspace>/resume.tex` and report.

## Routing

| Request | Do | Command |
|---|---|---|
| "Is it ATS friendly?" / audit | Step 5 report only; no edits | `/resume:check` |
| Small edit ("add X", "remove Y", "update the project line") | Steps 4 (only what is touched), 5 | `/resume:update` |
| JD or job link | Steps 1, 3, 6, 4, 5, 5b, 7 into `jobs/<Company>/` | `/resume:tailor` |
| ATS score, "make it 100" | Steps 5, 5b loop | `/resume:ats` |
| "Make it stronger", critique | Strength review (`references/strength-playbook.md`), no edits until approved | `/resume:review` |
| Missing numbers, thin bullets | Achievement interview into the ledger | `/resume:mine` |
| Interview coming up | Claim-defense sheet | `/resume:prep` |
| Undo, compare versions | `snap list/diff/restore` | `/resume:history` |
| No `.tex` yet | Start from `templates/resume.tex`, fill from the ledger | `/resume:setup` |

## Principles
1. **Facts come from the ledger.** Every claim traces to the user's words, their resume or their saved notes. No invented numbers, tools, certifications, URLs or experience.
2. **Measure, do not guess.** `check` after every change, then look at the PNG it prints.
3. **Snapshot before every edit:** `resumectl snap save <tex> --note "<what>"`.
4. **Ask once, only for gaps,** in one grouped message.
5. **Show anything new.** Content taken from notes or the ledger rather than the current resume is listed for approval.
6. **Deliver `.tex` and `.pdf`** named `First_Last_Resume[_Company]` (`resumectl ws deliver [--company X]`).
7. **Push the ATS score as high as honesty allows.** A score is never a reason to invent a claim.

## Step 1: Fact ledger
`ledger.md` columns: fact | source | proof level | status. Proof levels (content-rules section 3): production, POC, conceptual (studied, can discuss in an interview; Skills only, needs a prep entry), learning. Mark gaps `ASK`. Typical gaps: metrics, dates, certification status, claims that conflict with what the user said elsewhere. Surface conflicts as questions; never silently delete a claim. Keep the **bullet bank**: alternative phrasings and spare bullets per role, so tailoring can swap bullets without new facts.

## Step 2: Intake (gaps only)
Max 3 questions, 2 to 4 options each, for choices; open facts in plain text. Never ask about look, order, paper or fonts: the user's file decides.

## Step 3: Keyword research (JD mode)
1. Save the JD verbatim to `jobs/<Company>/jd.txt` (fetch a job link if possible; if blocked, ask the user to paste it).
2. `resumectl check resume.tex --text-out jobs/<Company>/resume.txt`, then `resumectl jd jobs/<Company>/jd.txt --resume jobs/<Company>/resume.txt --out jobs/<Company>/keywords.txt`.
3. Split the absent terms into: true and unconfirmed (ask once), and not true (drop). Hard requirements (years, degree, location, work type) are reported, never "fixed" by wording.
4. Edit `keywords.txt` down to confirmed terms only, then measure coverage with `check --keywords`.
5. No JD: read 3 to 5 current postings for the target title and city instead of keyword blogs.

## Step 4: Content pass
Read `references/content-rules.md` and `references/strength-playbook.md`, then audit:

| Audit | Typical finding |
|---|---|
| Top third (recruiter scan) | Best result not in the Summary or first bullet |
| Skills vs bullets | Terms proven in bullets but absent from Skills; JD terms only in Skills (prove them in a bullet where true) |
| Skills hygiene | Mislabeled rows, catch-all row, missing literal terms (`Git`, `Azure Pipelines`, `CI/CD`) |
| Bullet craft | No outcome or scale, 3+ lines, weak or repeated opener, 1-2 word last line |
| Projects | No link, no user/adoption signal, stack list longer than the point |
| Summary | Missing, outside 120-600 chars, adjectives instead of facts |
| Consistency | Date style, tense, trailing periods, tool spellings (checker flags them) |
| Claim risk | Claim stronger than its proof level; conceptual items need a prep entry |
| Certifications | Unearned or expired entries (respect the profile: some users renew on time) |
| Confidential names | Client or internal names (keep if the profile says the user chose them) |

Page space is fixed: to add, cut the weakest content. Never shrink spacing or fonts.

## Step 5: Verify (mandatory after every change)
```
resumectl check <tex> --outdir <dir> [--keywords kw.txt] [--avoid "A,B"] [--max-pages 1] [--json r.json] [--text-out r.txt] [--final]
```
Then **view the PNG** it prints. Exit 1 = do not deliver.

| Check | Fix |
|---|---|
| compile | read `r.log` in the build dir; missing package = environment (`doctor`), not the template |
| page count | cut words |
| fonts: Type 3 / not embedded | environment (cm-super); never touch the user's fonts |
| parse across engines | all extractors must see the same sections and the email; fix content order, not looks |
| contact, headings, summary | standard names, Summary 120-600 chars |
| ATS: symbols / columns / footer band / images | remove emoji and icons; keep single column; nothing in the bottom band |
| tool spellings | use the canonical form it suggests |
| short last lines | trim 1 to 3 words from that bullet |
| page fill > 8% gap | ask the user (real content from the ledger, or leave it). Never pad |
| links | every link's URL also visible as text; https |
| bullet lint | strong verb openers, no 3x repeated opener, no buzzwords |

Visual check the script cannot do: nothing overlapping, no heading stranded at the bottom.

## Step 5b: ATS tool loop (JD mode, or when a score is asked for)
1. Text: `resumectl check <tex> --text-out <file>` (the real extracted text, not a hand-typed version).
2. Load the ResumeNext connector (`analyze_resume`). If the "Job Match & Resume Keyword Scanner - ResumeNext" connector is also connected, run it too for matched/missing keywords. If neither is connected, say so and rely on `check` + `jd`.
3. Call with `resume_text`, the verbatim JD as `job_description`, `target_role`, and `target_company` when known. The text leaves the machine: if the profile does not record the user's consent to this tool, ask first.
4. Fix what can be fixed honestly, recompile (still 1 page, one body size), re-run. Repeat until 100 or only fact-blocked gaps remain (3 to 6 rounds).
5. Known tool behaviour (heuristics, `references/ats-research.md`): Summary 120-600 chars; literal JD terms; JD cities in the Summary only if the user confirms relocation; LinkedIn URL; "full-time" if the JD says so; accepted openers (Reduced, Built, Led, Deployed, Automated, Developed, Improved, Created, Optimized, Designed). It may misread a role/title line as a bullet (seen 2026-11-26): not fixable without changing the look; report it.
6. **Honesty gate.** Unconfirmed facts never enter a version meant to be sent. If the user wants to see the ceiling, write `First_Last_Resume_TEST_ONLY.tex` with every unconfirmed line marked `% TEST-ONLY`, and say it must not be sent.
7. Report score before and after, what moved it, what is left and why.

## Step 6: JD optimization
Before editing, show:
```
## JD match
Missing (confirmed true): [...]   Missing (needs your answer): [...]   Not true: [...]
Hard requirements: [...]
Bullets to reorder / swap from the bullet bank / reword (honestly): [...]
Skills: add / remove / reorder
Coverage: X% -> Y%   ATS score: A -> B (expected)
```
Reorder before rewriting. Mirror JD vocabulary only where true. Work on a copy: `jobs/<Company>/resume.tex`.

## Step 7: Delivery checklist
- [ ] `check --final` exits 0 (1 page, Summary, one body size, engines agree) and the PNG was viewed
- [ ] ATS loop run when a JD exists; score and remaining gaps reported; nothing added only for score
- [ ] `diff` IDENTICAL when only invisible lines changed
- [ ] Snapshot saved; `ws deliver` wrote `.tex` and `.pdf` to `out/` (claude.ai: `/mnt/user-data/outputs/`)
- [ ] Ledger updated with any new facts the user confirmed
- [ ] Reply lists: what changed, what came from notes, claims to confirm, open questions, file paths

## LaTeX notes
- Escape `& % $ # _`. `--` for an en dash. No `\\` inside `\resumeItem{}`. `~` keeps a two-word term on one line (`GitHub~Actions`).
- Never edit the template to dodge a missing font or package: fix the environment.

## Maintenance
Re-verify before relying on them: certification names and validity, tool names, `references/ats-research.md`. Record measured ATS-tool behaviour there with a date.
