"""Drawing helpers for printable card PDFs: card-sized placeholders, card pictures,
tables with checkboxes, rarity abbreviations.

A library only (no command of its own): used by masterset_placeholders.py and
masterset_shopping.py. Placeholder lists always come from a master set in the private
pokemon_mastersets.xlsx, never from the public bulk catalogue (a list built from bulk
doesn't know which cards are in a binder).
"""


import hashlib
import io
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_catalogue as bc  # noqa: E402  (also silences openpyxl/urllib3 warnings)

import requests  # noqa: E402
from PIL import Image, ImageOps  # noqa: E402
from reportlab.lib.pagesizes import landscape  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.lib.utils import ImageReader  # noqa: E402
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
    rarity = card_rarity(card, detail)
    if not above_limit(card, limit) or not rarity:
        return card["variant_label"].upper(), VARIANT_COLOURS.get(card["variant"], DEFAULT_BADGE)
    label = rarity.upper()
    if card["variant"] not in ("holo", "normal") or card.get("deck"):
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
    """[TCGdex card or None] for each card, matched on card number; cards of a set numbered
    as the original prints carry their TCGdex number (tcgdex_local) from build_catalogue."""
    ids = {bc.number_key(c["localId"]): c["id"] for c in set_detail.get("cards", [])}
    card_ids = [ids.get(bc.number_key(c.get("tcgdex_local") or c["number"])) for c in cards]
    wanted = {i for i in card_ids if i}
    with ThreadPoolExecutor(max_workers=8) as pool:
        found = dict(zip(wanted, pool.map(lambda i: tcgdex_card(i, refresh), wanted)))
    return [found.get(i) for i in card_ids]


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


def card_rarity(card, detail):
    """TCGdex's rarity, else TCGplayer's (stored by build_catalogue). TCGdex sends the
    text 'None' for cards it has no rarity for (e.g. the 30th Classic Collection)."""
    rarity = (detail or {}).get("rarity")
    if not rarity or rarity.strip().lower() == "none":
        rarity = card.get("rarity")
    return rarity


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


