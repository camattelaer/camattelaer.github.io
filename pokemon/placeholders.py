#!/usr/bin/env python3
"""Print placeholder cards for the cards still missing from a set (master set hunting).

Reads the set's generated data (_data/pokemon/<slug>.json, so run
build_catalogue.py first) and writes a PDF of card-sized placeholders, 3 x 3 per
page in binder order: every card + variant with qty 0, each showing a faded
picture of the card, its name, number and variant.

The PDF ends with a landscape checklist: on the left the cards numbered up to
the set's official count (number, name, variant), on the right the ones above it
(number, name, rarity, Cardmarket market price and a target price).

  pokemon/placeholders/<slug>-missing.pdf

Usage:  python pokemon/placeholders.py --set TEF [--variants reverse,pokeball]
                                       [--all] [--color] [--no-images] [--paper letter]
                                       [--price avg7|avg30|avg1|trend] [--target-pct 90]
                                       [--no-checklist] [--refresh-prices]
"""

import argparse
import hashlib
import io
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_catalogue as bc  # noqa: E402  (also silences openpyxl/urllib3 warnings)

import requests  # noqa: E402
from PIL import Image, ImageOps  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape, letter  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.lib.utils import ImageReader, simpleSplit  # noqa: E402
from reportlab.pdfbase.pdfmetrics import stringWidth  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

OUT_DIR = bc.ROOT / "pokemon" / "placeholders"
IMAGE_CACHE = bc.CACHE_DIR / "images"

CARD_W, CARD_H = 63 * mm, 88 * mm  # standard Pokémon card
COLS, ROWS = 3, 3                  # one 9-pocket binder page per sheet
BAND_H = 21 * mm                   # label band at the bottom of each placeholder
FADE = 0.55                        # how far card pictures are washed out towards white
VARIANT_COLOURS = {                # badge colour per variant; others use the default
    "normal": (0.45, 0.45, 0.45),
    "holo": (0.80, 0.60, 0.05),
    "reverse": (0.15, 0.45, 0.75),
    "pokeball": (0.80, 0.15, 0.15),
    "masterball": (0.45, 0.20, 0.65),
    "rocket": (0.10, 0.10, 0.10),
}
DEFAULT_BADGE = (0.15, 0.55, 0.40)

# Prices: Cardmarket's price guide (EUR) as published per card by TCGdex
CARD_CACHE = bc.CACHE_DIR / "cards"
CARD_MAX_AGE = 12 * 3600  # seconds before a card's price is refetched
PRICE_BASES = {
    "avg7": "7-day average sell price",
    "avg30": "30-day average sell price",
    "avg1": "1-day average sell price",
    "trend": "price trend",
}
PRICE_FALLBACKS = ("avg7", "avg30", "trend", "avg")  # tried after the chosen basis
RARITY_ABBR = {
    "common": "C",
    "uncommon": "U",
    "rare": "R",
    "rare holo": "RH",
    "holo rare": "RH",
    "double rare": "RR",
    "ultra rare": "UR",
    "illustration rare": "IR",
    "special illustration rare": "SIR",
    "hyper rare": "HR",
    "ace spec rare": "ACE",
    "shiny rare": "SR",
    "shiny ultra rare": "SSR",
    "mega attack rare": "MAR",
    "mega hyper rare": "MHR",
    "black white rare": "BWR",
    "secret rare": "SecR",
}
RARITY_COLOURS = {  # badge colour per rarity (abbreviation) above the set limit
    "IR": (0.10, 0.55, 0.55),
    "SIR": (0.75, 0.35, 0.10),
    "UR": (0.35, 0.35, 0.50),
    "HR": (0.80, 0.60, 0.05),
    "MHR": (0.80, 0.60, 0.05),
    "MAR": (0.45, 0.20, 0.65),
    "ACE": (0.75, 0.15, 0.45),
}


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def above_limit(card, limit):
    """Numbered above the set's official count (secret rares), or not a plain number.
    Without a known limit every card counts as above it."""
    return not (limit and card["number"].isdigit() and int(card["number"]) <= limit)


# ---------------------------------------------------------------- finding the set

def tcgdex_detail(set_id):
    try:
        return bc.get_json(f"{bc.TCGDEX}/sets/{set_id}", f"tcgdex_set_{set_id}") if set_id else {}
    except requests.RequestException:
        return {}


