# Summary: Reworking master set tracking (preventing dupe purchases)
Date: 2026-10-18 | Ideas: 168 (+23 decisions) | Forks: 2

## Why it went wrong
- PBL list (placeholders.py) measured "missing" against the BULK catalogue after one copy of every card had gone into the binder (qty -1), so binder-filled cards looked missing -> 17 dupes
- The list also predated deck prints and stamped promos (84/85 promo stamp) -> the universe was incomplete

## Decided model (final state of the decisions)
- Two independent ledgers, same shape ("I own X copies of card Y"), identical card lists per set:
  public = bulk only, in git, synced desktop/laptop, shown on the site; private = everything incl. expensive cards, local only (pokemon_mastersets.xlsx, not in git)
- One bridge: when a NEW master set is set up, optionally move 1 public copy of each card it wants -> private. No other transfers; master sets never share copies; finished sets keep their cards
- masterset_setup (rename of the current scripts for clarity): full card list with qty 0; offer the bridge if a public tab exists; soft exit if the master set tab already exists. Works for set (PBL), Pokémon (Kingdra) and illustrator (Yuka Mori) master sets
- Arrivals: new_entries.xlsx + add_entries.py with an obligatory destination (public / masterset:X), no default; missing destination -> soft exit; every label validated against the destination's card list first, soft exit listing all unidentified labels before anything is written
- ALL cards of a set (stamps, deck prints, ...) in both ledgers and on the public site; a set update adds cards everywhere and re-opens a finished master set
- Prices: two facts, no verdict (no target, no traffic lights): lowest NM English listing (EU + UK sellers, best condition if no NM, shown as such) + NM English 30-day sales average; if that average doesn't exist: average of the 5 lowest NM English listings, labelled. Never all-condition guide figures (Morpeko ex SIR: guide ~€54-56, NM reality €70+). Checked only when creating the missing list and the shopping list; no price history kept
- Cardmarket: as few sellers as possible; NM English only; wants list generated from the master set's missing cards (Add Decklist text format; not-added lines = to check)
- Audit: the checklist page at the end of the placeholders PDF, built from the private master set ledger, on screen; corrections via add_entries --to masterset:PBL

## Other ideas (condensed, not decided)
- Ledger mechanics: transfer receipt/log; reverse bridge when abandoning a set; multi-tab bridge for Kingdra/illustrator sets; "ordered" state counts as covered; cancelled order -> back on list
- Dupe guards: shopping list consults both ledgers ("bulk has 2: pull, don't buy"); dupe warning when adding to a master set that already holds the card; notice when public receives a card an open master set lacks; lists carry source + date + "outdated since last add"
- Universe: stack TCGplayer set + subsets + Deck Exclusives + Miscellaneous (stamps/cosmos) + promo groups + TCGdex variants; cross-check counts with Pokecottage; manual additions per set; fixed label vocabulary; record each row's source; per-set changelog; watchlist for sets still getting promos; flag (never delete) removed cards
- Cardmarket: anchor the priciest card's seller, then sweep; add a seller only if it saves more than a shipping fee; domestic first; batch orders; "Sellers with the most cards" before the Shopping Wizard (10 runs/day; Add All to Cart needs 6 purchases); offer count next to prices; one listing per seller in the 5-lowest average
- Naming: verb + noun script names; separate binder placeholders (rarely change) from shopping lists (prices, change often)

## Forks explored
- FORK 1 Two ledgers + one bridge: started as "one inventory", rejected (breaks git sync of the public collection); settled the ledger/bridge/destination model
- FORK 2 Cardmarket flow: few sellers, NM English EU+UK, two price facts, wants list from missing cards

## Open items
- Verify a source for an NM English 30-day sales average (test card Morpeko ex SIR, PBL 117)
- Fewer than 5 NM listings: include lower conditions in the average? Drop outliers?
- PBL restart: new universe, user's 20-card list as draft, then physical check; 84/85 promos and the 17 dupes entered via add_entries

Full session: brainstorm-untitled-20261018-1018.md
