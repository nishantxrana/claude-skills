# Content rules

## 1. The bullet

`[Strong verb] + [what] + [scale, outcome or mechanism]`, at most 2 lines (about 32 words). Name each tool once.

v1 required "a measurable outcome" in every bullet. That pushes toward invented numbers. v2 fills the last slot from this ladder, best available first:

1. **Measured result the user gave** ("cut deploy time from 40 to 12 minutes")
2. **Scale** ("across 5 Function Apps and 3 environments", "16 Jira subtasks")
3. **Mechanism** ("by adding the MSBuild `/p:ExcludeFoldersFromDeployment` argument")
4. **Named deliverable** ("in a 2-3 page findings report")

If only 3 or 4 exist, that is fine. A true mechanism beats a made-up percentage. If a bullet would be stronger with a number, ask the user: "Do you have a figure for X?" Accept "no".

| Weak | Strong (facts permitting) |
|---|---|
| Responsible for CI/CD pipelines | Fixed IIS deployments that synced the Uploads folder by adding an MSBuild exclude argument and `-skip` directives to the release task. |
| Worked on migration | Migrating classic release variables into Variable Group Libraries across 5 Function Apps and 3 environments. |
| Used Terraform | (Skills only if POC. No bullet.) |

## 2. Verbs and tense

- Past tense for finished work, present tense for ongoing work ("Migrating", "Building"). Current role may mix.
- Strong verbs: Architected, Automated, Built, Configured, Deployed, Designed, Diagnosed, Eliminated, Fixed, Implemented, Integrated, Migrated, Optimized, Provisioned, Reduced, Streamlined.
- Never open with: Responsible for, Helped, Worked on, Assisted, Participated, Involved, Tasked, Handled, Utilized, Leveraged.
- The ResumeNext ATS tool has its own verb list. Observed as accepted: Reduced, Built, Led, Deployed, Automated, Developed, Improved, Created, Optimized, Designed. At least one of Secured, Strengthened, Migrated, Streamlined, Spearheaded, Engineered was not accepted. Use accepted verbs when the tool flags openers (Step 5b), as long as the verb stays true to what was done.
- No first person. No "results-driven", "passionate", "dynamic", "team player", "detail-oriented".
- Do not open 3 or more bullets with the same verb.

## 3. Honesty tiers

| Proof level | Allowed in Skills | Allowed in bullets |
|---|---|---|
| production | yes | yes, as stated |
| POC | yes | only worded as built or evaluated, never "in production" |
| conceptual (user has used it a little or studied it and confirms they can discuss it in an interview) | yes, once the user confirms | no, unless they actually did that work |
| learning | yes if the user confirms | no |
| unknown | no | no (ask first) |

Every conceptual item gets an entry in the interview prep sheet (`/resume:prep`): the concepts an interviewer will probe, so the user can study them before the interview. Record the user's decision in the profile so it is not asked again.

Where two tools do the same job, use the one the user actually works in (for example Bash vs PowerShell) and keep that as a standing preference in their profile.

## 4. Client and internal names

Client names, internal system names and environment codes can breach confidentiality and mean little to a recruiter. Default: ask once. If the user chose to name a client in their own resume (for example for a cost-saving result), keep it and note it in the reply as a conscious choice. Pass any name they want removed to `resume_check.py --avoid`. Security findings: describe categories ("hard-coded credentials in config files"), never the specific repo, credential or host.

## 5. Certifications

Vendors retire, rename and expire certifications, and ATS matching is literal.

1. **Search current status** for each one: official name, exam code, retirement date, replacement.
2. List only what the user has **earned**. "Pursued" or "studied" is not earned. If the profile says the user keeps their certifications renewed, do not re-ask about validity; still never list a cert they say has lapsed as current.
3. **Check validity.** As far as I know, Microsoft role-based and associate certifications expire 12 months after earning unless renewed (free renewal assessment in the 6 months before expiry). A cert earned May 2025 and not renewed shows as expired from May 2026 on Microsoft Learn, and a retired exam can no longer be renewed. Ask the user to check their Learn transcript.
4. If expired or retired, the entry may stay as an honest history line: `Official Name (CODE) | Earned Mon YYYY` plus `(retired)` or `(expired Mon YYYY)`. Never present an expired cert as current.
5. Format: `Official Full Name (EXAM-CODE) | Mon YYYY`. Do not add the replacement exam unless earned.

