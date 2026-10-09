# Pokémon TCG catalogue

Source for the `/pokemon-tcg/` section of the site. This folder is excluded from
the Jekyll build (`_config.yml`); only the generated files below are published.

## Updating the catalogue

1. Add cards. Either:
   - **via `source/new_entries.xlsx`** (recommended for new cards): fill in
     `number`, `variant`, `qty` for one set, close Excel, and merge it into the
     catalogue with the set's official abbreviation (the code printed on the
     card, e.g. ASC, TEF, PRE):

     ```sh
     pokemon/.venv/bin/python pokemon/add_entries.py --set ASC
     ```

     A card + variant already on the set's tab gets the new qty **added** to
     it (`--replace` sets it instead); anything else is appended. A set
     without a tab gets one, copied from "Template". The catalogue is backed
     up to `pokemon/.cache/backups/` first, and `new_entries.xlsx` is emptied
     afterwards so a rerun can't add the same cards twice (`--keep` leaves it).
     `--dry-run` shows the changes without writing anything.
   - **or directly in `source/pokemon_bulk_catalogue.xlsx`**. Every set has its
     own sheet: the set name goes in cell B1 (dropdown), and from row 3 down
     there are `number`, `variant`, `qty` columns, one row per card + variant.
     For a new set, copy the "Template" sheet and rename the tab; the tab name
     is only for navigation. Every sheet except "How to use" and "Lists" is read.
2. Run the build script from the repo root:

   ```sh
   python3 -m venv pokemon/.venv                          # first time only
   pokemon/.venv/bin/pip install -r pokemon/requirements.txt  # first time only
   pokemon/.venv/bin/python pokemon/build_catalogue.py
   ```

3. Read the report at the end. Any row listed there is **not** on the site
   (unknown set, card number or variant). Fix the xlsx, or for a set that
   can't be matched add an entry to `source/set_overrides.yml`, then rerun.
4. Preview with `bundle exec jekyll serve` if you like, then commit the xlsx
   together with the generated files:
   - `_data/pokemon/sets.json` and `_data/pokemon/<slug>.json`
   - `pokemon-tcg/<slug>.md` (one stub page per set)

The script exits with status 1 when the report isn't empty, but it still
writes everything it could match.

## Placeholder cards for master set hunting

`placeholders.py` makes a printable PDF with a card-sized placeholder for every
card + variant you don't own yet in a set, 3 × 3 per page in set order, so a
printed page matches one 9-pocket binder page:

```sh
pokemon/.venv/bin/python pokemon/placeholders.py --set TEF
```

Each placeholder shows a faded greyscale picture of the card, its name, number
and a coloured variant badge (the picture alone can't tell a normal from a
reverse or Poké Ball print). It reads the generated `_data/pokemon/<slug>.json`,
so run `build_catalogue.py` first. The PDF goes to `pokemon/placeholders/`
(git-ignored); print it at 100% / actual size.

The PDF ends with a landscape **checklist**: on the left every card numbered up
to the set's official count (checkbox, number, name, variant), on the right the
ones above it (checkbox, number, name, rarity such as IR / SIR / HR, market
price, target price) with totals. When the lists are too long for one page they
continue on the next.

- **Market price** is Cardmarket's 7-day average sell price in EUR, taken
  from Cardmarket's price guide as TCGdex publishes it per card (Cardmarket has
  no open API). Reverse holos use Cardmarket's reverse-holo price. When a
  card has no 7-day value, the 30-day average or the trend is used and marked
  `*`. The page footer states the source and the date of the price data.
- **Target price** defaults to 90% of the market price.
- Prices are cached for 12 hours in `pokemon/.cache/cards/`.

Options: `--variants reverse,pokeball` (only those variants), `--all` (every
card, e.g. to set up a new binder), `--color`, `--no-images` (text only),
`--paper letter`, `--out file.pdf`, `--price avg7|avg30|avg1|trend`,
`--target-pct 85`, `--no-checklist`, `--refresh-prices`. `--set` takes the
set's official abbreviation, its name or its slug. Card pictures are cached in
`pokemon/.cache/images/`.