def find_set(wanted):
    """Summary from sets.json, matched on slug, set name or official abbreviation."""
    sets_file = bc.DATA_DIR / "sets.json"
    if not sets_file.exists():
        fail(f"{sets_file.relative_to(bc.ROOT)} not found; run build_catalogue.py first")
    sets = json.loads(sets_file.read_text(encoding="utf_8"))

    want = wanted.strip()
    for s in sets:
        if want.lower() in (s["slug"], s["name"].lower()) or bc.slugify(want) == s["slug"]:
            return s

    groups = {}
    try:
        groups = {g["groupId"]: g for g in bc.Catalogues(False).groups}
    except requests.RequestException:
        pass
    hits = []
    for s in sets:
        abbrs = {(tcgdex_detail(s["tcgdex_id"]).get("abbreviation") or {}).get("official"),
                 (groups.get(s["tcgplayer_group_id"]) or {}).get("abbreviation")}
        if want.upper() in {a.upper() for a in abbrs if a}:
            hits.append(s)
    if len(hits) == 1:
        return hits[0]
    if hits:
        fail(f"'{wanted}' matches several sets ({', '.join(s['name'] for s in hits)}); use the full set name")
    fail(f"no set '{wanted}' in the catalogue. Sets: {', '.join(s['name'] for s in sets)}")


# ---------------------------------------------------------------- images

def cached_image(url):
    """Local copy of url in pokemon/.cache/images/, or None if it can't be fetched."""
    path = IMAGE_CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + Path(url).suffix)
    if path.exists():
        return path
    try:
        resp = bc.session.get(url, timeout=30)
        resp.raise_for_status()
        Image.open(io.BytesIO(resp.content)).verify()
    except Exception:  # network trouble or not an image: placeholder gets no picture
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    return path


def card_picture(card, colour):
    """ImageReader of the card's (faded) picture, trying the fallback print's too."""
    for url in (card.get("image"), card.get("image_fallback")):
        path = cached_image(url) if url else None
        if not path:
            continue
        img = Image.open(path).convert("RGB")
        if not colour:
            img = ImageOps.grayscale(img).convert("RGB")
        img = Image.blend(img, Image.new("RGB", img.size, "white"), FADE)
        return ImageReader(img)
    return None


# ---------------------------------------------------------------- drawing

def fit_text(text, font, size, max_width, min_size=6):
    """Largest font size <= size at which text fits, ellipsising if even min_size doesn't."""
    while size > min_size and stringWidth(text, font, size) > max_width:
        size -= 0.5
    while stringWidth(text, font, size) > max_width and len(text) > 1:
        text = text[:-2].rstrip() + "…"
    return text, size


