#!/usr/bin/env python3
"""Build the Pokémon TCG catalogue data for the Jekyll site.

Reads pokemon/source/pokemon_bulk_catalogue.xlsx, fetches the full card list of
every set in it from TCGCSV (TCGplayer mirror) and set metadata from TCGdex,
and writes:

  _data/pokemon/sets.json      one summary entry per owned set
  _data/pokemon/<slug>.json    every card + variant of that set, with qty
  pokemon-tcg/<slug>.md        stub page per set (GitHub Pages can't generate
                               pages from data)

Usage:  python pokemon/build_catalogue.py [--refresh]
"""

import argparse
import difflib
import json
import re
import sys
import time
import unicodedata
import warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore", message=".*OpenSSL.*")               # macOS system Python + urllib3 v2
warnings.filterwarnings("ignore", message=".*Data Validation extension.*")  # xlsx dropdowns

import openpyxl  # noqa: E402
import requests  # noqa: E402
import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "pokemon" / "source"
XLSX = SOURCE_DIR / "pokemon_bulk_catalogue.xlsx"
OVERRIDES = SOURCE_DIR / "set_overrides.yml"
CACHE_DIR = ROOT / "pokemon" / ".cache"
DATA_DIR = ROOT / "_data" / "pokemon"
PAGES_DIR = ROOT / "pokemon-tcg"

TCGCSV = "https://tcgcsv.com/tcgplayer/3"
TCGDEX = "https://api.tcgdex.net/v2/en"

# Order here is also the display order of variants for the same card number.
VARIANTS = {
    "normal": "Normal",
    "holo": "Holo",
    "reverse": "Reverse",
    "pokeball": "Poké Ball",
    "masterball": "Master Ball",
    "friendball": "Friend Ball",
    "loveball": "Love Ball",
    "quickball": "Quick Ball",
    "duskball": "Dusk Ball",
    "energysymbol": "Energy Symbol",
    "rocket": "Team Rocket",
}

# TCGplayer price subTypeName of the plain product -> variant
SUBTYPES = {
    "Normal": "normal",
    "Holofoil": "holo",
    "Reverse Holofoil": "reverse",
}

# Bracketed label in a TCGplayer product name -> patterned-reverse variant
PATTERNS = [
    (re.compile(r"^pok[eé] ?ball( pattern)?$", re.I), "pokeball"),
    (re.compile(r"^master ?ball( pattern)?$", re.I), "masterball"),
    (re.compile(r"^friend ?ball( pattern)?$", re.I), "friendball"),
    (re.compile(r"^love ?ball( pattern)?$", re.I), "loveball"),
    (re.compile(r"^quick ?ball( pattern)?$", re.I), "quickball"),
    (re.compile(r"^dusk ?ball( pattern)?$", re.I), "duskball"),
    (re.compile(r"^energy symbol( pattern)?$", re.I), "energysymbol"),
    (re.compile(r"^(team )?rocket( pattern)?$", re.I), "rocket"),
]

session = requests.Session()
session.headers["User-Agent"] = "camattelaer.github.io pokemon catalogue builder"


# ---------------------------------------------------------------- helpers

