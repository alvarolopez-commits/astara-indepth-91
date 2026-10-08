"""Reads EV_AV_Trucks_InDepth_Data_v2.xlsx and writes data.json for the #91 HTML build."""
import json, sys, openpyxl

XLSX = sys.argv[1]
OUT = sys.argv[2]
wb = openpyxl.load_workbook(XLSX, data_only=True)


def rows(name):
    ws = wb[name]
    hdr = [c.value for c in ws[1]]
    return [dict(zip(hdr, r)) for r in ws.iter_rows(min_row=2, values_only=True) if any(v is not None for v in r)]


# ---------- timelines: curated rows (sheet row number -> short label, bold name, group) ----------
# groups: product | deploy | capital | fail
EV = {
    2: ("Traton", "commits billions to e-mobility", "capital"),
    3: ("Nikola", "goes public via SPAC, opening the 2020–21 capital wave", "capital"),
    5: ("Mercedes-Benz Trucks", "unveils the eActros LongHaul: long-haul enters OEM roadmaps", "product"),
    6: ("Volvo Trucks", "pledges to electrify its entire line-up", "capital"),
    8: ("Transport & Environment", "study: electric trucks close to cost parity with diesel", "capital"),
    14: ("Volta Trucks", "closes a €230M round, the peak of European e-truck start-up funding", "capital"),
    15: ("Volvo Trucks", "receives a record electric-truck order from Maersk", "deploy"),
    19: ("Renault Trucks", "opens its heavy electric range for orders", "product"),
    20: ("Tesla", "starts Semi deliveries, first to PepsiCo", "product"),
    22: ("Nikola", "cuts 23% of its workforce", "fail"),
    23: ("Mercedes-Benz Trucks", "40-tonne eActros 600 drives 1,000 km with a single charging stop", "product"),
    24: ("Volta Trucks", "files for bankruptcy after raising $390.9M", "fail"),
    25: ("Amazon", "puts its first electric semis into freight operations", "deploy"),
    27: ("Nikola", "files for Chapter 11; peak market value was ~$26–30B in 2020", "fail"),
    29: ("Harbinger", "raises a $160M Series C co-led by FedEx", "capital"),
    30: ("Bollinger Motors", "shuts down amid financial woes", "fail"),
    31: ("Kenworth / Peterbilt", "launch new electric trucks for North America", "product"),
    35: ("Tesla", "Semi's first truck rolls off the high-volume production line", "product"),
    36: ("Tesla", "confirms an 822 kWh battery for the Semi", "product"),
    37: ("Windrose", "Tesla Semi challenger reported to be missing paychecks and a truck", "fail"),
    38: ("Mars / Rewe", "deploy 47 battery-electric trucks on a shared pilot corridor", "deploy"),
    40: ("Amazon", "receives its first eActros 600 trucks in Germany", "deploy"),
    42: ("BYD", "brings the ETT 44 to Europe: 600 km range, 20-minute charge", "product"),
    43: ("Volvo Trucks", "starts production of the FH Aero Electric", "product"),
    44: ("Scania", "announces a battery solution for 720 km of range", "product"),
    46: ("FedEx / Harbinger", "FedEx orders 2,000 electric trucks in a $300M deal", "deploy"),
}
EV_KEY = {3, 8, 14, 20, 24, 27, 35, 42, 43}   # key milestones named in the PDF narrative
EV_TGT = set()

