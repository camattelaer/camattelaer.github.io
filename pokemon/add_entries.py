#!/usr/bin/env python3
# Run from the repo root (the folder containing pokemon/); close the xlsx files in Excel first.
#
# Windows (PowerShell / VS Code terminal):
#   pokemon\.venv\Scripts\python.exe pokemon\add_entries.py --set ASC --dry-run
#   pokemon\.venv\Scripts\python.exe pokemon\add_entries.py --set ASC
#   pokemon\.venv\Scripts\python.exe pokemon\build_catalogue.py      # then rebuild the site data
# macOS:
#   pokemon/.venv/bin/python pokemon/add_entries.py --set ASC
#   pokemon/.venv/bin/python pokemon/build_catalogue.py
#
# Replace ASC with the set's abbreviation (TEF, PRE, ...). First time on a machine:
# see the venv setup at the top of build_catalogue.py.
"""Merge pokemon/source/new_entries.xlsx into one set's tab of the bulk catalogue.

Each row of new_entries.xlsx (number, variant, qty) is looked up on the tab of
the set given with --set (its official abbreviation, e.g. ASC or TEF):

  - same number + variant already on the tab -> its qty is increased by the new qty
                                                (--replace: set to the new qty)
  - not there yet                            -> appended as a new row

A set without a tab yet gets one, copied from the Template tab. The catalogue is
backed up to pokemon/.cache/backups/ first, and new_entries.xlsx is emptied
afterwards so the same cards can't be added twice (--keep leaves it as is).

Usage:  python pokemon/add_entries.py --set ASC [--replace] [--keep] [--dry-run]
"""

import argparse
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from copy import copy
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_catalogue as bc  # noqa: E402  (also silences openpyxl/urllib3 warnings)

import openpyxl  # noqa: E402
from openpyxl.styles import Font, PatternFill  # noqa: E402
from openpyxl.worksheet.datavalidation import DataValidation  # noqa: E402

NEW_ENTRIES = bc.SOURCE_DIR / "new_entries.xlsx"
BACKUP_DIR = bc.CACHE_DIR / "backups"
HEADERS = ("number", "variant", "qty")
FIRST_ROW = 4  # catalogue tabs: set_name in B1, headers in row 3, cards from row 4


def rel(path):
    """Path as shown to the user: relative to the repo when inside it."""
    try:
        return path.relative_to(bc.ROOT)
    except ValueError:
        return path


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def clean_number(raw):
    """'025/217' -> '25', 25.0 -> '25', 'tg05' -> 'TG05' (text as typed otherwise)."""
    if isinstance(raw, float) and raw.is_integer():
        raw = int(raw)
    text = str(raw).strip().split("/")[0].strip().upper()
    return str(int(text)) if text.isdigit() else text


def ensure_closed(*paths):
    """Excel on macOS doesn't lock files, so a save here would be lost (or
    clobbered) when Excel saves its open copy. Its ~$ owner file gives it away."""
    for path in paths:
        if (path.parent / f"~${path.name}").exists():
            fail(f"{path.name} is open in Excel; close it first")


