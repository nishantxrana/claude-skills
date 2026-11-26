# ATS research record (last reviewed 2026-10-21)

Evidence is split into **measured** (reproduced in this skill's own tests on a real resume) and **reported** (web sources, mostly vendor and SEO blogs, so moderate confidence at best).

## Measured (high confidence)

| Finding | How tested | Consequence |
|---|---|---|
| The user's hand-curated template is structurally sound: 1 page, vector fonts with Unicode maps, black links, standard headings, clean text layer. | `resume_check.py` on the real resume | Template is left alone. Improvement is content. |
| The old skill's embedded template differed from the user's real template (no `colorlinks`, so it drew coloured link boxes). | render + pixel scan | v2 template = the user's file. |
| Adding `\input{glyphtounicode}`, `\pdfgentounicode=1` and `pdftitle/pdfauthor` changes no pixel. | `pixel_diff.py`, 150 dpi, 0 differing pixels | These are the only allowed template edits. |
| Type 3 bitmap bullets appeared only because the sandbox lacked `cm-super`; after `apt-get install cm-super lmodern` the same template had zero Type 3 fonts. | `pdffonts` before/after | Fix the environment, never the template. |
| In layout-order extraction (`pdftotext` default) the two-row right-aligned header separates dates and location from role and company; content-order extraction (`-raw`) keeps them adjacent. | `pdftotext` both modes | Reported as INFO, not a defect: it is the look the user chose. |
| fi/fl ligatures extract correctly with poppler. | `pdftotext` | `glyphtounicode` kept as insurance for other extractors. |

## Reported (moderate confidence)

| Claim | Source | Use |
|---|---|---|
| Single column, standard fonts, contact in the body, no tables/text boxes parse best | jobcannon.io, jobshinobi.com (2026) | Already true of the user's template. |
| Copy-paste the PDF text as a quick parse test | jobshinobi.com | Automated. |
| Standard LaTeX resume templates add `glyphtounicode` + `pdfgentounicode` for ATS | GitHub templates (swhasans, kfaizi forks of Jake Gutierrez's); Typst forum | Adopted (invisible). |
| LaTeX resumes are rarely tested for text extraction | lilachbullock.com | Principle: test, do not assume. |
| 1 page under about 7 to 10 years; 2 pages reasonable beyond; ATS does not penalize length | techinterview.org, atsverification.com, rezi.ai, recruiteze.com | Default 1 page; the user's file decides. Sources disagree on the threshold. |
| DevOps screening clusters: cloud platform, containers, IaC and CI/CD; recruiters search tool names; certifications searched by exact name | resumegeni.com, enhancv.com | Verbatim JD terms; real postings preferred over keyword lists. |
| Core skills near the top | enhancv.com | Skills-first order (user's choice). |

## ATS tool measurements (ResumeNext `analyze_resume`, 2026-10-22)

One tool, one resume, one JD (Azure DevOps / Cloud Engineer). Observations, not guarantees; other ATS vendors differ.

| Observation | Effect |
|---|---|
| No Summary section | Flagged "important"; Content score lost points (resume without it: 83/100) |
| Summary 120 to 600 chars added, plus JD terms in Skills | 83 -> 90 |
| JD city names (Gurugram, Pune) missing | Keyword coverage stuck below 100% until the cities appeared in text (a Summary relocation line fixed it) |
| LinkedIn URL absent | Flagged optional; adding a URL cleared it |
| "full-time" in the JD | Counted as a keyword; coverage hit 100% once the word appeared |
| Action-verb check | Flags bullets whose opener is not in its list; it names only the first one's section, not the line. Counts fell 6 -> 3 -> 2 -> 1 as openers moved to accepted verbs; the last flagged bullet was never identified. Best score reached: 99/100 |
| Project entries starting with a title instead of a verb | Counted against the verb check until rewritten to open with "Built ...", "Developed ..." |
| Quantified-achievements flag | Cleared when bullets carried numbers (only use numbers the user supplied) |

## Certification facts (2026-10-21)

- **AI-102** retired 2026-06-30 (replacement AI-103); the Lumify listing states it can no longer be earned or renewed after that date. Several sources agree.
- **AZ-204** reported retiring 2026-07-31 (replacement AI-200). Single vendor source (whizlabs.com): verify on Microsoft Learn.
- Validity: associate certs expire after 12 months unless renewed, as far as I know; **not verified in this session**. Ask the user to check their transcript.

## Open

- Which ATS each employer uses and how it orders extracted text. The checker tests two extraction orders, not every vendor.
- Whether AI screeners weight semantic match over literal keywords. Literal matching assumed for safety.

## URLs
https://jobcannon.io/blog/what-is-an-ats-friendly-resume
https://jobshinobi.com/blog/ats-optimized-resume-formatting-rules-2026
https://github.com/swhasans/Resume/blob/main/resume.tex
https://forum.typst.app/t/is-there-an-equivalent-to-latexs-pdfgentounicode-1-in-typst/7533
https://www.lilachbullock.com/build-resume-latex-template/
https://www.techinterview.org/post/3233474607/engineering-resume-one-page-vs-two/
https://atsverification.com/blog/resume-length-1-page-vs-2-pages/
https://resumegeni.com/ats-keywords/devops-engineer-ats-keywords
https://enhancv.com/resume-examples/azure-devops-engineer/
https://learn.microsoft.com/en-us/answers/a/12700187
https://www.lumifywork.com/en-nz/certifications/microsoft-certified-azure-ai-engineer-associate
https://www.whizlabs.com/blog/microsofts-next-generation-ai-certifications/

## Update 2026-11-26 (v3)

### Measured
| Observation | Effect |
|---|---|
| ResumeNext `analyze_resume` on the current resume, no JD | 99/100 (Structure 100, Content 98, Contact 100). Only issue: "Action verbs" pointing at the role line "Software Engineer - DevOps & Cloud", i.e. the tool parsed the title row as a bullet. Not fixable without changing the template's two-row heading; reported, not chased. |
| PyMuPDF (layout + stream order) and PDFium on the same PDF | All three agree on sections, contact and clean Unicode. Used as the v3 multi-engine parse check, replacing poppler as a hard dependency. |

### Tools surveyed (2026-11-26)
| Tool | What it is | Verdict |
|---|---|---|
| ResumeNext ATS Resume Checker (connector, `analyze_resume`) | Hosted, deterministic score, issues list, JD coverage | Keep as the primary score |
| ResumeNext Job Match & Resume Keyword Scanner (connector) | Matched/missing JD keywords and a job-tailored score | Optional second opinion when connected |
| cv-mirror-mcp (npm, MIT, local) | Heuristic simulators for Workday, Greenhouse, Lever, Taleo, iCIMS; no AI, no upload (author's claim) | Not added as a dependency; its rule ideas are built into `resume_check.py` (ATS: rows) |
| Other community MCP servers (resume-optimizer, resume-ats-mcp, Jobscan wrappers) | Keyword-overlap scores | Duplicate `jd_terms.py` + `check --keywords`; Jobscan needs an account |
| Career suites in the plugin directory (Career Navigator, Career Compass, Career Desk) | Broad job-search assistants | Not ATS scorers; out of scope |

### Reported parser rules (moderate confidence; vendor docs as cited by ResumeGeni 2026, and practitioner tests)
- Greenhouse: accepts DOC, DOCX, PDF, RTF, TXT; parse failures from images, graphics, tables, headers/footers, text boxes, columns, unclear sections (vendor-cited).
- Workday: reads PDFs in stream order, so columns interleave; standard headings; consistent dates (practitioner).
- Lever: may drop header/footer text; images not parsed (vendor-cited for images).
- Taleo: Month-Year dates fill durations most reliably; DOCX is the conservative choice on old forms (practitioner).
- iCIMS: weakest with multi-column sidebars (practitioner).
- No vendor documents AI ranking that replaces keyword search; documented mechanisms are parsing to fields, Boolean/keyword search, scorecards and knock-out questions.

### URLs (v3)
https://resumegeni.com/blog/ats-system-guide
https://dev.to/goofypluto999/i-built-an-open-source-mcp-server-that-lints-a-cv-against-5-real-ats-parsers-pjb
https://glama.ai/mcp/servers/aliameenrana/ATS
https://hugounoclaw.github.io/ats-checker/guides/how-ats-works.html
https://www.techinterview.org/post/3233474603/ats-friendly-resume-formatting-engineers/

### Measured 2026-11-26 (text fed to the ATS tool)
| Text given to `analyze_resume` | Score |
|---|---|
| Raw layout extraction (wrapped lines kept, bullets on their own lines) | 78: tool read every wrapped line as a new job entry, "dates missing", "6 action verbs" |
| Logical text from `resume_check.py --text-out` (wrapped lines rejoined, one bullet per line) | 99: only the known role-line quirk |
Always feed the `--text-out` file, never raw `pdftotext` output.
