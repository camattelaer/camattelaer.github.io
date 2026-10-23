# Pokémon TCG catalogue

Source for the `/pokemon-tcg/` section of the site. This folder is excluded from
the Jekyll build (`_config.yml`); only the generated files below are published.

There are two independent collections:

| | public collection | private master sets |
|---|---|---|
| workbook | `source/pokemon_bulk_catalogue.xlsx` | `source/pokemon_mastersets.xlsx` |
| holds | bulk cards: "I own X copies of card Y" | master sets (a set, a Pokémon or an illustrator), incl. valuable cards |
| in git | yes (synced to every machine, shown on the site) | **no** (git-ignored, local only, not on the site) |
| scripts | `build_catalogue.py`, `add_entries.py` | `masterset_setup.py`, `masterset_placeholders.py` (local only) |

Both use the same complete card list per set (`build_catalogue.set_universe`).
Cards only move from the public collection to a master set once: when that master
set is set up. Master sets never share copies.

Commands below are for macOS; on Windows use `pokemon\.venv\Scripts\python.exe
pokemon\<script>.py` (each script lists its exact commands at the top). Close the
workbooks in Excel before running a script that changes them.

## Adding cards

Fill in `source/new_entries.xlsx` (`number`, `variant`, `qty`, cards of one set),
close Excel, then say where they go. **`--to` is required**:

```sh
pokemon/.venv/bin/python pokemon/add_entries.py --to public --set ASC          # bulk collection
pokemon/.venv/bin/python pokemon/add_entries.py --to masterset:PBL             # a set master set
pokemon/.venv/bin/python pokemon/add_entries.py --to masterset:Kingdra --set PAR   # Pokémon master set
```

Every row is checked against the destination's card list first; if any row
doesn't match (unknown number, variant or card), all of them are listed and
nothing is written. A card a master set already has is flagged as a duplicate.
`--dry-run` shows the changes, `--replace` sets quantities instead of adding,
`--keep` leaves `new_entries.xlsx` filled. Workbooks are backed up to
`pokemon/.cache/backups/` before every save.

**Numbers**: the printed number (`25` or `025/217`); promos with their prefix
(`MEP 084`); Classic Collection-style sets the full number where several cards
share one (`106/105`). **Variants**: `normal`, `holo`, `reverse`, `1st-normal`,
`1st-holo`, the ball / energy patterns, `cosmos` (Cosmos Holo), `altholo` (other
holo patterns), `stamp`, `prerelease`, `staff`, `promo` (store / event promos).
Deck-exclusive non-holos are `normal` (shown as "Normal (deck)").

## Updating the site

```sh
python3 -m venv pokemon/.venv                              # first time only
pokemon/.venv/bin/pip install -r pokemon/requirements.txt  # first time only
pokemon/.venv/bin/python pokemon/build_catalogue.py
```

Read the report at the end: rows listed there are **not** on the site. Fix the
xlsx, or for a set that can't be matched add an entry to
`source/set_overrides.yml`, then rerun. Commit the xlsx with the generated
`_data/pokemon/*.json` and `pokemon-tcg/<slug>.md`.

## Master sets (private)

```sh
pokemon/.venv/bin/python pokemon/masterset_setup.py --set "Pitch Black"     # or --set PBL
pokemon/.venv/bin/python pokemon/masterset_setup.py --pokemon Kingdra
pokemon/.venv/bin/python pokemon/masterset_setup.py --illustrator "Yuka Mori"
```

`masterset_setup.py` creates a tab listing every card + variant with qty 0. If
the public collection has some of those cards, it asks whether to move 1 copy of
each into the master set (public qty − 1, master set qty 1, logged on the
"Transfers" sheet; `--transfer yes|no` answers up front). A master set that
already has a tab is left alone.

```sh
pokemon/.venv/bin/python pokemon/masterset_placeholders.py --masterset PBL
```

`masterset_placeholders.py` refreshes a master set. `add_entries.py --to masterset:<name>` and
`masterset_setup.py` run it automatically; run it by hand after editing quantities yourself.