def create_new_entries_file():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "New entries"
    ws.append(HEADERS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "A2"
    for col, width in zip("ABC", (12, 16, 8)):
        ws.column_dimensions[col].width = width
    fill = PatternFill("solid", fgColor="FFF9DB")  # same yellow as the catalogue
    for row in ws.iter_rows(min_row=2, max_row=500, max_col=3):
        for cell in row:
            cell.fill = fill
    variants = DataValidation(type="list", formula1='"' + ",".join(bc.VARIANTS) + '"', allow_blank=True)
    variants.add("B2:B500")
    qty = DataValidation(type="whole", operator="greaterThanOrEqual", formula1="1", allow_blank=True)
    qty.add("C2:C500")
    ws.add_data_validation(variants)
    ws.add_data_validation(qty)
    wb.save(NEW_ENTRIES)


def read_new_entries():
    """{(number_key, variant): (number, variant, qty)} plus the row numbers read."""
    wb = openpyxl.load_workbook(NEW_ENTRIES, data_only=True)
    ws = wb.worksheets[0]
    header = [str(c.value).strip().lower() if c.value is not None else "" for c in ws[1]]
    if not all(h in header for h in HEADERS):
        fail(f"{NEW_ENTRIES.name}: row 1 must be the headers number / variant / qty")
    col = {h: header.index(h) for h in HEADERS}

    entries, rows, problems = {}, [], []
    for rownum, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        number, variant, qty = (row[col[h]] if col[h] < len(row) else None for h in HEADERS)
        if all(v in (None, "") for v in (number, variant, qty)):
            continue
        rows.append(rownum)
        variant = str(variant or "").strip().lower()
        if number in (None, ""):
            problems.append(f"row {rownum}: missing number")
            continue
        if variant not in bc.VARIANTS:
            problems.append(f"row {rownum}: #{number}: unknown variant '{variant}'")
            continue
        try:
            qty = int(qty) if qty not in (None, "") else 1
        except (TypeError, ValueError):
            problems.append(f"row {rownum}: #{number}: qty '{qty}' is not a number")
            continue
        if qty <= 0:
            problems.append(f"row {rownum}: #{number}: qty must be 1 or more")
            continue
        number = clean_number(number)
        key = (bc.number_key(number), variant)
        if key in entries:  # same card twice in new_entries: add them up
            qty += entries[key][2]
        entries[key] = (number, variant, qty)

    if problems:
        fail(f"{NEW_ENTRIES.name} has problems, nothing was changed:\n  " + "\n  ".join(problems))
    return entries, rows


# ---------------------------------------------------------------- finding the tab

class SetLookup:
    """Official abbreviations per set name: TCGdex first, TCGplayer's as a fallback."""

    def __init__(self):
        self.cats = bc.Catalogues(False)
        self.overrides = bc.read_overrides()

    def abbreviations(self, set_name):
        ov = self.overrides.get(set_name) or {}
        found = set()
        tset, _ = self.cats.match_tcgdex(set_name, ov.get("tcgdex"))
        release_date = None
        if tset:
            detail = self.cats.tcgdex_detail(tset["id"])
            release_date = detail.get("releaseDate")
            abbr = (detail.get("abbreviation") or {}).get("official")
            if abbr:
                found.add(abbr.upper())
        group, _ = self.cats.match_group(set_name, release_date, ov.get("tcgplayer"))
        if group and group.get("abbreviation"):
            found.add(group["abbreviation"].upper())
        return found


def set_tabs(wb):
    """{tab title: set_name in B1} for every set tab that has a set name."""
    tabs = {}
    for ws in wb.worksheets:
        if ws.title in bc.NON_COLLECTION_SHEETS or ws.title == "Template":
            continue
        name = ws["B1"].value
        if name not in (None, ""):
            tabs[ws.title] = str(name).strip()
    return tabs


def find_set(wb, wanted, lookup):
    """(tab title or None, set_name). Matches an existing tab first, then any set
    in the Lists sheet (whose tab will be created)."""
    want = wanted.strip().upper()
    tabs = set_tabs(wb)

    # an exact set or tab name also works, e.g. --set "Ascended Heroes"
    for title, name in tabs.items():
        if want in (title.upper(), name.upper()):
            return title, name

    hits = [(title, name) for title, name in tabs.items() if want in lookup.abbreviations(name)]
    if len(hits) > 1:
        fail(f"'{wanted}' matches several tabs ({', '.join(t for t, _ in hits)}); "
             f"use the full set name, e.g. --set \"{hits[0][1]}\"")
    if hits:
        return hits[0]

    # no tab yet: look through every set in the Lists sheet (dropdown source)
    names = [str(r[0]).strip() for r in wb["Lists"].iter_rows(min_row=2, max_col=1, values_only=True) if r[0]]
    exact = [n for n in names if n.upper() == want]
    if exact:
        return None, exact[0]
    print("Looking up set abbreviations (slow only the first time)...")
    with ThreadPoolExecutor(max_workers=8) as pool:
        abbrs = list(pool.map(lookup.abbreviations, names))
    hits = [n for n, a in zip(names, abbrs) if want in a]
    if len(hits) > 1:
        fail(f"'{wanted}' matches several sets ({', '.join(hits)}); use the full set name instead")
    if not hits:
        known = ", ".join(f"{sorted(lookup.abbreviations(n)) or ['?']} {n}" for n in tabs.values())
        fail(f"no set with abbreviation '{wanted}'. Sets with a tab: {known or 'none'}")
    return None, hits[0]


def create_tab(wb, set_name):
    template = wb["Template"]
    ws = wb.copy_worksheet(template)  # copies cells, styles and column widths only
    title = "".join(ch for ch in set_name if ch not in "[]:*?/\\")[:31]
    if title in wb.sheetnames:
        title = title[:28] + " 2"
    ws.title = title
    ws["B1"] = set_name
    ws.freeze_panes = template.freeze_panes
    for dv in template.data_validations.dataValidation:
        new = copy(dv)
        new.sqref = copy(dv.sqref)
        ws.add_data_validation(new)
    wb.move_sheet(ws, offset=wb.index(wb["Lists"]) - wb.index(ws))  # keep Lists last
    return ws


# ---------------------------------------------------------------- merging

def merge(ws, entries, replace):
    existing = {}  # (number_key, variant) -> row
    last_row = FIRST_ROW - 1
    for row in ws.iter_rows(min_row=FIRST_ROW, max_col=3):
        number, variant, qty = (c.value for c in row)
        if all(v in (None, "") for v in (number, variant, qty)):
            continue
        last_row = row[0].row
        if number not in (None, "") and variant:
            key = (bc.number_key(clean_number(number)), str(variant).strip().lower())
            existing.setdefault(key, row[0].row)  # duplicates: update the first one

    changes = []
    for key, (number, variant, qty) in sorted(entries.items(), key=lambda kv: bc.number_sort(kv[0][0])):
        if key in existing:
            cell = ws.cell(existing[key], 3)
            try:
                old = int(cell.value) if cell.value not in (None, "") else 1  # blank counts as 1
            except (TypeError, ValueError):
                old = 0
            new = qty if replace else old + qty
            cell.value = new
            changes.append(f"  updated  row {existing[key]:>4}: #{number} {variant}  qty {old} -> {new}")
        else:
            last_row += 1
            ws.cell(last_row, 1, number)
            ws.cell(last_row, 2, variant)
            ws.cell(last_row, 3, qty)
            changes.append(f"  added    row {last_row:>4}: #{number} {variant}  qty {qty}")
    return changes


def clear_entries(rows):
    wb = openpyxl.load_workbook(NEW_ENTRIES)
    ws = wb.worksheets[0]
    for rownum in rows:
        for col in range(1, 4):
            ws.cell(rownum, col).value = None
    wb.save(NEW_ENTRIES)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--set", required=True, metavar="ABBR",
                        help="official set abbreviation, e.g. ASC or TEF (a full set name also works)")
    parser.add_argument("--replace", action="store_true",
                        help="set the qty of existing rows to the new qty instead of adding to it")
    parser.add_argument("--keep", action="store_true", help="don't empty new_entries.xlsx afterwards")
    parser.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    args = parser.parse_args()

    if not NEW_ENTRIES.exists():
        create_new_entries_file()
        print(f"Created {rel(NEW_ENTRIES)}; fill in number / variant / qty and run again.")
        return
    ensure_closed(bc.XLSX, NEW_ENTRIES)

    entries, rows = read_new_entries()
    if not entries:
        print(f"{NEW_ENTRIES.name} is empty; nothing to add.")
        return

    wb = openpyxl.load_workbook(bc.XLSX)
    title, set_name = find_set(wb, args.set, SetLookup())
    if title is None:
        ws = create_tab(wb, set_name)
        print(f"{set_name}: no tab yet, created '{ws.title}' from the Template tab")
    else:
        ws = wb[title]
    print(f"{set_name} (tab '{ws.title}'), {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}:")
    for line in merge(ws, entries, args.replace):
        print(line)

    if args.dry_run:
        print("\nDry run: nothing was written.")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f"{bc.XLSX.stem}-{datetime.now():%Y%m%d-%H%M%S}.xlsx"
    shutil.copy2(bc.XLSX, backup)
    wb.save(bc.XLSX)
    print(f"\nSaved {bc.XLSX.name} (previous version: {rel(backup)})")
    if not args.keep:
        clear_entries(rows)
        print(f"Emptied {NEW_ENTRIES.name}.")
    print("Next: pokemon/.venv/bin/python pokemon/build_catalogue.py")


if __name__ == "__main__":
    main()
