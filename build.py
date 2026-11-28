#!/usr/bin/env python3
"""Costruisce index.html di Milano My Events.

Legge data/sources/*.json (un file per fonte) e data/meta.json, applica le
regole di categoria / bambini / gratis agli eventi che non le hanno già,
toglie gli eventi finiti da più di 3 giorni e scrive index.html da template.html.

Uso:  python3 build.py            # build normale
      python3 build.py --check    # solo controlli, non scrive nulla
"""
import json, re, sys, glob, os, datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
TZ = ZoneInfo("Europe/Rome")

# file -> nome fonte mostrato, categoria di default, se è aggiornata in automatico
SOURCES = {
    "corte-dei-miracoli":        ("Corte dei Miracoli", "Concerti", True),
    "biko":                      ("Biko", "Concerti", True),
    "nidaba":                    ("Nidaba", "Concerti", True),
    "better-together-sito":      ("Better Together (sito)", "Better", True),
    "better-together-instagram": ("Better Together (Instagram)", "Better", True),
    "milano-da-scrocco":         ("Milano da Scrocco", "Altro", True),
    "teatri-possibili":          ("Teatri Possibili", "Altro", True),
    "planetario":                ("Planetario", "Altro", True),
    "osteria-del-jazz":          ("Osteria del Jazz", "Concerti", False),
    "parteciprato-newsletter":   ("ParteciPrato (newsletter)", "Altro", False),
    "teatro-carcano":            ("Teatro Carcano", "Teatro", False),
    "manuali-vari":              ("Instagram (manuale)", "Altro", False),
    "proposte":                  ("Proposte dal modulo", "Altro", False),
}
CAT_GROUP = {"Cinema": "Cinema", "Corso": "Corsi", "Teatro": "Teatro", "Stand-up": "Teatro"}

KIDS_PER = ["in una goccia", "benvenuta catastrofe", "il senno tra le rime", "teatro ragazzi", "per bambini", "laboratorio per bambini"]
KIDS_ADATTO = ["villaggio delle meraviglie", "villa litta", "nativitas", "artigiano in fiera", "milano al duomo", "brueghel",
    "dalí e la moda", "nivola", "aki sasamoto", "luciano fabro", "shilpa gupta", "le prime stelle", "pulci pettinate",
    "siam christmas", "mercatone", "cotoletta vintage", "buona domenica", "merkatino kolbe", "roda de choro",
    "concerto di natale", "amore in musica", "christmas carol", "verso il sol levante", "taglietti", "mimmo dabbrescia",
    "together to shop", "pattinaggio", "mercatino", "market"]
NOT_KIDS = ["violenza", "horror", "drag me to", "com'eri vestita", "indie-club", "karmadrome"]
FESTIVI = {"2026-12-07", "2026-12-08", "2026-12-24", "2026-12-26", "2026-12-28", "2026-12-29", "2026-12-30",
           "2026-12-31", "2027-01-01", "2027-01-02", "2027-01-05", "2027-01-06", "2026-12-23"}


def group_for(e, default):
    if e["source"].startswith("Better Together"):
        return "Better"
    return CAT_GROUP.get(e.get("cat", ""), default)


def kids_for(e):
    t = (e["title"] + " " + e.get("note", "")).lower()
    if any(k in t for k in NOT_KIDS):
        return ""
    if any(k in t for k in KIDS_PER):
        return "per"
    if e["source"] == "Planetario" and e.get("time"):
        wd = datetime.date.fromisoformat(e["start"]).weekday()
        if int(e["time"][:2]) < 19 and (wd >= 5 or e["start"] in FESTIVI):
            return "adatto"
        return ""
    if any(k in t for k in KIDS_ADATTO):
        return "adatto"
    return ""


def free_for(e):
    if e["source"] == "Milano da Scrocco":
        return True
    price = e.get("price", "")
    t = (e["title"] + " " + e.get("note", "") + " " + price).lower()
    if "donazione minima" in t:
        return False
    return bool(re.search(r"gratis|gratuit|ingresso libero", t))


def load():
    events, counts = [], {}
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "sources", "*.json"))):
        key = os.path.basename(path)[:-5]
        if key not in SOURCES:
            sys.exit(f"Fonte sconosciuta: {key}. Aggiungila a SOURCES in build.py")
        name, default_group, _ = SOURCES[key]
        data = json.load(open(path, encoding="utf-8"))
        for e in data:
            for f in ("title", "start"):
                if not e.get(f):
                    sys.exit(f"{key}: evento senza {f}: {e}")
            e.setdefault("end", e["start"])
            for f in ("time", "end_time", "venue", "price", "url", "note", "cat"):
                e.setdefault(f, "")
            if not re.fullmatch(r"\d{4}-\d\d-\d\d", e["start"]) or not re.fullmatch(r"\d{4}-\d\d-\d\d", e["end"]):
                sys.exit(f"{key}: data non valida in {e['title']}")
            e["source"] = name
            if "group" not in e:
                e["group"] = group_for(e, default_group)
            if "kids" not in e:
                e["kids"] = kids_for(e)
            if "free" not in e:
                e["free"] = free_for(e)
        counts[name] = len(data)
        events += data
    return events, counts


def main():
    check = "--check" in sys.argv
    now = datetime.datetime.now(TZ)
    cutoff = (now.date() - datetime.timedelta(days=3)).isoformat()
    events, counts = load()
    events = [e for e in events if e["end"] >= cutoff]
    events.sort(key=lambda e: (e["start"], e["time"] or "99", e["title"]))
    for i, e in enumerate(events):
        e["id"] = i
    meta = json.load(open(os.path.join(ROOT, "data", "meta.json"), encoding="utf-8"))
    meta["snapshot"] = now.date().isoformat()
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
    meta["updated"] = f"{now.day} {mesi[now.month-1]} {now.year}, {now:%H:%M}"
    if check:
        print(f"OK: {len(events)} eventi, fonti: {counts}")
        return
    json.dump(meta, open(os.path.join(ROOT, "data", "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tpl = open(os.path.join(ROOT, "template.html"), encoding="utf-8").read()
    html = tpl.replace("__DATA__", json.dumps(events, ensure_ascii=False)).replace("__META__", json.dumps(meta, ensure_ascii=False))
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print(f"Scritto index.html: {len(events)} eventi")


if __name__ == "__main__":
    main()
