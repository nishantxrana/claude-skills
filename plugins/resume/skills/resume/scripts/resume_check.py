#!/usr/bin/env python3
"""
resume_check.py - compile a LaTeX resume and audit the PDF the way an ATS sees it.

  python resume_check.py resume.tex [--outdir DIR] [--max-pages 1] [--final]
        [--keywords kw.txt] [--avoid "ClientA,ProjectX"] [--json report.json]
        [--pdf-out Name_Resume.pdf] [--text-out resume.txt] [--no-summary]
  python resume_check.py --pdf someone.pdf ...   # audit an existing PDF (no compile, no source lints)

Policy defaults: STRICTLY 1 page (--max-pages 2 only if the user allows more), a Summary
section is REQUIRED (--no-summary only if the user opts out), ONE body font size.

Engines: PyMuPDF (layout and content-stream order), PDFium (a second, independent extractor)
and poppler's pdftotext when installed. Works on Windows, Linux, macOS and the claude.ai sandbox.
Exit 0 = no FAIL, 1 = at least one FAIL (do not deliver).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import compile_tex, run  # noqa: E402

try:
    import pymupdf as fitz
except ImportError:  # older PyMuPDF
    import fitz  # type: ignore

PASS, WARN, FAIL, INFO = "PASS", "WARN", "FAIL", "INFO"
rows: list[tuple[str, str, str]] = []
metrics: dict = {}


def add(status, check, detail=""):
    rows.append((status, check, detail))


SECTION_NAMES = {
    "summary", "professional summary", "skills", "technical skills", "experience", "work experience",
    "professional experience", "projects", "certifications", "education", "achievements", "awards",
    "publications", "volunteering", "languages",
}
MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
DATE = (rf"(?:(?:{MONTH}\s*\d{{4}})|(?:\d{{1,2}}/\d{{4}})|\d{{4}}|\[[A-Z][A-Z _/-]+\])"
        rf"\s*[\u2013\u2014-]+\s*(?:Present|Current|Now|(?:{MONTH}\s*\d{{4}})|(?:\d{{1,2}}/\d{{4}})|\d{{4}}|\[[A-Z][A-Z _/-]+\])")
PLACEHOLDER_STRICT = re.compile(r"\[[A-Z][A-Z0-9 _/-]{1,}\]|TODO|FIXME|XXXX|FULL NAME|Tool, Tool|Verb \+ what")

# Canonical spellings recruiters and ATS search for (wrong -> right). Case-sensitive, whole word.
CANON = {
    r"Github": "GitHub", r"Gitlab": "GitLab", r"Javascript": "JavaScript", r"Typescript": "TypeScript",
    r"Nodejs|NodeJS|NodeJs|Node JS": "Node.js", r"ReactJS|Reactjs|ReactJs": "React.js",
    r"Azure Devops|Azure devops|AzureDevOps|Azure Dev Ops": "Azure DevOps", r"Kubernates|Kubernets": "Kubernetes",
    r"Mongodb|MongoDb|Mongo DB": "MongoDB", r"Mysql|MySql": "MySQL", r"Postgresql|PostgresQL|Postgre SQL": "PostgreSQL",
    r"Powershell|Power Shell": "PowerShell", r"Dotnet|DotNet|\.Net": ".NET", r"Fastapi|FastApi": "FastAPI",
    r"Graphql|GraphQl": "GraphQL", r"Restful|REST-ful": "RESTful", r"Ci/Cd|CI/Cd|ci/cd|CICD": "CI/CD",
    r"Aws": "AWS", r"Gcp": "GCP", r"Sql": "SQL", r"Json": "JSON", r"Yaml": "YAML", r"Devops": "DevOps",
    r"Sharepoint": "SharePoint", r"Openai|OpenAi": "OpenAI", r"Github Actions|GitHub actions": "GitHub Actions",
}
LOWER_TOOLS = ["kubernetes", "docker", "terraform", "jenkins", "ansible", "python", "grafana", "prometheus",
               "azure", "linux", "github", "gitlab", "typescript", "javascript"]


def norm_lines(text):
    return [l.strip() for l in text.splitlines()]


BULLET = "•◦▪"


def logical_text(text):
    """Plain text with the document's logical structure: wrapped lines rejoined, one bullet per
    line, right-aligned columns separated by ' | '. Feed THIS to text-only ATS tools; raw layout
    text makes them read every wrapped line as a new entry (measured 2026-11-26: 78 vs 99)."""
    out, cur = [], None
    for raw in text.splitlines():
        line = re.sub(r"\s{3,}", " | ", raw.strip())
        if not line or line in ("•", "◦"):
            if cur is not None:
                out.append(cur)
                cur = None
            if not line:
                out.append("")
            continue
        m = re.match(rf"^[{BULLET}]\s*(.*)$", line)
        if m and line[0] in "•◦▪":
            if cur is not None:
                out.append(cur)
            cur = "- " + m.group(1)
        elif cur is not None and line.lower() not in SECTION_NAMES and not re.search(DATE, line):
            cur += (" " if not cur.endswith("-") else "") + line
        else:
            if cur is not None:
                out.append(cur)
                cur = None
            out.append(line)
    if cur is not None:
        out.append(cur)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


# --------------------------------------------------------------- PDF facts
def audit_pdf_basics(doc, args):
    pages = doc.page_count
    r = doc[0].rect
    metrics.update(pages=pages, page_w_pt=round(r.width), page_h_pt=round(r.height))
    paper = "A4" if abs(r.width - 595) < 3 else "Letter" if abs(r.width - 612) < 3 else "custom"
    if pages > args.max_pages:
        add(FAIL, "page count", f"{pages} pages, limit {args.max_pages}. Trim words, never fonts or spacing")
    else:
        add(PASS, "page count", f"{pages} page(s) ({paper})")
    title = (doc.metadata or {}).get("title", "")
    add(PASS if title else WARN, "pdf metadata", f"title '{title}'" if title else "no PDF title (set pdftitle in hyperref)")


def audit_fonts(doc):
    fonts = {}
    for pno in range(doc.page_count):
        for xref, ext, ftype, basefont, *_ in doc.get_page_fonts(pno):
            fonts[xref] = (ext, ftype, basefont)
    if not fonts:
        add(FAIL, "fonts", "no fonts found (image-only or scanned PDF: ATS reads nothing)")
        return
    t3 = [b for x, (e, t, b) in fonts.items() if t == "Type3"]
    noemb = [b for x, (e, t, b) in fonts.items() if e == "n/a" and t != "Type3"]
    nouni = [b for x, (e, t, b) in fonts.items()
             if t != "Type3" and doc.xref_get_key(x, "ToUnicode")[0] == "null"]
    metrics.update(fonts=len(fonts), type3_fonts=len(t3), no_unicode_fonts=len(nouni))
    if t3:
        add(FAIL, "fonts: Type 3", f"{len(t3)} bitmap font(s): glyphs (often bullets) extract as blanks. "
            "Fix the ENVIRONMENT (cm-super fonts; see env_check.py), never the user's fonts.")
    if noemb:
        add(FAIL, "fonts: not embedded", ", ".join(noemb))
    if nouni:
        add(WARN, "fonts: no ToUnicode", ", ".join(nouni) + " - keep \\input{glyphtounicode} + \\pdfgentounicode=1")
    if not (t3 or noemb or nouni):
        add(PASS, "fonts", f"{len(fonts)} vector fonts, embedded, Unicode-mapped")


# -------------------------------------------------------------- extraction
def extract_all(doc, pdf: Path):
    """Text from every available engine. Returns dict engine -> text."""
    out = {
        "pymupdf-layout": "\n".join(p.get_text("text", sort=True) for p in doc),
        "pymupdf-stream": "\n".join(p.get_text("text") for p in doc),
    }
    try:
        import pypdfium2 as pdfium
        pd = pdfium.PdfDocument(str(pdf))
        parts = [pd[i].get_textpage().get_text_range() for i in range(len(pd))]
        out["pdfium"] = "\n".join(parts).replace("\r\n", "\n").replace("\r", "\n")
        pd.close()
    except Exception as e:  # pragma: no cover
        add(INFO, "pdfium", f"not available ({type(e).__name__}): one engine fewer")
    if shutil.which("pdftotext"):
        out["poppler"] = run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"]).stdout
    return out


def garbled(text):
    bad = []
    if "(cid:" in text: bad.append("(cid:NN) glyph ids")
    if re.search("[\ufb00-\ufb06]", text): bad.append("unexpanded ligatures")
    if "\ufffd" in text: bad.append("replacement chars")
    return bad


def sections_in(text):
    return [l.lower() for l in norm_lines(text) if l.lower() in SECTION_NAMES]


def audit_engines(texts):
    """Every engine must give clean text, the same sections, and the contact details."""
    hard, soft = [], []
    ref = None
    for eng, t in texts.items():
        b = garbled(t)
        if b:
            hard.append(f"{eng}: " + ", ".join(b))
        secs = sections_in(t)
        if ref is None:
            ref = secs
        elif secs != ref:
            soft.append(f"{eng}: sections {secs} differ from {ref}")
        if not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", t):
            hard.append(f"{eng}: no email found")
    metrics["engines"] = list(texts)
    if hard:
        add(FAIL, "parse across engines", "; ".join((hard + soft)[:3]))
    elif soft:
        add(WARN, "parse across engines", "; ".join(soft[:2]))
    else:
        add(PASS, "parse across engines", f"{len(texts)} extractors agree on sections and contact ({', '.join(texts)})")


def audit_text(text, stream, args):
    lines = norm_lines(text)
    nonempty = [l for l in lines if l]
    metrics["words"] = len(text.split())
    bad = garbled(text)
    add(FAIL if bad else PASS, "text layer", ("garbled: " + ", ".join(bad)) if bad else f"clean Unicode, {metrics['words']} words")

    top = "\n".join(nonempty[:8])
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", top)
    phone = re.search(r"\+?\d[\d\s().-]{8,}\d", top)
    first = re.split(r"\s{2,}|\s+(?:Email|E-mail|Phone|Mobile)\b", nonempty[0])[0] if nonempty else ""
    name_ok = 2 <= len(first.split()) <= 5 and not re.search(r"[@\d|]", first)
    miss = [n for n, ok in (("name", name_ok), ("email", email), ("phone", phone)) if not ok]
    add(FAIL if miss else PASS, "contact block",
        ("not found in first 8 lines: " + ", ".join(miss)) if miss else "name, email, phone in the body near the top")
    links = re.findall(r"(?:linkedin\.com/in/[\w-]+|github\.com/[\w-]+)", text, re.I)
    metrics["profile_links"] = links
    add(PASS if any("linkedin" in l.lower() for l in links) else WARN, "profile links",
        ", ".join(dict.fromkeys(links)) if links else "no LinkedIn URL visible as text (ATS tools flag it)")

    found = [(i, l.lower()) for i, l in enumerate(lines) if l.lower() in SECTION_NAMES]
    names = [n for _, n in found]
    need = [s for s in ("skills", "experience") if not any(s in n for n in names)]
    add(FAIL if need else PASS, "section headings",
        ("standard heading(s) not detected: " + ", ".join(need)) if need else " > ".join(n.title() for n in names))
    metrics["sections"] = names

    if not args.no_summary:
        idx = next((i for i, n in found if "summary" in n), None)
        if idx is None:
            add(FAIL, "summary section", "missing: add a 3-line Summary (120-600 chars) or pass --no-summary")
        else:
            nxt = min([i for i, _ in found if i > idx] or [len(lines)])
            body = " ".join(l for l in lines[idx + 1:nxt] if l).lstrip("\u2022 ").strip()
            metrics["summary_chars"] = n = len(body)
            add(PASS if 120 <= n <= 600 else WARN, "summary section",
                f"{n} chars" + ("" if 120 <= n <= 600 else "; aim for 120-600 (about 3 lines)"))

    def detached(src):
        out = []
        for i, l in enumerate(src):
            if not re.search(DATE, l) or "|" in l:
                continue
            rest = re.sub(r"\[[A-Z _/-]+\]", "", re.sub(DATE, "", l))
            if re.findall(r"[A-Za-z]{3,}", rest):
                continue
            prev = next((src[j] for j in range(i - 1, -1, -1) if src[j]), "")
            if len(prev.split()) < 4 and "|" not in prev:
                out.append(f"'{prev}' / '{l}'")
        return out

    d_layout, d_stream = detached(lines), detached(norm_lines(stream))
    metrics.update(detached_dates=len(d_layout), detached_dates_stream=len(d_stream))
    if d_stream:
        add(WARN, "dates vs role", f"{len(d_stream)} date(s) detached from the role even in content order (e.g. {d_stream[0]})")
    elif d_layout:
        add(INFO, "dates vs role", f"{len(d_layout)} date(s) split from the role in layout order only; content order intact")
    else:
        add(PASS, "dates vs role", "every date range stays with its role line")

    ph = PLACEHOLDER_STRICT.findall(text)
    metrics["placeholders"] = len(ph)
    if ph:
        add(FAIL if args.final else WARN, "placeholders", f"{len(ph)} unresolved: " + ", ".join(sorted(set(ph))[:8]))
    else:
        add(PASS, "placeholders", "none")

    if args.avoid:
        terms = [t.strip() for t in args.avoid.split(",") if t.strip()]
        hits = [t for t in terms if re.search(re.escape(t), text, re.I)]
        add(FAIL if hits else PASS, "avoid-terms", ("present: " + ", ".join(hits)) if hits else "none present")
    return lines


# ----------------------------------------------------- per-ATS parse rules
def audit_ats_rules(doc, text):
    """Heuristics reported for common ATS parsers (Workday, Taleo, iCIMS, Greenhouse, Lever).
    Sources are vendor docs and practitioner tests; see references/ats-research.md."""
    notes = []
    odd = sorted({c for c in text if ord(c) > 0x24FF and c not in "\u2022\u25e6\u2013\u2014\u2018\u2019\u201c\u201d"})
    if odd:
        notes.append((WARN, "symbols", "non-text glyphs may be stripped (Greenhouse drops emoji): " + " ".join(odd[:10])))
    styles = set()
    for r in re.findall(DATE, text):
        styles.add("Mon YYYY" if re.search(MONTH, r) else "MM/YYYY" if "/" in r else "YYYY")
    metrics["date_styles"] = sorted(styles)
    if len(styles) > 1:
        notes.append((INFO, "date styles", f"mixed {sorted(styles)}: Month YYYY parses most reliably (Taleo); "
                                           "years-only on Education is common and usually fine"))
    band = 0.35 * 72
    hits = [b[4].strip()[:30] for p in doc for b in p.get_text("blocks") if b[1] > p.rect.height - band]
    if hits:
        notes.append((WARN, "footer band", "text in the bottom 0.35in may be read as a footer and dropped: " + "; ".join(hits[:2])))
    p0 = doc[0]
    W = p0.rect.width
    wide = 0
    for b in p0.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            spans = [s for s in ln["spans"] if s["text"].strip()]
            wide += sum(1 for a, c in zip(spans, spans[1:]) if c["bbox"][0] - a["bbox"][2] > 0.25 * W)
    metrics["split_rows"] = wide
    if wide > 8:
        notes.append((WARN, "columns", f"{wide} rows have a wide mid-line gap: looks multi-column (Workday, iCIMS interleave)"))
    else:
        notes.append((PASS, "columns", f"single column ({wide} right-aligned date/location rows, normal)"))
    imgs = sum(len(p.get_images()) for p in doc)
    metrics["images"] = imgs
    if imgs:
        notes.append((WARN, "images", f"{imgs} image(s): parsers ignore text inside images"))
    for s, c, d in notes:
        add(s, f"ATS: {c}", d)


def audit_canonical(text):
    def outside_url(m):
        ctx = text[max(0, m.start() - 25):m.end() + 25]
        return not re.search(r"[/@]|\.(com|io|dev|me)\b", ctx)
    bad = []
    for wrong, right in CANON.items():
        bad += [f"{m.group(0)}->{right}" for m in re.finditer(rf"(?<![\w.]){wrong}(?![\w])", text) if outside_url(m)]
    for t in LOWER_TOOLS:
        bad += [f"{t}->{t.capitalize()}" for m in re.finditer(rf"(?<![\w./@-]){t}(?![\w./-])", text) if outside_url(m)]
    metrics["spelling_issues"] = bad
    add(WARN if bad else PASS, "tool spellings",
        ("fix: " + ", ".join(dict.fromkeys(bad))) if bad else "canonical (GitHub, Node.js, Azure DevOps...)")


# ------------------------------------------------------------ render checks
def audit_body_sizes(doc):
    spans = [s for p in doc for b in p.get_text("dict")["blocks"] for ln in b.get("lines", []) for s in ln["spans"]]
    head_tops = [s["bbox"][1] for s in spans if "CSC" in s["font"]]
    first_head = min(head_tops) if head_tops else 0
    cnt = Counter()
    for s in spans:
        f = s["font"]
        if "CSC" in f or "BX" in f or "Bold" in f or s["flags"] & 16 or s["bbox"][1] < first_head:
            continue
        n = sum(ch.isalnum() for ch in s["text"])
        if n:
            cnt[round(s["size"], 1)] += n
    total = sum(cnt.values()) or 1
    body = {sz: n for sz, n in cnt.items() if 8.5 <= sz <= 11.6 and n / total > 0.03 and n >= 40}
    metrics["body_sizes"] = {str(k): v for k, v in sorted(cnt.items())}
    if len(body) > 1:
        desc = ", ".join(f"{sz}pt ({n * 100 // total}%)" for sz, n in sorted(body.items()))
        add(WARN, "body font size", f"mixed body sizes: {desc}. Use one size (\\small rows)")
    else:
        sz = next(iter(body), None)
        add(PASS, "body font size", f"uniform body text ({sz}pt)" if sz else "no body text found")


def audit_widows(doc):
    """Last lines of a bullet holding only 1-2 short words waste a line (was a manual visual check)."""
    hits = []
    for p in doc:
        W = p.rect.width
        for b in p.get_text("dict")["blocks"]:
            lines = b.get("lines", [])
            for i, ln in enumerate(lines):
                txt = "".join(s["text"] for s in ln["spans"]).strip()
                if not (1 <= len(txt.split()) <= 2) or i == 0:
                    continue
                x0, x1 = ln["bbox"][0], ln["bbox"][2]
                if x0 > 0.45 * W or (x1 - x0) > 0.18 * W:
                    continue
                if any("CSC" in s["font"] or "BX" in s["font"] for s in ln["spans"]) or re.fullmatch(r"[\u2022\u25e6-]", txt):
                    continue
                prev = lines[i - 1]
                if abs(prev["bbox"][0] - x0) < 40 and prev["bbox"][2] > 0.6 * W:
                    hits.append(txt)
    metrics["widows"] = hits
    add(WARN if hits else PASS, "short last lines",
        (f"{len(hits)} line(s) carry only 1-2 words: " + ", ".join(f"'{h}'" for h in hits[:5]) +
         ". Trim a few words to win the line back") if hits else "no 1-2 word last lines")


def audit_render(doc, outdir: Path, pages: int):
    from PIL import Image
    for stale in outdir.glob("page-*.png"):
        stale.unlink()
    imgs = []
    for i, p in enumerate(doc, 1):
        f = outdir / f"page-{i}.png"
        p.get_pixmap(dpi=100).save(str(f))
        imgs.append(f)
    metrics["png"] = [str(p) for p in imgs]
    last = Image.open(imgs[-1]).convert("RGB")
    first = Image.open(imgs[0]).convert("RGB")

    def bbox(im):
        return im.convert("L").point(lambda v: 255 if v < 245 else 0).getbbox()

    bb = bbox(last)
    h = last.size[1]
    gap = (h - bb[3]) / h * 100
    metrics["bottom_gap_pct"] = round(gap, 1)
    if pages == 1:
        if gap <= 8:
            add(PASS, "page fill", f"bottom gap {gap:.1f}% of page height")
        else:
            add(WARN, "page fill", f"bottom gap {gap:.1f}%: room for real content (ask the user). Never pad")
        if gap < 3.5:
            add(WARN, "page fill", f"content {gap:.1f}% from the bottom edge: crowded, trim")
    else:
        used = bb[3] / h
        add(WARN if used < 0.25 else PASS, "last page", f"page {pages} {used * 100:.0f}% used")
    bb1 = bbox(first)
    metrics["margins_in"] = dict(left=round(bb1[0] / 100, 2), right=round((first.size[0] - bb1[2]) / 100, 2),
                                 top=round(bb1[1] / 100, 2))
    px = first.load()
    colored = sum(1 for y in range(0, first.size[1], 2) for x in range(0, first.size[0], 2)
                  if max(px[x, y]) - min(px[x, y]) > 60)
    metrics["colored_pixels"] = colored
    add(WARN if colored > 10 else PASS, "link boxes",
        f"{colored} coloured sample pixels: visible link boxes" if colored > 10 else "none visible")


def audit_links(doc, text):
    uris = [l.get("uri") for p in doc for l in p.get_links() if l.get("uri")]
    metrics["links"] = uris
    flat = re.sub(r"\s+", "", text.lower())
    bad = [u for u in uris if u.startswith("http://")]
    hidden = [u for u in uris if not u.startswith("mailto:") and
              re.sub(r"^https?://(www\.)?", "", u).rstrip("/").lower() not in flat]
    msg = f"{len(uris)} clickable link(s)"
    if hidden:
        msg += f"; {len(hidden)} URL(s) not printed as text (parsers keep visible URLs only): " + ", ".join(hidden[:3])
    if bad:
        msg += "; insecure http: " + ", ".join(bad)
    add(WARN if (bad or hidden) else INFO, "links", msg)


# ------------------------------------------------------------- source lints
WEAK = {"responsible", "helped", "worked", "assisted", "participated", "involved", "tasked", "handled",
        "utilized", "leveraged", "exposed", "was", "did"}
STRONG = {"reduced", "built", "led", "deployed", "automated", "developed", "improved", "created", "optimized",
          "designed", "architected", "configured", "diagnosed", "eliminated", "fixed", "implemented", "integrated",
          "migrated", "provisioned", "streamlined", "cut", "launched", "delivered", "scaled", "secured", "migrating",
          "building", "designing", "leading", "owned", "established", "standardized", "accelerated", "resolved",
          "wrote", "published", "mentored", "trained", "won", "increased", "decreased", "saved"}
BUZZ = ["results-driven", "passionate", "synergy", "self-starter", "team player", "hard-working", "hardworking",
        "go-getter", "detail-oriented", "dynamic", "responsible for", "proven track record"]


def clean_tex(s):
    s = re.sub(r"\\textit\{Stack:.*$", "", s)
    s = re.sub(r"\\href\{[^}]*\}", "", s)
    s = re.sub(r"\\(?:textit|textbf|texttt|small)\b", "", s)
    s = s.replace("\\&", "&").replace("\\%", "%").replace("\\_", "_").replace("--", "-").replace("~", " ")
    return re.sub(r"[{}\\]", "", s).strip()


def tex_bullets(tex: Path):
    cur, out = None, []
    for l in tex.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\s*\\section\{([^}]*)\}", l)
        if m:
            cur = m.group(1).lower()
            continue
        m = re.match(r"^\s*\\resumeItem\{(.*)\}\s*$", l)
        if m:
            out.append(("experience", clean_tex(m.group(1))))
            continue
        m = re.match(r"^\s*\\item\\small\{(.*)\}\s*$", l)
        if m and cur == "projects":
            out.append(("projects", clean_tex(m.group(1))))
    return out


def lint_bullets(tex: Path):
    bullets = tex_bullets(tex)
    metrics["bullets"] = len(bullets)
    if not bullets:
        add(INFO, "bullet lint", "no \\resumeItem{...} or project items found")
        return
    issues, firsts = [], Counter()
    for sec, b in bullets:
        words = b.split()
        fw = words[0].lower().strip(",:;") if words else ""
        firsts[fw] += 1
        if fw in WEAK: issues.append(f"weak opener '{words[0]}'")
        elif fw not in STRONG: issues.append(f"opener '{words[0]}' is not a common action verb")
        if re.search(r"\b(I|my|me|we|our)\b", b): issues.append(f"first person in '{b[:40]}'")
        issues += [f"buzzword '{z}'" for z in BUZZ if z in b.lower()]
        lim = 45 if sec == "projects" else 38
        if len(words) > lim: issues.append(f"{len(words)} words: '{b[:36]}...'")
        if len(words) < 8: issues.append(f"too thin ({len(words)} words): '{b[:36]}'")
    issues += [f"opener '{fw}' used {n}x" for fw, n in firsts.items() if n >= 3 and fw]
    ends = [b.rstrip().endswith(".") for s, b in bullets if s == "experience"]
    if any(ends) and not all(ends): issues.append("mixed trailing periods")
    with_num = sum(1 for _, b in bullets if re.search(r"\d", b))
    metrics.update(bullets_with_number=with_num, bullet_issues=len(issues), openers=dict(firsts.most_common()))
    if issues:
        add(WARN, "bullet lint", f"{len(issues)} issue(s): " + "; ".join(issues[:5]) + (" ..." if len(issues) > 5 else ""))
    else:
        add(PASS, "bullet lint", f"{len(bullets)} bullets: action-verb openers, no buzzwords, none overlong")
    add(INFO, "numbers", f"{with_num}/{len(bullets)} bullets carry a number (only user-confirmed figures)")


# -------------------------------------------------------------- JD keywords
def audit_keywords(text, lines, kwfile: Path):
    terms = []
    for l in kwfile.read_text(encoding="utf-8").splitlines():
        l = l.split("#")[0].strip()
        if l:
            terms.append([a.strip() for a in l.split("|") if a.strip()])
    idx = {l.lower(): i for i, l in enumerate(lines) if l.lower() in SECTION_NAMES}
    sk = next((i for k, i in idx.items() if "skills" in k), None)
    nxt = sorted(i for i in idx.values() if sk is not None and i > sk)
    if sk is not None and nxt:
        skills_txt = "\n".join(lines[sk:nxt[0]])
        body_txt = "\n".join(lines[:sk] + lines[nxt[0]:])
    else:
        skills_txt, body_txt = "", text

    def has(t, s):
        return re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", s, re.I) is not None

    found, skills_only, missing = [], [], []
    for alts in terms:
        if any(has(a, body_txt) for a in alts): found.append(alts[0])
        elif any(has(a, skills_txt) for a in alts): skills_only.append(alts[0])
        else: missing.append(alts[0])
    cov = (len(found) + len(skills_only)) / max(1, len(terms)) * 100
    metrics.update(keyword_coverage_pct=round(cov), keywords_missing=missing, keywords_skills_only=skills_only)
    add(INFO, "JD keywords", f"{cov:.0f}% present ({len(found)} in bullets, {len(skills_only)} Skills only, {len(missing)} absent)")
    if missing: add(INFO, "  absent", ", ".join(missing) + "  -> ask the user; add ONLY what they confirm")
    if skills_only: add(INFO, "  skills-only", ", ".join(skills_only) + "  -> also prove in a bullet where true")


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex", nargs="?")
    ap.add_argument("--pdf", help="audit an existing PDF instead of compiling")
    ap.add_argument("--outdir")
    ap.add_argument("--max-pages", type=int, default=1)
    ap.add_argument("--no-summary", action="store_true")
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--keywords")
    ap.add_argument("--avoid")
    ap.add_argument("--json")
    ap.add_argument("--pdf-out")
    ap.add_argument("--text-out", help="write the extracted plain text (feed this to the ATS tool)")
    args = ap.parse_args()
    if not args.tex and not args.pdf:
        ap.error("give a .tex file or --pdf")

    outdir = Path(args.outdir) if args.outdir else Path(tempfile.mkdtemp(prefix="resume_check_"))
    outdir.mkdir(parents=True, exist_ok=True)
    tex = Path(args.tex) if args.tex else None
    if args.pdf:
        pdf = Path(args.pdf)
        add(INFO, "compile", "skipped: auditing an existing PDF")
    else:
        pdf, log, errs = compile_tex(tex, outdir)
        if not pdf:
            add(FAIL, "compile", " | ".join(errs))
        else:
            add(PASS, "compile", "pdflatex x2, exit 0")
            over = [float(m) for m in re.findall(r"Overfull \\hbox \(([\d.]+)pt", log) if float(m) > 1.0]
            if over:
                add(WARN, "overfull lines", f"{len(over)} line(s) stick out of the margin (max {max(over):.1f}pt)")
            if "Missing character" in log:
                add(FAIL, "missing glyphs", "LaTeX dropped characters")
            other = [l for l in log.splitlines() if "Warning" in l and not any(
                k in l for k in ("rerunfilecheck", "footskip", "Overfull", "Underfull"))]
            if other:
                add(WARN, "latex warnings", f"{len(other)}: " + "; ".join(w.strip()[:90] for w in other[:2]))

    if pdf:
        doc = fitz.open(str(pdf))
        audit_pdf_basics(doc, args)
        audit_fonts(doc)
        audit_body_sizes(doc)
        texts = extract_all(doc, pdf)
        audit_engines(texts)
        text, stream = texts["pymupdf-layout"], texts["pymupdf-stream"]
        lines = audit_text(text, stream, args)
        audit_ats_rules(doc, text)
        audit_canonical(text)
        audit_widows(doc)
        audit_render(doc, outdir, doc.page_count)
        audit_links(doc, text)
        if args.keywords:
            audit_keywords(text, lines, Path(args.keywords))
        tx = outdir / "resume.txt"
        tx.write_text(logical_text(text), encoding="utf-8")
        metrics["text_file"] = str(tx)
        if args.text_out and Path(args.text_out).resolve() != tx.resolve():
            shutil.copy(tx, args.text_out)
        if args.pdf_out and not args.pdf:
            shutil.copy(pdf, args.pdf_out)
        doc.close()
    if tex:
        lint_bullets(tex)

    w = max(len(c) for _, c, _ in rows)
    print(f"\n{(tex or pdf).name}\n" + "-" * 78)
    for s, c, d in rows:
        print(f"{s:<5} {c:<{w}}  {d}")
    nf = sum(1 for s, _, _ in rows if s == FAIL)
    nw = sum(1 for s, _, _ in rows if s == WARN)
    print("-" * 78)
    print(f"RESULT: {'FAIL' if nf else 'PASS'}  ({nf} fail, {nw} warn)   build dir: {outdir}")
    if metrics.get("png"):
        print(f"View the render: {metrics['png'][0]}")
    if args.json:
        Path(args.json).write_text(json.dumps(dict(rows=rows, metrics=metrics, fails=nf, warns=nw), indent=2))
    sys.exit(1 if nf else 0)


if __name__ == "__main__":
    main()
