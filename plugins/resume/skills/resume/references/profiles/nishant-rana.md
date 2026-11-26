# Profile: Nishant Rana (standing preferences)

Source of truth is the user's current resume `.tex` (hand-curated). In Claude Code the workspace copy of this file (`profile.md`) wins; this copy is the claude.ai fallback.

## Hard rule
- **Never change the template look**: fonts, letter paper, margins, two-row heading (name + site + LinkedIn left, Email/Mobile right), small-caps section style, bullets. Content and ATS only, plus the house rules (1 page, Summary, one body size).
- The `.tex` must keep compiling with pdfLaTeX on Overleaf (the user makes small edits there).

## Structure
- Order: Summary, Skills, Experience, Projects, Certifications, Education.
- Heading: name, site, LinkedIn, email, phone.
- Strictly one page. All body text `\small`.
- Output `.tex` and `.pdf`.

## Writing
- Past tense for finished work, present for ongoing.
- Keeps the client name (American Express) in the cost-saving bullet: deliberate, do not strip.
- Voice-to-text input: interpret intent over literal transcription artifacts.
- Bash preferred over PowerShell when one must be chosen.

## Decisions already made (2026-11-26)
- **Jenkins stays in Skills.** Proof level: conceptual. The user has used it and will prepare the theory for interviews; do not ask again. Add it to every `/resume:prep` sheet.
- **Certifications (AZ-204, AI-102):** the user renews them on time. List as earned; do not raise expiry questions.
- **ATS tool:** the user consents to sending the resume text to the ResumeNext tool and wants the score pushed as high as honesty allows. Unconfirmed claims only in a `_TEST_ONLY` file.
- LinkedIn URL is on the resume (closed).

## Open items
- Terraform: earlier notes called it POC-level; the resume lists it only in Skills (no production claim). Ask before any bullet claims Terraform production work.

## Machines
- Work laptop: Windows 11, Claude Code (Git Bash). Personal laptop: Linux. Also uses claude.ai.