def draw_placeholder(c, x, y, card, set_info, picture, badge):
    pad = 2.5 * mm
    # cut line
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.setLineWidth(0.3)
    c.setDash(2, 2)
    c.rect(x, y, CARD_W, CARD_H)
    c.setDash()

    # picture, scaled to fit above the band
    if picture:
        iw, ih = picture.getSize()
        avail_w, avail_h = CARD_W - 2 * pad, CARD_H - BAND_H - 2 * pad
        scale = min(avail_w / iw, avail_h / ih)
        w, h = iw * scale, ih * scale
        c.drawImage(picture, x + (CARD_W - w) / 2, y + BAND_H + pad + (avail_h - h) / 2, w, h)
    else:
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.setFont("Helvetica", 9)
        c.drawCentredString(x + CARD_W / 2, y + BAND_H + (CARD_H - BAND_H) / 2, "no picture available")

    # label band: name / number + set / variant badge
    inner = CARD_W - 2 * pad
    c.setFillColorRGB(0.1, 0.1, 0.1)
    name, size = fit_text(card["name"], "Helvetica-Bold", 11, inner)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x + pad, y + BAND_H - pad - size * 0.8, name)

    total = f" / {set_info['official']}" if set_info.get("official") else ""
    line = f"#{card['number']}{total}  ·  {set_info['name']}"
    line, size = fit_text(line, "Helvetica", 8, inner)
    c.setFont("Helvetica", size)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(x + pad, y + BAND_H - pad - 11 - size, line)

    label, colour = badge
    label, size = fit_text(label, "Helvetica-Bold", 8, inner - 4 * mm)
    c.setFont("Helvetica-Bold", size)
    badge_w, badge_h = stringWidth(label, "Helvetica-Bold", size) + 4 * mm, 5 * mm
    c.setFillColorRGB(*colour)
    c.roundRect(x + pad, y + pad, badge_w, badge_h, 1.5 * mm, stroke=0, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(x + pad + 2 * mm, y + pad + 1.6 * mm, label)


def card_badge(card, detail, limit):
    """(label, colour) of a placeholder's badge: the variant for cards up to the set
    limit, the rarity (e.g. ILLUSTRATION RARE) for the ones above it."""
    rarity = (detail or {}).get("rarity")
    if not above_limit(card, limit) or not rarity:
        return card["variant_label"].upper(), VARIANT_COLOURS.get(card["variant"], DEFAULT_BADGE)
    label = rarity.upper()
    if card["variant"] not in ("holo", "normal"):
        label += f" · {card['variant_label'].upper()}"
    return label, RARITY_COLOURS.get(rarity_abbr(rarity), DEFAULT_BADGE)


def write_pdf(path, cards, set_info, paper, pictures, badges, checklist=None):
    """checklist: None, or a function(canvas) drawing the landscape checklist page(s)."""
    page_w, page_h = paper
    margin_x = (page_w - COLS * CARD_W) / 2
    margin_y = (page_h - ROWS * CARD_H) / 2
    c = canvas.Canvas(str(path), pagesize=paper)
    c.setTitle(f"{set_info['name']} placeholders")
    per_page = COLS * ROWS
    for i, card in enumerate(cards):
        slot = i % per_page
        if i and not slot:
            c.showPage()
        col, row = slot % COLS, slot // COLS
        draw_placeholder(c, margin_x + col * CARD_W, page_h - margin_y - (row + 1) * CARD_H,
                         card, set_info, pictures[i], badges[i])
    if checklist:
        c.showPage()
        c.setPageSize(landscape(paper))
        checklist(c)
    c.save()


# ---------------------------------------------------------------- prices + rarity

def tcgdex_card(card_id, refresh):
    """TCGdex card (rarity + Cardmarket pricing), cached for CARD_MAX_AGE.
    A stale copy is used when TCGdex can't be reached."""
    path = CARD_CACHE / f"{card_id}.json"
    fresh = path.exists() and time.time() - path.stat().st_mtime < CARD_MAX_AGE
    if fresh and not refresh:
        return json.loads(path.read_text(encoding="utf_8"))
    try:
        resp = bc.session.get(f"{bc.TCGDEX}/cards/{card_id}", timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return json.loads(path.read_text(encoding="utf_8")) if path.exists() else None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf_8")
    return data


def card_details(cards, set_detail, refresh):
    """[TCGdex card or None] for each card, matched on card number."""
    ids = {bc.number_key(c["localId"]): c["id"] for c in set_detail.get("cards", [])}
    wanted = {ids[k] for k in (bc.number_key(c["number"]) for c in cards) if k in ids}
    with ThreadPoolExecutor(max_workers=8) as pool:
        found = dict(zip(wanted, pool.map(lambda i: tcgdex_card(i, refresh), wanted)))
    return [found.get(ids.get(bc.number_key(c["number"]))) for c in cards]


def market_price(detail, variant, basis):
    """(price in EUR, field used, cardmarket 'updated' timestamp) or (None, None, None).
    Reverse holos use Cardmarket's separate reverse-holo ('-holo') prices."""
    cm = ((detail or {}).get("pricing") or {}).get("cardmarket") or {}
    suffix = "-holo" if variant == "reverse" else ""
    for field in (basis,) + tuple(f for f in PRICE_FALLBACKS if f != basis):
        value = cm.get(field + suffix)
        if value:
            return float(value), field, cm.get("updated")
    return None, None, None


def rarity_abbr(rarity):
    if not rarity:
        return "?"
    key = bc.fold(rarity)
    return RARITY_ABBR.get(key) or "".join(word[0].upper() for word in key.split())


def euro(value):
    return f"€{value:,.2f}" if value is not None else "–"


# ---------------------------------------------------------------- checklist page

CL_MARGIN = 12 * mm
CL_GAP = 8 * mm       # between the two halves (and between bulk sub-columns)
CL_ROW = 3.9 * mm
CL_FONT = 7.5
CL_HEAD = 16 * mm     # title + section heading
CL_FOOT_FONT = 6.5    # price note under the right half
CHECKED = object()    # table cell: ticked checkbox


def draw_table(c, x, y_top, width, columns, rows, shade_from=0):
    """columns: [(header, width or None for the flexible one, align)];
    rows: [[cell, ...]] where a cell of True draws a checkbox (CHECKED: a ticked one)."""
    flex = width - sum(w for _, w, _ in columns if w)
    widths = [w or flex for _, w, _ in columns]

    def cells(values, y, font):
        cx = x
        for (_, _, align), w, value in zip(columns, widths, values):
            if value is True or value is CHECKED:
                box = 2.6 * mm
                bx, by = cx + 0.3 * mm, y + (CL_ROW - box) / 2
                c.setStrokeColorRGB(0.35, 0.35, 0.35)
                c.setLineWidth(0.5)
                c.rect(bx, by, box, box)
                if value is CHECKED:
                    c.setLineWidth(0.9)
                    c.lines([(bx + 0.5 * mm, by + 1.3 * mm, bx + 1.1 * mm, by + 0.5 * mm),
                             (bx + 1.1 * mm, by + 0.5 * mm, bx + 2.3 * mm, by + 2.2 * mm)])
            elif value:
                text, size = fit_text(str(value), font, CL_FONT, w - 1.5 * mm)
                c.setFont(font, size)
                if align == "right":
                    c.drawRightString(cx + w - 0.8 * mm, y + 1.15 * mm, text)
                else:
                    c.drawString(cx + 0.8 * mm, y + 1.15 * mm, text)
            cx += w

    y = y_top - CL_ROW
    c.setFillColorRGB(0.1, 0.1, 0.1)
    cells([h for h, _, _ in columns], y, "Helvetica-Bold")
    c.setStrokeColorRGB(0.2, 0.2, 0.2)
    c.setLineWidth(0.6)
    c.line(x, y, x + width, y)
    for i, row in enumerate(rows):
        y -= CL_ROW
        bold = row and row[0] == "total"
        if bold:
            c.setLineWidth(0.6)
            c.setStrokeColorRGB(0.2, 0.2, 0.2)
            c.line(x, y + CL_ROW, x + width, y + CL_ROW)
            row = [None] + row[1:]
        elif (i + shade_from) % 2:
            c.setFillColorRGB(0.94, 0.94, 0.94)
            c.rect(x, y, width, CL_ROW, stroke=0, fill=1)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        cells(row, y, "Helvetica-Bold" if bold else "Helvetica")


def checklist_drawer(cards, set_info, details, basis, target_pct, missing_only):
    """function(canvas) drawing the checklist on as many landscape pages as needed."""
    limit = set_info.get("official")
    bulk = [[True, c["number"], c["name"], c["variant_label"]] for c in cards if not above_limit(c, limit)]
    secret, totals, used, updated, unpriced = [], [0.0, 0.0], set(), set(), 0
    for card, detail in zip(cards, details):
        if not above_limit(card, limit):
            continue
        price, field, stamp = market_price(detail, card["variant"], basis)
        rarity = rarity_abbr((detail or {}).get("rarity")) if detail else "?"
        if card["variant"] not in ("holo", "normal"):
            rarity += f" · {card['variant_label']}"
        target = round(price * target_pct / 100, 2) if price is not None else None
        if price is None:
            unpriced += 1
        else:
            totals[0] += price
            totals[1] += target
            used.add(field)
            if stamp:
                updated.add(stamp[:10])
        flag = "*" if field and field != basis else ""
        secret.append([True, card["number"], card["name"], rarity, euro(price) + flag, euro(target)])
    if secret:
        secret.append(["total", "", f"Total ({len(secret)} cards)", "", euro(totals[0]), euro(totals[1])])

    bulk_cols = [("", 4 * mm, "left"), ("#", 9 * mm, "left"), ("Name", None, "left"),
                 ("Variant", 17 * mm, "left")]
    secret_cols = [("", 4 * mm, "left"), ("#", 9 * mm, "left"), ("Name", None, "left"),
                   ("Rarity", 20 * mm, "left"), ("Market", 15 * mm, "right"),
                   (f"Target ({target_pct:g}%)", 18 * mm, "right")]

    note = (f"Market price: Cardmarket {PRICE_BASES[basis]} in EUR, from Cardmarket's price guide as "
            f"published per card by TCGdex (api.tcgdex.net)")
    if updated:
        dates = [f"{date.fromisoformat(d):%d %b %Y}" for d in sorted(updated)]
        note += f", price data of {dates[0] if len(dates) == 1 else dates[0] + ' to ' + dates[-1]}"
    note += f"; retrieved {date.today():%d %b %Y}. Reverse holos use Cardmarket's reverse-holo price."
    note2 = f"Target = {target_pct:g}% of market price."
    fallbacks = sorted(used - {basis})
    if fallbacks:
        note2 += (f" * no {PRICE_BASES[basis]} available; "
                  f"{' / '.join(PRICE_BASES.get(f, f) for f in fallbacks)} used instead.")
    if unpriced:
        note2 += f" {unpriced} card(s) without a Cardmarket price (–)."

    def draw(c):
        page_w, page_h = c._pagesize
        half_w = (page_w - 2 * CL_MARGIN - CL_GAP) / 2
        table_top = page_h - CL_MARGIN - CL_HEAD
        right_x = CL_MARGIN + half_w + CL_GAP
        # price note: wrapped to the right half, which gives up that height; the left half doesn't
        foot_lines = [line for text in (note, note2) for line in simpleSplit(text, "Helvetica", CL_FOOT_FONT, half_w)]
        foot_h = len(foot_lines) * CL_FOOT_FONT * 1.25 + 3 * mm
        left_rows = int((table_top - CL_MARGIN) // CL_ROW) - 1  # minus header row
        right_rows = int((table_top - CL_MARGIN - foot_h) // CL_ROW) - 1
        bulk_split = len(bulk) > left_rows  # two narrower sub-columns in the left half
        sub_w = (half_w - CL_GAP / 2) / 2
        bulk_frames = ([(CL_MARGIN, sub_w), (CL_MARGIN + sub_w + CL_GAP / 2, sub_w)]
                       if bulk_split else [(CL_MARGIN, half_w)])
        pages = max(-(-len(bulk) // (left_rows * len(bulk_frames))), -(-len(secret) // right_rows), 1)
        title = f"{set_info['name']}: {'missing cards' if missing_only else 'checklist'}"

        b = s = 0
        for page in range(pages):
            if page:
                c.showPage()
            c.setFillColorRGB(0.1, 0.1, 0.1)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(CL_MARGIN, page_h - CL_MARGIN - 4 * mm, title + (" (continued)" if page else ""))
            c.setFont("Helvetica", 8)
            c.drawRightString(page_w - CL_MARGIN, page_h - CL_MARGIN - 4 * mm,
                              f"{len(cards)} card{'s' if len(cards) != 1 else ''} · set limit "
                              f"{limit or '?'} · {date.today():%d %b %Y}"
                              + (f" · page {page + 1}/{pages}" if pages > 1 else ""))
            heading_y = page_h - CL_MARGIN - CL_HEAD + 2.5 * mm
            c.setFont("Helvetica-Bold", 9)
            c.drawString(CL_MARGIN, heading_y, f"Up to #{limit} ({len(bulk)})" if limit else
                         "Set limit unknown: all cards on the right")
            c.drawString(right_x, heading_y,
                         f"Above #{limit} ({len(secret) - 1 if secret else 0})" if limit else
                         f"All cards ({len(secret) - 1 if secret else 0})")
            c.setStrokeColorRGB(0.75, 0.75, 0.75)
            c.setLineWidth(0.4)
            mid = CL_MARGIN + half_w + CL_GAP / 2
            c.line(mid, CL_MARGIN, mid, table_top)

            for x, w in bulk_frames:
                chunk = bulk[b:b + left_rows]
                if chunk:
                    draw_table(c, x, table_top, w, bulk_cols, chunk, b)
                b += len(chunk)
            chunk = secret[s:s + right_rows]
            if chunk:
                draw_table(c, right_x, table_top, half_w, secret_cols, chunk, s)
            s += len(chunk)

            c.setFont("Helvetica", CL_FOOT_FONT)
            c.setFillColorRGB(0.35, 0.35, 0.35)
            for i, line in enumerate(reversed(foot_lines)):
                c.drawString(right_x, CL_MARGIN + i * CL_FOOT_FONT * 1.25, line)

    return draw


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", required=True, metavar="SET",
                        help="official abbreviation (e.g. TEF), set name or slug")
    parser.add_argument("--variants", metavar="LIST",
                        help=f"only these variants, comma-separated ({', '.join(bc.VARIANTS)})")
    parser.add_argument("--all", action="store_true", help="every card of the set, owned or not")
    parser.add_argument("--color", action="store_true", help="keep card pictures in colour")
    parser.add_argument("--no-images", action="store_true", help="text-only placeholders, no downloads")
    parser.add_argument("--paper", choices=("a4", "letter"), default="a4")
    parser.add_argument("--out", type=Path, help=f"output PDF (default: {OUT_DIR.relative_to(bc.ROOT)}/<set>-missing.pdf)")
    parser.add_argument("--price", choices=list(PRICE_BASES), default="avg7",
                        help="Cardmarket price used as market price (default: avg7, the 7-day average)")
    parser.add_argument("--target-pct", type=float, default=90, metavar="PCT",
                        help="target price as a percentage of the market price (default: 90)")
    parser.add_argument("--no-checklist", action="store_true", help="leave out the landscape checklist page")
    parser.add_argument("--refresh-prices", action="store_true",
                        help=f"refetch prices even if cached less than {CARD_MAX_AGE // 3600} h ago")
    args = parser.parse_args()

    summary = find_set(args.set)
    data_file = bc.DATA_DIR / f"{summary['slug']}.json"
    data = json.loads(data_file.read_text(encoding="utf_8"))

    cards = data["cards"] if args.all else [c for c in data["cards"] if c["qty"] == 0]
    if args.variants:
        wanted = {v.strip().lower() for v in args.variants.split(",") if v.strip()}
        unknown = wanted - set(bc.VARIANTS)
        if unknown:
            fail(f"unknown variant(s): {', '.join(sorted(unknown))}; choose from {', '.join(bc.VARIANTS)}")
        cards = [c for c in cards if c["variant"] in wanted]
    if not cards:
        print(f"{data['name']}: nothing missing{' for those variants' if args.variants else ''}. Master set complete!")
        return

    detail = tcgdex_detail(data.get("tcgdex_id"))
    set_info = {"name": data["name"], "official": (detail.get("cardCount") or {}).get("official")}

    if args.no_images:
        pictures = [None] * len(cards)
    else:
        print(f"Fetching {len(cards)} card picture(s) (cached in {IMAGE_CACHE.relative_to(bc.ROOT)}/)...")
        with ThreadPoolExecutor(max_workers=8) as pool:
            pictures = list(pool.map(lambda card: card_picture(card, args.color), cards))
        if None in pictures:
            print(f"  {pictures.count(None)} picture(s) unavailable; those placeholders are text-only")

    # rarity (badges + checklist) and prices (checklist) for the cards above the set limit
    limit = set_info["official"]
    secret = [c for c in cards if above_limit(c, limit)]
    details = [None] * len(cards)
    if secret:
        print(f"Fetching rarity + Cardmarket prices for {len(secret)} card(s) above #{limit} (via TCGdex)...")
        by_id = {id(c): d for c, d in zip(secret, card_details(secret, detail, args.refresh_prices))}
        details = [by_id.get(id(c)) for c in cards]
    badges = [card_badge(c, d, limit) for c, d in zip(cards, details)]

    checklist = None
    if not args.no_checklist:
        checklist = checklist_drawer(cards, set_info, details, args.price, args.target_pct, not args.all)

    suffix = "all" if args.all else "missing"
    out = args.out or OUT_DIR / f"{summary['slug']}-{suffix}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        write_pdf(out, cards, set_info, A4 if args.paper == "a4" else letter, pictures, badges, checklist)
    except PermissionError:
        fail(f"can't write {out}; is it open in a PDF viewer?")

    pages = -(-len(cards) // (COLS * ROWS))
    try:
        shown = out.resolve().relative_to(bc.ROOT)
    except ValueError:
        shown = out
    print(f"{data['name']}: {len(cards)} placeholder(s) on {pages} page(s) -> {shown}")
    print("Print at 100% / actual size (not 'fit to page') so they match real cards.")


if __name__ == "__main__":
    main()
