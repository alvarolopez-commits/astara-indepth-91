# In Depth #91 — build

Regenerates `index_91.html` from the PDF (verbatim text), the Excel v2 (chart data) and the files in this folder.
The build is self-contained: it does not read any other page.

Run from the project folder (the one containing `index_91.html` and `deploy/`). The PDF and Excel are not part of the repository; keep them next to the project:

```bash
python -X utf8 _build/pdf_paras.py "Octubre 1ª - Octubre 2ª In Depth EV_AV_Trucks.pdf" _build/paras.json
python -X utf8 _build/prep_data.py EV_AV_Trucks_InDepth_Data_v2.xlsx _build/data.json
python -X utf8 _build/build91.py _build .
```

`paras.json` and `data.json` are committed, so the last command alone rebuilds the page without the PDF or Excel.

- `body91.html` — page structure; `{{s1p1}}`-style markers are replaced with the PDF paragraphs.
- `style91.css` — the single stylesheet (tokens, palette, type scale, components).
- `app91.js` — charts and interactions; `/*__DATA__*/` is replaced with `data.json`.
- `prep_data.py` — timeline selection (key milestones, targets), map cleaning, alliance normalisation.
- `build91.py` — writes the page and checks that every PDF block appears exactly once and unaltered (exit code 1 otherwise).

Images are optimised WebP files in `deploy/img/` (1672 px and 840 px versions of the four illustrations).