- It writes `pokemon/placeholders/<name>-missing.pdf`: a card-sized placeholder for every
  missing card (3 × 3 per page, the master set's order; print at 100%), and as last page the
  **fair page**: series number, name, rarity, print, the lowest Near Mint English price,
  the average of the 5 lowest and a target of 90% of that average. `*` = no Near Mint copy
  (the condition is named at the bottom), `NA` = no English copy listed, `(n)` = average of
  only n copies.
- It replaces the master set's private **CardTrader wishlist** ("PBL - Pitch Black",
  "Kingdra", "Yuka Mori") with the missing cards, English and Near Mint minimum. The API has
  no update, so the old wishlist is deleted and created again. Prints CardTrader doesn't have
  (deck prints, Cosmos Holos, some stamps) are listed in the receipt.
- Two wishlists per master set:
  - "PBL - Pitch Black": every card CardTrader can place exactly, ready to add to the cart.
    Lines are English + Near Mint, except cards that share their name with another card of
    the same set (Gladion's Final Battle 077 / 108 / 118, Mega Darkrai ex 120): they go on by
    set code + number, which CardTrader's API only accepts without language or condition
    (the receipt lists them), so choose English Near Mint when buying;
  - "PBL - Pitch Black (verify version)": stamped / Staff / deck / Cosmos prints, English +
    Near Mint. CardTrader's API can't choose their version, so pick it once in the dropdown
    on CardTrader; this list is only recreated when its own cards change, so your choices stay.
  Which cards are exact is checked with a temporary trial wishlist on every update.
- Cards are found on CardTrader by TCGplayer id in their own expansion, then in an index of
  every CardTrader Pokémon card (deck exclusives, Cosmos Holos and stamps live in separate
  expansions there; built once a month, a few minutes), then for special prints without a
  TCGplayer id by name + number + version keyword (a match on just "stamp" is flagged).

**Prices** (`masterset_cardtrader.py`): CardTrader marketplace listings for the exact card
(matched on its TCGplayer id) and print (reverse / 1st Edition flags), English copies from
sellers shipping via CardTrader Zero (any country), graded / signed / altered copies left out. CardTrader has no 30-day average,
so the average of the 5 cheapest Near Mint copies is used. The token goes in the
git-ignored `source/api_keys.yml` (`cardtrader_token`). Each set is matched to a CardTrader
expansion by name (the one sharing the most cards when several fit); pin it with
`cardtrader: <expansion id>` in `source/set_overrides.yml` if needed. Card lists are cached
30 days, listings 12 hours.

## How it works

- **Card lists** come from [TCGCSV](https://tcgcsv.com) (a TCGplayer mirror):
  the set's own group (variants from the price subtypes, ball / energy pattern
  products), its subsets (Trainer Gallery, Galarian Gallery, Shiny Vault,
  Radiant Collection), deck exclusives, Cosmos Holos and stamps from the Blister
  Exclusives / Miscellaneous groups (matched on number + printed total + name),
  and the set's promos (prefix `MEP 084`: promos stamped with the set's name mark
  a number range in a promo group; staff and prerelease versions in it belong to
  the set too).
- **Set logos, release dates and series** come from [TCGdex](https://tcgdex.dev),
  with [pokemontcg.io](https://pokemontcg.io) or a `logo:` override as fallback.
- **Set matching**: xlsx set names are TCGdex names; TCGplayer group names are
  fuzzy-matched and every non-exact match is printed. `source/set_overrides.yml`
  pins a set to a TCGplayer `groupId`, a TCGdex id, a `logo`, or a card `order`.
- **Classic Collection-style sets** (cards with their original number, e.g. Mew
  VMAX 114/264) are detected and matched on the full printed number.
- **Cache**: API responses live in `pokemon/.cache/` (git-ignored). Use
  `--refresh` on `build_catalogue.py` to refetch everything.
- Deleting a set's sheet in the public workbook removes its page and data file
  on the next build.
