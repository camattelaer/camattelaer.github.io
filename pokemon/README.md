# Pokémon TCG catalogue

Source for the `/pokemon-tcg/` section of the site. This folder is excluded from
the Jekyll build (`_config.yml`); only the generated files below are published.

## Updating the catalogue

1. Edit `source/pokemon_bulk_catalogue.xlsx` (sheet "Catalogue": `set_name`,
   `number`, `variant`, `qty`, one row per card + variant).
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

## How it works

- **Card lists** come from [TCGCSV](https://tcgcsv.com) (a TCGplayer mirror).
  Plain cards get their normal / holo / reverse variants from the price
  subtypes; Poké Ball, Master Ball, Energy Symbol, etc. patterns are separate
  products named e.g. `Oddish (Poke Ball Pattern)`. Trainer Gallery, Galarian
  Gallery, Shiny Vault and Radiant Collection groups are merged into their
  main set automatically.
- **Set logos, release dates and series** come from [TCGdex](https://tcgdex.dev).
- **Set matching**: xlsx set names are TCGdex names. TCGplayer group names
  have prefixes (`SV: Prismatic Evolutions`), so the script strips those,
  then fuzzy-matches; it prints every non-exact match so you can check it.
  `source/set_overrides.yml` pins a set to a TCGplayer `groupId` and/or
  TCGdex id when that fails.
- **Cache**: API responses are stored in `pokemon/.cache/` (git-ignored), so
  reruns are fast and offline. Use `--refresh` to refetch everything, e.g.
  after TCGplayer adds cards to a new set. Set lists are refetched
  automatically when a set isn't found in the cached copy.
- Removing every row for a set from the xlsx removes its page and data file
  on the next run.
