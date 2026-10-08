"""Builds index_91.html from the files in _build/ (self-contained: no dependency on the #90 page).
Usage (from the project folder):  python -X utf8 _build/build91.py _build .
Fails (exit code 1) if any PDF paragraph is missing, duplicated or altered."""
import json, sys, re, html as H

S, PROJ = sys.argv[1], sys.argv[2]
read = lambda name: open(f"{S}/{name}", encoding="utf-8").read()

HEAD = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Two Revolutions, One Truck — Astara Intelligence In Depth #91</title>
<meta name="description" content="The electrification and autonomy of heavy freight, 2019–2026. Astara Intelligence In Depth #91.">
<meta name="theme-color" content="#221E41">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="preload" as="image" href="deploy/img/hero-1672.webp" imagesrcset="deploy/img/hero-840.webp 840w, deploy/img/hero-1672.webp 1672w" imagesizes="100vw">
<style>
"""

css, body, js = read("style91.css"), read("body91.html"), read("app91.js").replace("/*__DATA__*/null", read("data.json"))
P = json.load(open(f"{S}/paras.json", encoding="utf-8"))
paras, full = dict(P["paras"]), P["fulltext"]

# derived splits: each is checked to rebuild the original paragraph exactly
i = paras["s7p3"].index("The winners"); paras["s7p3a"], paras["s7p3b"] = paras["s7p3"][:i].rstrip(), paras["s7p3"][i:]
assert paras["s7p3a"] + " " + paras["s7p3b"] == paras["s7p3"]
a, b = paras["s1p5"].split(": ", 1); paras["s1p5a"], paras["s1p5b"] = a + ":", b
assert paras["s1p5a"] + " " + paras["s1p5b"] == paras["s1p5"]
lead, rest = paras["s7p1"].split(". ", 1); paras["s7p1_lead"] = lead + "."
qs = [q + "?" for q in rest.rstrip("?").split("? ")]
assert len(qs) == 5, qs
for n, q in enumerate(qs, 1): paras[f"s7p1_q{n}"] = q
assert " ".join([paras["s7p1_lead"]] + qs) == paras["s7p1"]

# ---- timelines: pre-rendered as static HTML (readable without JavaScript) ----
D = json.loads(read("data.json"))
CATS = {"product": ("Product & technology", "#8BCDFF"), "deploy": ("Orders, fleets & partnerships", "#3EC6C6"),
        "capital": ("Capital, strategy & policy", "#B79CFF"), "fail": ("Failures & retrenchment", "#FF8F9C")}
ARROW = {-1: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
         1: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'}
e = lambda s: H.escape(str(s))
cap = lambda s: s[:1].upper() + s[1:]

def render_timeline(key):
    items, phases = D[key], D["phases"][key]
    years = list(range(min(d["y"] for d in items), max(d["y"] for d in items) + 1))
    span = [y for p in phases for y in range(p["from"], p["to"] + 1)]
    assert span == years, (key, span, years)  # phases cover every year once, in order
    dense = [y for y in years if sum(d["y"] == y for d in items) >= 6]
    cols = " ".join("calc(var(--yw)*var(--dm))" if y in dense else "var(--yw)" for y in years)
    TRACK_OPEN = (f'<div class="tl__track" style="--cols:{cols};width:calc(({len(years) - len(dense)} + {len(dense)}*var(--dm))*var(--yw))">')
    legend = ('<div class="key-legend">' + "".join(f'<span><i style="background:{c}"></i>{e(l)}</span>' for l, c in CATS.values())
              + '<span><i class="sq" style="background:#333A60;border:1px solid rgba(220,229,237,.3)"></i>Key milestone</span>'
              + '<span><span class="chip chip--tgt">Target</span> announced goal, not yet achieved</span></div>')
    o = ['<div class="tl" data-tl>',
         f'<div class="tl__bar">{legend}<div class="tl__nav">'
         f'<button type="button" class="tl__btn" data-dir="-1" aria-label="Scroll to earlier years">{ARROW[-1]}</button>'
         f'<button type="button" class="tl__btn" data-dir="1" aria-label="Scroll to later years">{ARROW[1]}</button></div></div>',
         '<div class="tl__fade tl__fade--l" aria-hidden="true"></div><div class="tl__fade tl__fade--r" aria-hidden="true"></div>',
         f'<div class="tl__viewport" tabindex="0" role="region" aria-label="{key.upper()} timeline {years[0]}–{years[-1]}, scrolls horizontally">',
         TRACK_OPEN,
         '<div class="tl__phases">' + "".join(
             f'<div class="tphase" style="grid-column:span {p["to"] - p["from"] + 1}"><span class="tphase__label">Phase 0{i + 1} · <b>{e(p["name"])}</b></span></div>'
             for i, p in enumerate(phases)) + "</div>",
         '<ol class="tl__years">']
    n_cards = 0
    for y in years:
        evs = [d for d in items if d["y"] == y]   # data order = chronological order within the year
        o.append(f'<li class="tyear{" tyear--dense" if len(evs) >= 6 else ""}"><div class="tyear__head"><span class="tyear__label">{y}</span></div>')
        if evs:
            o.append('<ul class="tyear__events">')
            for d in evs:
                lab, col = CATS[d["g"]]
                cls = "tcard" + (" tcard--key" if d["key"] else "") + (" tcard--tgt" if d["tgt"] else "")
                chip = '<span class="chip chip--tgt">Target</span>' if d["tgt"] else ""
                sr = f'Category: {e(lab)}.' + (" Key milestone." if d["key"] else "")
                o.append(f'<li class="{cls}" style="--c:{col}"><div class="tcard__co"><i class="tcard__dot" aria-hidden="true"></i><span>{e(d["who"])}</span>{chip}</div>'
                         f'<p class="tcard__t">{e(cap(d["t"]))}</p><span class="sr-only">{sr}</span></li>')
                n_cards += 1
            o.append("</ul>")
        else:
            o.append('<p class="tyear__empty">No selected events this year.</p>')
        o.append("</li>")
    o.append("</ol></div></div>")
    o.append(f'<div class="tl__progress" role="progressbar" aria-label="Position in the timeline" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">'
             f'<span>{years[0]}</span><div class="tl__bar-track"><i class="tl__bar-thumb"></i></div><span>{years[-1]}</span></div>')
    o.append("</div>")
    assert n_cards == len(items), (key, n_cards, len(items))
    print(f"timeline {key}: {n_cards} events in {len(years)} years ({years[0]}–{years[-1]}), {len(phases)} phases")
    return "\n".join(o)

for k in ("ev", "av"):
    assert f"[[TIMELINE:{k}]]" in body
    body = body.replace(f"[[TIMELINE:{k}]]", render_timeline(k))

used = set()
def sub(m):
    k = m.group(1); used.add(k)
    return H.escape(paras[k], quote=False)
body = re.sub(r"\{\{([a-z0-9_]+)\}\}", sub, body)
assert "{{" not in body

page = HEAD + css + "</style>\n</head>\n<body>\n\n" + body + \
    '\n<script src="deploy/d3.v7.min.js"></script>\n<script src="deploy/topojson-client.min.js"></script>\n<script src="deploy/countries-110m.js"></script>\n<script>\n' + js + "\n</script>\n\n</body></html>\n"
open(f"{PROJ}/index_91.html", "w", encoding="utf-8").write(page)

# ---- verification: every PDF block used exactly once and unaltered; excerpts literal ----
fail = []
blocks = list(P["paras"])
missing = [k for k in blocks if k not in used and not any(u.startswith(k + "_") or u in (k + "a", k + "b") for u in used)]
print("PDF blocks:", len(blocks), "missing:", missing)
if missing: fail.append("missing blocks")
cnt = {k: len(re.findall(r'data-pdf="%s"' % k, body)) for k in blocks}
bad = {k: v for k, v in cnt.items() if v != 1}
print("data-pdf markers not exactly once:", bad)
if bad: fail.append("markers")
norm = lambda s: re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
fulln = norm(full)
for ex in re.findall(r'class="[^"]*excerpt-text[^"]*">(.*?)</', body):
    ok = norm(ex) in fulln
    print("excerpt OK" if ok else "EXCERPT NOT IN PDF", "|", norm(ex)[:70])
    if not ok: fail.append("excerpt")
for k in [x for x in blocks if not x.startswith("s7p1")]:
    seg = re.search(r'data-pdf="%s"[^>]*>(.*?)</(?:p|span)>' % k, body, flags=re.S)
    if not (seg and norm(seg.group(1)) == norm(H.escape(paras[k]))):
        print("MISMATCH", k); fail.append("mismatch " + k)
blk = re.search(r'data-pdf="s7p1">(.*?)</ol>', body, flags=re.S).group(1)
qtext = [norm(x) for t in re.findall(r'<p class="body-text lead-para reveal"[^>]*>(.*?)</p>|<p class="q__text">(.*?)</p>', blk) for x in t if x]
ok7 = " ".join(qtext) == paras["s7p1"]
print("s7p1 rebuilt OK:", ok7)
if not ok7: fail.append("s7p1")
print(len(page), "bytes written")
if fail:
    print("BUILD CHECK FAILED:", fail); sys.exit(1)