AV = {
    2: ("Daimler Truck", "buys a stake in Torc Robotics", "capital"),
    3: ("Starsky Robotics", "runs the first uncrewed truck at highway speed (55 mph)", "product"),
    5: ("Starsky Robotics", "shuts down after failing to find a buyer or investors", "fail"),
    7: ("Waymo / Daimler Truck", "Waymo Driver is to power Daimler trucks", "deploy"),
    9: ("Volvo / Aurora", "partner on autonomous transport solutions", "deploy"),
    10: ("TuSimple", "IPO raises $1.35B, peak of the AV-trucking capital cycle", "capital"),
    12: ("Embark", "announces a SPAC deal at a $5.2B valuation", "capital"),
    13: ("Aurora", "lists on Nasdaq via SPAC, ~$1.8B gross proceeds", "capital"),
    14: ("TuSimple / Navistar / DHL", "sell 100 self-driving trucks to DHL", "deploy"),
    15: ("TuSimple", "completes its first driverless run on public roads", "product"),
    19: ("Waymo Via", "pauses its trucking programme", "fail"),
    20: ("Embark", "sold to Applied Intuition for ~$71M, about 1% of its SPAC valuation", "fail"),
    22: ("Pony.ai", "wins its first autonomous trucking licence in Guangzhou", "capital"),
    23: ("TuSimple", "winds down its US operations", "fail"),
    24: ("Aurora / Uber Freight", "sign a long-term driverless truck deal after a pilot", "deploy"),
    25: ("Volvo / DHL", "begin autonomous truck operations", "deploy"),
    27: ("Waabi / Volvo", "partner on the Volvo VNL Autonomous", "deploy"),
    28: ("Aurora", "launches commercial driverless operations in Texas", "deploy"),
    30: ("Kodiak", "lists via SPAC", "capital"),
    31: ("Einride", "completes the world's first autonomous border crossing", "deploy"),
    33: ("Einride", "announces a SPAC with Legato at a $1.8B valuation", "capital"),
    35: ("Gatik", "operates fully driverless trucks at commercial scale", "deploy"),
    36: ("Waabi", "raises a $750M Series C, the largest private AV-truck round in the set", "capital"),
    39: ("PlusAI", "SPAC business combination terminated", "fail"),
    40: ("California DMV", "finalises rules opening the state to heavy-duty autonomous trucks", "capital"),
    41: ("Aurora", "selected by a leading carrier to scale to 500 trucks", "deploy"),
    43: ("Volvo", "targets a $3B autonomous business within five years", "capital"),
    46: ("Einride / Lidl", "launch the first cab-less truck on a German public road", "deploy"),
    47: ("Pony.ai / GAC", "unveil the Gen-4 robotruck, with European sales targeted", "product"),
    48: ("Aurora", "targets 30,000 driverless trucks by 2030, from about 20 today", "capital"),
    49: ("Kodiak", "picks Dallas–Houston for its driverless long-haul launch", "deploy"),
}
AV_KEY = {2, 3, 10, 12, 13, 19, 20, 23, 28, 35, 46, 48}
AV_TGT = {41, 43, 48, 49}   # announced goals / plans, not achieved results


def timeline(sheet, picks, keys, tgts):
    ws = wb[sheet]
    out = []
    for r, (who, text, grp) in sorted(picks.items()):
        year = ws.cell(r, 1).value
        assert isinstance(year, int), (sheet, r, year)
        out.append({"y": year, "who": who, "t": text, "g": grp, "key": r in keys, "tgt": r in tgts})
    return out


# ---------- exits ----------
exits = [
    {"y": r["Year"], "co": r["Company"], "seg": r["Segment"], "region": r["Region"], "out": r["Outcome"], "ctx": r["Context"]}
    for r in rows("04_Exits_Failures")
]

# ---------- funding by year (values frozen in v2) ----------
fb = {}
ws = wb["11_Funding_By_Year"]
for r in ws.iter_rows(min_row=4, max_row=9, values_only=True):
    if isinstance(r[0], int):
        fb[r[0]] = {"avPub": r[4], "avVen": r[5], "evVen": r[6], "total": r[3]}
tot = [r for r in ws.iter_rows(min_row=4, max_row=12, values_only=True) if r[0] == "Total"][0]
funding = {"years": [{"y": y, **v} for y, v in sorted(fb.items())], "totalAV": tot[1], "totalEV": tot[2], "total": tot[3]}

# ---------- map: region aggregation with documented corrections ----------
REGION = {"US": "United States", "CA": "Canada", "CN": "China", "IN": "India", "JP": "Japan & Korea", "KR": "Japan & Korea"}
EU = {"FI", "CH", "NL", "FR", "ES", "GB", "CZ", "DE", "SE"}
drop = {"Torc", "Kodiak", "Senior Auto"}  # duplicates of Torc Robotics / Kodiak Robotics / Sinian zhijia
fix_iso = {"Bolinger Motors": "US", "Rideflux": "KR"}
agg = {}
for r in rows("06_Map_Companies"):
    name = r["Company"]
    if name in drop:
        continue
    iso = fix_iso.get(name, r["ISO"])
    reg = "Europe" if iso in EU else REGION[iso]
    seg = r["Segment"]
    d = agg.setdefault(reg, {"EV": 0, "AV": 0, "BOTH": 0, "names": {"EV": [], "AV": []}})
    if seg == "EV + AV":
        d["BOTH"] += 1
        d["names"]["EV"].append(name); d["names"]["AV"].append(name)
    else:
        d[seg] += 1
        d["names"][seg].append(name)
