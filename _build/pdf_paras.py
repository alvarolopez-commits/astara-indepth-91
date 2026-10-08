"""Extract the editorial paragraphs of the #91 PDF verbatim, keyed by section/paragraph.
Usage: python pdf_paras.py <pdf> <out.json>"""
import json, re, sys, pypdf

pdf, out = sys.argv[1], sys.argv[2]
r = pypdf.PdfReader(pdf)
lines = []
for p in r.pages:
    for ln in p.extract_text().split("\n"):
        if ln.strip().startswith("Astara Intelligence · Two revolutions, one truck"):
            continue  # running page header
        lines.append(ln.strip())
text = re.sub(r"\s+", " ", " ".join(lines)).strip()

# Paragraph starts (in reading order). Section headings / visual labels act as hard stops.
STARTS = [
    ("s1p1", "A heavy truck is not bought"),
    ("s1p2", "The electric transition is already real"),
    ("s1p3", "In Europe, the most important change"),
    ("s1p4", "Autonomy is at an earlier stage"),
    ("s1p5", "That is the central tension"),
    ("v1", "From 2019 roadmaps and early funding"),
    ("s2p1", "The electric truck story can now be read"),
    ("s2p2", "Between 2019 and 2021, manufacturers"),
    ("s2p3", "The next phase brought the first serious"),
    ("s2p4", "By 2024–2026, the discussion had shifted"),
    ("s2p5", "So, the question is changing."),
    ("s3p1", "Autonomous trucking followed a more dramatic path."),
    ("s3p2", "Then the model was tested by reality."),
    ("s3p3", "The more recent phase is different."),
    ("s3p4", "But the scale gap remains enormous."),
    ("v2", "The path from pilots and SPACs"),
    ("s4p1", "The funding history tells a useful story."),
    ("s4p2", "That money created scale"),
    ("s4p3", "The more resilient companies"),
    ("v3", "The casualties of the 2020–2021 funding wave"),
    ("s5p1", "The market is not developing at the same speed"),
    ("s5p2", "Europe is moving more slowly"),
    ("s5p3", "The US is taking a different path."),
    ("s5p4", "The company map reflects that geography."),
    ("v4", "A world view of the main companies"),
    ("s6p1", "Electric and autonomous trucks are not separate stories."),
    ("s6p2", "This is important because the eventual winner"),
    ("s6p3", "The alliance network makes that visible."),
    ("v5", "Disclosed capital raised from 2021 to 2026."),
    ("v6", "The network linking truck makers"),
    ("s7p1", "The next phase will be judged less by announcements"),
    ("s7p2", "For fleets, the decision is becoming practical"),
    ("s7p3", "The simple conclusion is that both revolutions"),
]
STOPS = [
    r"VISUAL \d — [^\n]*?(?= [A-Z])", r"\d\. (The truck is being rebuilt twice|Electric trucks: from promise to product|Autonomous trucks: from pilot to driverless|The shake-out: capital creates winners and losers|Where the market is moving|The two revolutions are starting to converge|What matters next)",
]
VISUAL_LABELS = ["VISUAL 1 — EV timeline", "VISUAL 2 — AV timeline", "VISUAL 3 — Exits and failures",
                 "VISUAL 4 — Company map: EV and AV", "VISUAL 5 — Funding by year: EV vs AV", "VISUAL 6 — Alliances"]
HEADINGS = ["1. The truck is being rebuilt twice", "2. Electric trucks: from promise to product",
            "3. Autonomous trucks: from pilot to driverless", "4. The shake-out: capital creates winners and losers",
            "5. Where the market is moving", "6. The two revolutions are starting to converge", "7. What matters next"]
cut = text
for m in VISUAL_LABELS + HEADINGS:
    assert m in cut, m
    cut = cut.replace(m, "\u0000")

pos = []
for k, s in STARTS:
    i = cut.find(s)
    assert i >= 0, (k, s)
    pos.append((i, k))
pos.sort()
assert [k for _, k in pos] == [k for k, _ in STARTS], "order mismatch"
paras = {}
for n, (i, k) in enumerate(pos):
    j = pos[n + 1][0] if n + 1 < len(pos) else len(cut)
    seg = cut[i:j]
    seg = seg.split("\u0000")[0].strip()
    paras[k] = seg
json.dump({"paras": paras, "fulltext": text}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in paras.items():
    print(k, len(v), "|", v[:60], "...", v[-40:])