## Pokémon master sets

`source/pokemon_mastersets.xlsx` tracks master sets per Pokémon (one tab each,
name in B1). It is **not** part of the website: nothing reads it except
`masterset.py`. Both files are local only: they're git-ignored, so they're never
committed (not to dev, not to main) and aren't backed up by git. Keep your own
copy of them.

```sh
pokemon/.venv/bin/python pokemon/masterset.py --pokemon Kingdra   # new Pokémon: creates its tab
pokemon/.venv/bin/python pokemon/masterset.py                     # every tab
```

The script fills each tab with every English card + variant of that Pokémon;
you only fill in `qty` (blank = missing, `skip` = not hunting that variant).
Reruns add newly released cards and keep your quantities; rows you add yourself
(without a key) are kept too. The workbook is backed up to
`pokemon/.cache/backups/` before every save. Close it in Excel first.

- **Variants** come from TCGplayer (via TCGCSV): one row per product + print
  (1st Edition / Unlimited, normal / holo / reverse), including stamped
  promos, staff and prerelease versions, deck exclusives and World Championship
  deck cards. Jumbo cards, code cards and anything labelled error / misprint
  are left out, as is TCG Pocket. Matching on whole words keeps e.g. Mewtwo
  out of a Mew master set.
- **Set, release date and rarity** come from TCGdex.
- It writes `pokemon/placeholders/<pokemon>-masterset.pdf`: placeholders for
  the missing cards (without prices, since those change), then a landscape
  price list of the whole master set in two columns (owned cards ticked) with totals for the set, owned and missing cards.
- **Prices**: Cardmarket's 7-day average (EUR) via TCGdex where Cardmarket's
  price guide maps onto the variant. Where it can't (1st Edition vs Unlimited,
  normal vs holo of one card, stamped and other special prints), or where
  TCGdex has linked the wrong Cardmarket product (one product on two cards,
  swapped normal / reverse prices, more than 10× off), TCGplayer's market
  price for the exact variant is converted at the ECB rate
  ([frankfurter.dev](https://frankfurter.dev)), marked † / ‡. The footer
  explains it. Same `--price`, `--target-pct`, `--refresh-prices`, `--color`,
  `--no-images`, `--paper` options as `placeholders.py`; `--no-pdf` only
  updates the workbook.

## How it works

- **Card lists** come from [TCGCSV](https://tcgcsv.com) (a TCGplayer mirror).
  Plain cards get their normal / holo / reverse variants from the price
  subtypes; Poké Ball, Master Ball, Energy Symbol, etc. patterns are separate
  products named e.g. `Oddish (Poke Ball Pattern)`. Trainer Gallery, Galarian
  Gallery, Shiny Vault and Radiant Collection groups are merged into their
  main set automatically.
- **Set logos, release dates and series** come from [TCGdex](https://tcgdex.dev).
  TCGdex has no logo for some sets (e.g. Temporal Forces); those fall back to
  [pokemontcg.io](https://pokemontcg.io) by set name, or to a `logo:` URL in
  `source/set_overrides.yml`. Sets with neither show the set name as text.
- **Set matching**: xlsx set names are TCGdex names. TCGplayer group names
  have prefixes (`SV: Prismatic Evolutions`), so the script strips those,
  then fuzzy-matches; it prints every non-exact match so you can check it.
  `source/set_overrides.yml` pins a set to a TCGplayer `groupId` and/or
  TCGdex id when that fails.
- **Cache**: API responses are stored in `pokemon/.cache/` (git-ignored), so
  reruns are fast and offline. Use `--refresh` to refetch everything, e.g.
  after TCGplayer adds cards to a new set. Set lists are refetched
  automatically when a set isn't found in the cached copy.
- Deleting a set's sheet (or emptying it) removes its page and data file on
  the next run.