def get_json(url, cache_name, refresh=False):
    """GET url as JSON, cached in pokemon/.cache/<cache_name>.json."""
    path = CACHE_DIR / f"{cache_name}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    for attempt in range(3):
        try:
            resp = session.get(url, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            break
        except requests.RequestException as exc:
            if attempt == 2:
                raise
            print(f"  retrying {url} ({exc})", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return data


def fold(text):
    """Lowercase, strip accents and punctuation, collapse whitespace."""
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    text = text.lower().replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def slugify(text):
    return fold(text).replace(" ", "-")


def number_key(raw):
    """Canonical number for matching: '025/217' -> '25', 'TG05/TG30' -> 'TG5'."""
    raw = str(raw).strip().split("/")[0].strip().upper()
    if raw.endswith(".0") and raw[:-2].isdigit():  # xlsx numeric cells
        raw = raw[:-2]
    m = re.fullmatch(r"([A-Z-]*)0*(\d+)([A-Z]*)", raw)
    if m:
        return f"{m.group(1)}{m.group(2)}{m.group(3)}"
    return raw


def number_sort(key):
    """Plain numbers first in numeric order, then prefixed ones (TG, GG, SV...)."""
    m = re.fullmatch(r"([A-Z-]*)(\d+)([A-Z]*)", key)
    if not m:
        return (2, key, 0, "")
    prefix, digits, suffix = m.groups()
    return (0 if not prefix else 1, prefix, int(digits), suffix)


def strip_group_prefix(name):
    """'SV: Prismatic Evolutions' -> 'Prismatic Evolutions', 'SM - Lost Thunder' -> 'Lost Thunder'."""
    return re.sub(r"^[A-Za-z0-9&.]+(\s*:\s*|\s+-\s+)", "", name).strip()


def product_number(product):
    for field in product.get("extendedData", []):
        if field["name"] == "Number":
            return field["value"]
    return None


def clean_card_name(name):
    name = re.sub(r"\s*\([^)]*\)", "", name)
    name = re.sub(r"\s+-\s+[A-Z]*\d+[A-Z]*(/[A-Z]*\d+)?$", "", name)
    return name.strip()


# ---------------------------------------------------------------- inputs

def read_catalogue():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["Catalogue"]
    rows = ws.iter_rows(values_only=True)
    header = [str(h).strip().lower() if h is not None else "" for h in next(rows)]
    col = {name: header.index(name) for name in ("set_name", "number", "variant", "qty")}

    owned = defaultdict(int)  # (set_name, number_key, variant) -> qty
    rows_of = defaultdict(list)  # same key -> xlsx row numbers, for the report
    problems = []
    for rownum, row in enumerate(rows, start=2):
        set_name, number, variant, qty = (row[col[c]] if col[c] < len(row) else None
                                          for c in ("set_name", "number", "variant", "qty"))
        if all(v in (None, "") for v in (set_name, number, variant, qty)):
            continue
        set_name = str(set_name or "").strip()
        variant = str(variant or "").strip().lower()
        if not set_name or number in (None, ""):
            problems.append(f"row {rownum}: missing set_name or number")
            continue
        if variant not in VARIANTS:
            problems.append(f"row {rownum}: {set_name} #{number}: unknown variant '{variant}'")
            continue
        try:
            qty = int(qty) if qty not in (None, "") else 1
        except (TypeError, ValueError):
            problems.append(f"row {rownum}: {set_name} #{number}: qty '{qty}' is not a number")
            continue
        if qty <= 0:
            continue
        owned[(set_name, number_key(number), variant)] += qty
        rows_of[(set_name, number_key(number), variant)].append(rownum)

    # Lists sheet: fallback series / release date per set name
    lists = {}
    if "Lists" in wb.sheetnames:
        for row in wb["Lists"].iter_rows(min_row=2, values_only=True):
            if row and row[0]:
                lists[str(row[0]).strip()] = {
                    "series": row[1] if len(row) > 1 else None,
                    "release_date": str(row[2])[:10] if len(row) > 2 and row[2] else None,
                }
    wb.close()
    return owned, rows_of, lists, problems


def read_overrides():
    if not OVERRIDES.exists():
        return {}
    return yaml.safe_load(OVERRIDES.read_text()) or {}


# ---------------------------------------------------------------- matching

class Catalogues:
    def __init__(self, refresh):
        self.refresh = refresh
        self._load(refresh)

    def _load(self, refresh):
        self.tcgdex_sets = get_json(f"{TCGDEX}/sets", "tcgdex_sets", refresh)
        self.groups = get_json(f"{TCGCSV}/groups", "tcgcsv_groups", refresh)["results"]
        self.loaded_fresh = refresh

    def reload_once(self):
        """Cached lists may predate a new set: refetch them once on a miss."""
        if self.loaded_fresh:
            return False
        print("  (refreshing cached set lists)")
        self._load(True)
        return True

    def tcgdex_detail(self, set_id):
        return get_json(f"{TCGDEX}/sets/{set_id}", f"tcgdex_set_{set_id}", self.refresh)

    def match_tcgdex(self, name, override):
        if override:
            return next((s for s in self.tcgdex_sets if s["id"] == str(override)), None), "override"
        exact = [s for s in self.tcgdex_sets if fold(s["name"]) == fold(name)]
        if len(exact) == 1:
            return exact[0], "exact"
        # xlsx set names come from TCGdex, so only accept a very close fuzzy match
        names = {fold(s["name"]): s for s in self.tcgdex_sets}
        close = difflib.get_close_matches(fold(name), names, n=1, cutoff=0.9)
        return (names[close[0]], "fuzzy") if close else (None, None)

    def match_group(self, name, release_date, override):
        if override:
            return next((g for g in self.groups if g["groupId"] == int(override)), None), "override"
        target = fold(name)
        exact = [g for g in self.groups if fold(strip_group_prefix(g["name"])) == target]
        if len(exact) == 1:
            return exact[0], "exact"

        scored = []
        for g in self.groups:
            cand = fold(strip_group_prefix(g["name"]))
            score = difflib.SequenceMatcher(None, target, cand).ratio()
            if target and re.search(rf"\b{re.escape(target)}\b", cand):
                score += 0.15
            if release_date and g.get("publishedOn"):
                try:
                    days = abs((date.fromisoformat(g["publishedOn"][:10])
                                - date.fromisoformat(release_date)).days)
                    if days <= 21:
                        score += 0.15
                except ValueError:
                    pass
            scored.append((score, g))
        scored.sort(key=lambda s: -s[0])
        if scored and scored[0][0] >= 0.85 and (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.05):
            return scored[0][1], "fuzzy"
        return None, None

    def subset_groups(self, group, override):
        """TCGplayer splits Trainer Gallery, Galarian Gallery, Shiny Vault and Radiant
        Collection subsets into their own groups; TCGdex keeps them in the main set."""
        if override is not None:
            ids = {int(i) for i in override}
            return [g for g in self.groups if g["groupId"] in ids]
        pattern = re.compile(re.escape(group["name"]) +
                             r"(\s+Trainer Gallery|:\s*(Galarian Gallery|Shiny Vault|Radiant Collection))$")
        return [g for g in self.groups if pattern.match(g["name"])]


# ---------------------------------------------------------------- set build

def check_images(urls, refresh):
    """url -> whether the CDN serves it. Cached in pokemon/.cache/image_status.json."""
    path = CACHE_DIR / "image_status.json"
    status = {} if refresh or not path.exists() else json.loads(path.read_text())

    def probe(url):
        try:
            resp = session.head(url, timeout=15, allow_redirects=True)
            ok = resp.ok and resp.headers.get("Content-Type", "").startswith("image/")
            return url, ok
        except requests.RequestException:
            return url, None  # network trouble: don't cache, assume fine for now

    todo = [u for u in urls if u not in status]
    if todo:
        print(f"  checking {len(todo)} image(s)...")
        with ThreadPoolExecutor(max_workers=16) as pool:
            for url, ok in pool.map(probe, todo):
                if ok is not None:
                    status[url] = ok
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(status))
    return {u: status.get(u, True) for u in urls}


def build_card_list(group_ids, refresh):
    """Every card + variant in the given TCGplayer groups, keyed by (number_key, variant)."""
    products, subtypes = [], defaultdict(set)
    for group_id in group_ids:
        products += get_json(f"{TCGCSV}/{group_id}/products", f"tcgcsv_{group_id}_products", refresh)["results"]
        for p in get_json(f"{TCGCSV}/{group_id}/prices", f"tcgcsv_{group_id}_prices", refresh)["results"]:
            subtypes[p["productId"]].add(p["subTypeName"])

    # Sort products into plain ones (variants come from price subtypes), ball/energy
    # pattern reverses, and other labels. Labels like "(Full Art)" or "(Secret)" in
    # older sets are separate cards with their own number; labels on a number that
    # already has a plain product ("(Prerelease)", stamps, ...) are skipped.
    plain, patterned, labelled = [], [], []
    for prod in products:
        raw_number = product_number(prod)
        if not raw_number:
            continue  # sealed product
        labels = [l.strip() for l in re.findall(r"\(([^)]*)\)", prod["name"])]
        variant = next((v for label in labels for rx, v in PATTERNS if rx.match(label)), None)
        entry = (prod, raw_number, labels)
        if variant:
            patterned.append(entry + (variant,))
        elif labels:
            labelled.append(entry)
        else:
            plain.append(entry)

    plain_numbers = {number_key(n) for _, n, _ in plain}
    unrecognised = defaultdict(int)
    for prod, raw_number, labels in labelled:
        if number_key(raw_number) in plain_numbers:
            unrecognised[", ".join(labels)] += 1
        else:
            plain.append((prod, raw_number, labels))
            plain_numbers.add(number_key(raw_number))

    def card(prod, raw_number, variant):
        return {
            "number": raw_number.split("/")[0].strip(),
            "key": number_key(raw_number),
            "name": clean_card_name(prod["name"]),
            "image": (prod.get("imageUrl") or "").replace("_200w.", "_400w.") if prod.get("imageCount") else None,
            "url": prod.get("url"),
            "product_id": prod["productId"],
            "variant": variant,
        }

    cards = {}
    for prod, raw_number, _ in plain:
        found = subtypes.get(prod["productId"], set())
        variants = [SUBTYPES[s] for s in found if s in SUBTYPES] or ["normal"]  # unpriced: assume plain print
        for variant in variants:
            cards.setdefault((number_key(raw_number), variant), card(prod, raw_number, variant))
    for prod, raw_number, _, variant in patterned:
        cards.setdefault((number_key(raw_number), variant), card(prod, raw_number, variant))

    # TCGplayer sometimes lists an image the CDN refuses to serve (403), so check.
    ok = check_images({c["image"] for c in cards.values() if c["image"]}, refresh)
    for c in cards.values():
        if c["image"] and not ok[c["image"]]:
            c["image"] = None

    # Products without a working picture (often new pattern reverses) borrow the
    # image of another print of the same number; the variant badge tells them apart.
    # Every card also gets that plain image as a browser-side fallback.
    by_number = defaultdict(list)
    for (key, variant), card in cards.items():
        if card["image"]:
            by_number[key].append((list(VARIANTS).index(variant), card["image"]))
    for (key, _), card in cards.items():
        plain = min(by_number[key])[1] if by_number[key] else None
        if not card["image"] and plain:
            card["image"] = plain
            card["image_borrowed"] = True
        if plain and plain != card["image"]:
            card["image_fallback"] = plain

    return cards, dict(unrecognised)


def write_stub(slug, name):
    PAGES_DIR.mkdir(exist_ok=True)
    (PAGES_DIR / f"{slug}.md").write_text(
        "---\n"
        "# Generated by pokemon/build_catalogue.py; do not edit by hand.\n"
        "generated: true\n"
        "layout: pokemon-set\n"
        f"title: {json.dumps(name, ensure_ascii=False)}\n"
        f"set_slug: {json.dumps(slug)}\n"
        f"permalink: /pokemon-tcg/{slug}/\n"
        "---\n"
    )


def remove_stale(slugs):
    for path in PAGES_DIR.glob("*.md"):
        if path.stem not in slugs and "\ngenerated: true\n" in path.read_text():
            path.unlink()
            print(f"  removed stale page {path.relative_to(ROOT)}")
    for path in DATA_DIR.glob("*.json"):
        if path.stem != "sets" and path.stem not in slugs:
            path.unlink()
            print(f"  removed stale data {path.relative_to(ROOT)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--refresh", action="store_true", help="ignore the API cache and refetch everything")
    args = parser.parse_args()

    owned, rows_of, lists, report = read_catalogue()

    def rows(*key):
        nums = rows_of[key]
        return ("row " if len(nums) == 1 else "rows ") + ", ".join(map(str, nums))
    overrides = read_overrides()
    cats = Catalogues(args.refresh)

    by_set = defaultdict(dict)
    for (set_name, key, variant), qty in owned.items():
        by_set[set_name][(key, variant)] = qty

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    summaries = []
    for set_name in sorted(by_set):
        print(f"• {set_name}")
        ov = overrides.get(set_name) or {}

        tset, how = cats.match_tcgdex(set_name, ov.get("tcgdex"))
        if not tset and cats.reload_once():
            tset, how = cats.match_tcgdex(set_name, ov.get("tcgdex"))
        detail = cats.tcgdex_detail(tset["id"]) if tset else {}
        if tset and how != "exact":
            print(f"  TCGdex: {how} match -> {tset['name']} ({tset['id']})")

        fallback = lists.get(set_name, {})
        release_date = detail.get("releaseDate") or fallback.get("release_date")
        series = (detail.get("serie") or {}).get("name") or fallback.get("series") or "Other"

        group, how = cats.match_group(set_name, release_date, ov.get("tcgplayer"))
        if not group and cats.reload_once():
            group, how = cats.match_group(set_name, release_date, ov.get("tcgplayer"))
        if not group:
            n = sum(by_set[set_name].values())
            report.append(f"{set_name}: no TCGplayer group found ({n} cards skipped); "
                          f"add a 'tcgplayer: <groupId>' entry to {OVERRIDES.relative_to(ROOT)}")
            continue
        if how != "exact":
            print(f"  TCGplayer: {how} match -> {group['name']} ({group['groupId']})")

        extra = cats.subset_groups(group, ov.get("tcgplayer_extra"))
        for g in extra:
            print(f"  TCGplayer: + subset {g['name']} ({g['groupId']})")
        cards, unrecognised = build_card_list([group["groupId"]] + [g["groupId"] for g in extra], args.refresh)
        for label, n in sorted(unrecognised.items()):
            print(f"  note: skipped {n} product(s) labelled '({label})' (duplicate of a plain card number)")

        numbers = {k for k, _ in cards}
        for (key, variant), qty in sorted(by_set[set_name].items(), key=lambda kv: number_sort(kv[0][0])):
            if (key, variant) in cards:
                cards[(key, variant)]["qty"] = qty
            elif key in numbers:
                have = sorted({v for k, v in cards if k == key}, key=list(VARIANTS).index)
                report.append(f"{rows(set_name, key, variant)}: {set_name} #{key}: no '{variant}' variant on TCGplayer "
                              f"(known: {', '.join(have)}); qty {qty} skipped")
            else:
                report.append(f"{rows(set_name, key, variant)}: {set_name} #{key} ({variant}): card number not found in "
                              f"'{group['name']}'; qty {qty} skipped")

        order = list(VARIANTS)
        card_list = sorted(cards.values(), key=lambda c: (number_sort(c["key"]), order.index(c["variant"])))
        for c in card_list:
            c["qty"] = c.get("qty", 0)
            c["variant_label"] = VARIANTS[c["variant"]]
            del c["key"]

        slug = slugify(set_name)
        logo = f"{detail['logo']}.png" if detail.get("logo") else None
        summary = {
            "slug": slug,
            "name": set_name,
            "series": series,
            "release_date": release_date,
            "logo": logo,
            "tcgdex_id": tset["id"] if tset else None,
            "tcgplayer_group_id": group["groupId"],
            "tcgplayer_group_name": group["name"],
            "owned_count": sum(1 for c in card_list if c["qty"] > 0),
            "total_count": len(card_list),
            "owned_qty": sum(c["qty"] for c in card_list),
        }
        summaries.append(summary)
        (DATA_DIR / f"{slug}.json").write_text(
            json.dumps(dict(summary, cards=card_list), ensure_ascii=False, indent=1) + "\n", encoding="utf_8")
        write_stub(slug, set_name)

    # Newest first; Liquid's group_by keeps this order, so series are ordered by their newest set.
    summaries.sort(key=lambda s: (s["release_date"] or "", s["name"]), reverse=True)
    (DATA_DIR / "sets.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=1) + "\n", encoding="utf_8")
    remove_stale({s["slug"] for s in summaries})

    print(f"\nWrote {len(summaries)} set(s) to {DATA_DIR.relative_to(ROOT)}/")
    if report:
        print(f"\n{len(report)} problem(s) — these xlsx rows are NOT on the site:")
        for line in report:
            print(f"  - {line}")
        sys.exit(1)
    print("All xlsx rows matched.")


if __name__ == "__main__":
    main()