## 6. Skills section

- 4 to 5 short rows beat 3 long ones. Group by theme, most JD-relevant first, keep each row to 2 lines or fewer.
- **Rows must match their label.** An AI service under "Monitoring" is a miscategorization; give it an AI row.
- **Every tool a bullet proves must also appear in Skills.** Recruiters and ATS search the Skills block first.
- Literal search terms matter: `Azure Pipelines` as well as `Azure DevOps`, `CI/CD` as a standalone term, `Git`, `Infrastructure as Code (Terraform)`, `Retrieval-Augmented Generation (RAG)`.
- Only add what the user has used or confirmed. Trivial implications (Git when GitLab and GitHub Actions are listed) may be added visibly and flagged.
- No soft skills, proficiency bars, or years per tool.

## 7. Summary (required)

Every resume has a Summary section, placed before Skills (house rule, 2026-10-22; ATS tools flag its absence). Use `--no-summary` only if the user opts out, and then fall back to a one-line headline (title + 3 core tools, real title only).

- 3 lines maximum, 120 to 600 characters, body size (`\small`), same section style as the rest.
- Order: specialty and platform, 2 to 3 core tools or methods mirroring the JD's vocabulary, one verifiable achievement from the ledger, then (if the user confirms) target locations as "Open to relocate to A, B, C" and "full-time" when the JD says so.
- No years of experience unless accurate (count from the earliest relevant role date; never round up to meet a JD's "3+ years").
- No adjectives ("results-driven", "passionate"), no first person.
- Every statement must also be provable in the bullets or Skills below it.

## 8. Tailoring to a JD

- Reorder before rewriting: move the most relevant Skills row and bullets up.
- Reword toward the JD's vocabulary only where the statement stays true.
- Title match matters to recruiters' searches: keep the user's real job title; if the JD title differs, put the JD term in a bullet or Skills, not in the title line.
- Remove, do not hide: never use white text, tiny text or off-page keywords.

## 9. Length: strictly 1 page

House rule: **1 page, always**, unless the user explicitly says multiple pages are fine. This replaces the earlier "2 pages at 8+ years" guidance. Fit by editing words, never by shrinking fonts, margins or spacing: shorten bullets to about one line, cut project blurbs to 2 lines, merge Skills rows, drop the weakest bullet, tighten the Summary. If a page would otherwise overflow by a few lines, fix with word trims first (verbs like "Spearheaded" and "Streamlined" are also longer; prefer short accepted verbs).

## 9b. One body font size

House rule: all body text is one size. In the template that is `\small` (10pt on an 11pt base). Applies to Summary, Skills rows, bullets, Projects, Certifications and the role/date line. Larger: name (`\Large`) and section headings (`\large`, small caps). Bold company and school lines keep the template's own hierarchy. Skills rows must therefore be `\item\small{...}` (the original template had them at the base size, which looks uneven next to the bullets). `resume_check.py` reports `body font size` and warns on mixed sizes.

## 10. Claim risk (interview exposure)

Resumes get probed line by line. Before delivering, list bullets that claim more than the proof level or the user's own account supports, and ask:
- A tool the user called a weak area, or only used in a POC, written as a production achievement.
- Outcome words with no evidence ("eliminated manual configuration drift", "faster mean-time-to-resolution"). Keep if the user can explain them in an interview; otherwise soften to the mechanism.
Never delete the user's claim silently; ask, and let them decide.

## 11. Honest ATS scoring

Chasing 100 on the ATS tool is a goal only while every line stays true. Terms the user has not confirmed, invented metrics, invented URLs and unclaimed experience never go into a version meant to be sent, however many points they add. See SKILL.md Step 5b for the loop and the `TEST_ONLY` convention.