mapdata = [{"region": k, **v} for k, v in agg.items()]

# ---------- alliances: normalise names, split compound parties ----------
canon = {"Volvo Trucks": "Volvo", "Mercedes-Benz Trucks": "Daimler Truck", "NVIDIA": "Nvidia", "Chery Heavy Trucks": "Chery Heavy Trucks"}
split = {"Navistar / DHL": ["Navistar", "DHL"], "Nvidia / Continental": ["Nvidia", "Continental"], "Gotion / Green Power Morocco": ["Gotion"]}
edges = {}
for r in rows("12_Alliances"):
    a, b, seg = r["Party A"], r["Party B"], r["Segment"]
    A = split.get(a, [a]); B = split.get(b, [b])
    for x in A:
        for y in B:
            x2, y2 = canon.get(x, x), canon.get(y, y)
            key = tuple(sorted((x2, y2)))
            e = edges.setdefault(key, {"s": x2, "t": y2, "seg": set(), "year": r["Year"]})
            e["seg"].add(seg)
            e["year"] = min(e["year"], r["Year"])
types = {
    "oem": ["Volvo", "Daimler Truck", "Paccar", "Traton", "Navistar", "International Motors", "Isuzu", "GAC", "Tata Daewoo", "BYD", "Tesla", "Harbinger", "Chery Heavy Trucks"],
    "dev": ["Aurora", "Waabi", "Torc", "Waymo", "TuSimple", "Embark", "Kodiak", "Gatik", "Plus", "Pony.ai", "Rideflux", "Einride", "Outrider"],
    "tech": ["Nvidia", "Continental", "McLeod Software", "Gotion"],
}
tmap = {n: t for t, ns in types.items() for n in ns}
nodes = {}
for e in edges.values():
    for n in (e["s"], e["t"]):
        nodes.setdefault(n, {"id": n, "type": tmap.get(n, "cust"), "seg": set(), "deg": 0})
        nodes[n]["seg"] |= e["seg"]
        nodes[n]["deg"] += 1
alli = {
    "nodes": [{"id": n["id"], "type": n["type"], "deg": n["deg"], "both": len(n["seg"]) > 1} for n in nodes.values()],
    "links": [{"source": e["s"], "target": e["t"], "seg": sorted(e["seg"])[0] if len(e["seg"]) == 1 else "BOTH"} for e in edges.values()],
}

PHASES = {
    "ev": [
        {"name": "The announcements", "from": 2019, "to": 2021},
        {"name": "First deliveries, first failures", "from": 2022, "to": 2023},
        {"name": "Real products", "from": 2024, "to": 2026},
    ],
    "av": [
        {"name": "Pilots and experiments", "from": 2019, "to": 2020},
        {"name": "Public-market excitement", "from": 2021, "to": 2021},
        {"name": "Tested by reality", "from": 2022, "to": 2024},
        {"name": "Driverless on real freight lanes", "from": 2025, "to": 2026},
    ],
}

data = {
    "phases": PHASES,
    "ev": timeline("02_Timeline_EV", EV, EV_KEY, EV_TGT),
    "av": timeline("03_Timeline_AV", AV, AV_KEY, AV_TGT),
    "exits": exits,
    "funding": funding,
    "map": mapdata,
    "alli": alli,
}
json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ev", len(data["ev"]), "av", len(data["av"]), "exits", len(exits))
print("funding", funding["totalAV"], funding["totalEV"])
print("map", [(m["region"], m["EV"], m["AV"], m["BOTH"]) for m in mapdata])
print("alli nodes", len(alli["nodes"]), "links", len(alli["links"]), "customers", sorted(n["id"] for n in alli["nodes"] if n["type"] == "cust"))
