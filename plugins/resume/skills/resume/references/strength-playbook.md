# Strength playbook: what makes a resume land interviews

ATS checks get a resume read. This file is about what makes the reader say yes. Everything here still obeys the honesty rules: stronger means sharper evidence, never bigger claims.

## 1. The 7-second scan (top third)
Recruiters skim the top third first: name, Summary, the first role and its first two bullets.
- The Summary's first clause names the target role in the JD's words (only if it is the user's real field), then 2 to 3 core tools, then the single best result.
- The **first bullet of the current role is the strongest result**, not the oldest task. Order bullets by impact x relevance to the target JD.
- The best number on the page appears at least once in the top third.

## 2. Bullet strength test
Every bullet must pass "so what?". Shape: `[verb] [what] [scale or result] [how, if it adds credibility]`.
Ladder for the last slot (content-rules section 1): measured result > scale > mechanism > named deliverable.

| Weak | Strong (facts permitting) |
|---|---|
| Worked on Kubernetes deployments | Deployed 20+ .NET microservices to AKS with Helm, enabling zero-downtime rollbacks |
| Created dashboards in Grafana | Built Grafana alerting on Prometheus metrics for 20+ services, catching failures before users reported them |
| Built a tool for variable groups | Built ToolDock, an open-source Azure DevOps toolkit that migrates repos, pipelines and boards between orgs |

## 3. Mining numbers (use with `/resume:mine`)
Ask per bullet, one at a time. Accept "no" and move on; estimates are fine only if the user can explain how they estimated (use "about" or "~").

| Area | Questions |
|---|---|
| Delivery (DORA) | Deploys per week before/after? Lead time from merge to prod? Change failure rate? Time to restore? |
| Pipelines | Build/release minutes before/after? How many pipelines, repos, environments? |
| Cost | Monthly spend before/after, or % saved? Which resources? |
| Reliability | Uptime or SLO? Incidents per month before/after? Alert noise reduced? |
| Scale | Services, clusters, VMs, regions, users, teams, orgs served? |
| Toil | Hours per week saved? Manual steps removed? |
| Security | Findings fixed? Secrets moved to a vault? Projects audited? |
| Adoption | Users, teams, GitHub stars, installs, people who asked for it? Awards? |
| Ownership | Designed it? Led it? Sole owner? Mentored anyone? |

Record answers in `ledger.md` with source "user, <date>".

## 4. Scope and ownership signals
Words that change how senior a line reads, when true: designed, owned, led, end-to-end, production, client-facing, across N teams/orgs, on-call. Never upgrade "helped" to "led". If the user did part of a team effort, name their part.

## 5. Projects that count
- Link (visible URL text), what problem it solves, the hard part, and an adoption or outcome signal.
- Keep the stack list short (5 to 6 items); it is for keywords, not the story.
- Open-source repos: the README must back the claims (a recruiter clicks). Pin the repos on GitHub.
- Keep dates, titles and project names identical across resume, LinkedIn and GitHub.

## 6. Skills strategy
- Order rows by the target JD. Literal JD terms beat synonyms.
- A term proven in a bullet beats a term that only sits in Skills (semantic ATS and humans both weight context). Aim: every must-have JD term appears in Skills AND in at least one bullet, where true.
- "Conceptual" items (studied, not shipped) may sit in Skills when the user confirms they can discuss them; each gets a `/resume:prep` entry.
- No proficiency bars, years per tool or soft skills.

## 7. Keywords without stuffing
- Expand an acronym once where it is searched: `Azure Kubernetes Service (AKS)`.
- Place must-haves in Summary, Skills and a bullet. More than 3 mentions of one term reads as stuffing.
- Never hidden text, white text or keyword blocks.

## 8. Tailoring per JD (fast path)
1. Reorder Skills rows and bullets.
2. Swap 1 to 2 bullets with bullet-bank alternatives that match the JD.
3. Adjust the Summary's first clause and core tools to the JD vocabulary.
4. Only then reword, and only where the statement stays true.

## 9. Consistency polish
Date style (`Mon YYYY -- Present`), tense (past for done, present for ongoing), trailing periods all or none, canonical tool names (GitHub, Node.js, Azure DevOps), numbers as digits (`30%`, `20+`), en dashes in ranges.

## 10. Market notes (India and similar)
- No photo, date of birth, marital status, father's name, religion or full address on the resume (city is enough).
- Notice period and CTC go in the application form, not the resume, unless the employer asks.
- If the JD names cities and the user is open to them, "Open to relocate to A, B" in the Summary helps location searches (only if the user confirms).
- Keep the Naukri and LinkedIn headline/skills in sync with the resume's top terms.

## 11. Red flags to remove
Responsibilities instead of results; tool soup with no outcome; buzzwords; anything the user cannot explain for 2 minutes; outdated or irrelevant items crowding the page; inconsistent dates; broken links.

## 12. Defensibility
Every line should survive "tell me more about that" for 2 minutes: situation, what *they* did, how, result, what they would do differently. `/resume:prep` builds that sheet.

## 13. Strength scorecard (`/resume:review`)
Score 1 to 5 with one-line evidence each, then list the 3 changes with the biggest gain.

| Dimension | 5 looks like |
|---|---|
| Targeting | Summary and top bullets match the target role's vocabulary |
| Impact | Most bullets carry a result or scale |
| Scope and ownership | Clear what the user owned and at what scale |
| Evidence | Links that back the claims; numbers the user can explain |
| Keywords / ATS | `check` passes; must-have JD terms present in context |
| Clarity | 1 to 2 line bullets, no filler, readable in 7 seconds |
| Consistency | Dates, tense, spelling, punctuation uniform |
| Defensibility | No claim beyond its proof level; conceptual items have prep |
