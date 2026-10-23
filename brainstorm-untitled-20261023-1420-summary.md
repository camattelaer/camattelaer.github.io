# Summary: Switching master set prices and wishlists from Cardmarket to CardTrader
Date: 2026-10-23 | Ideas: 77 (+16 decisions) | Forks: 1

## Why
Unsure about the TCGGO/RapidAPI setup (third party, 100 requests/day, no prices for special
prints and reverses, no individual listings); Cardmarket's wants-list import and "sellers with
the most cards" cart don't work well. CardTrader has its own API: listings filtered on language +
condition, and private wishlists created through the API. Plan to try CardTrader Zero (hub shipping).

## Decided
- Prices from CardTrader: lowest Near Mint English listing + 30-day average NM EN; if CardTrader has
  no 30-day average: average of the 5 lowest NM EN listings. Column header names the average used.
  Decimals kept. No NM English listing -> best English condition, marked * with a per-card footnote;
  no English listing -> NA.
- Fair page = last page of <name>-missing.pdf (pen and paper, no phone): series number, card name,
  rarity, lowest, average, target = 90% of the average (opening offer for haggling).
- One private CardTrader wishlist per master set: "PBL - Pitch Black" / "Kingdra" / "Yuka Mori";
  items English + Near Mint minimum; deleted and recreated on every update (the API has no update).
  Cards without a CardTrader listing still go on the wishlist. The -missing.xlsx is dropped.
- add_entries --to masterset:X is the single moment: writes the cards, regenerates PDF + fair page,
  replaces the wishlist, prints one receipt. Fairs and the wishlist run in parallel (no trigger).

## Other ideas (not decided)
- Use blueprint ids, not the text import (it silently drops unmatched lines); report every card
  without a CardTrader blueprint; check missing count = wishlist items + not found.
- Wishlist public = false; only delete an exact name match; complete master set -> wishlist deleted;
  no token / offline -> PDF still made, wishlist skipped with a message.
- DeckItem reverse / first_edition -> reverse holos and 1st Editions as their own lines (maybe prices).
- Fair page: checkbox + "paid" write-in column, date + source header, chase cards bold, totals,
  binder order; a refresh command after manual qty edits.
- Zero-only prices / Zero 1-Day as condition-checked signal; retire TCGGO or keep as cross-check.

## Open
- Store the CardTrader token git-ignored (pasted in chat; can be regenerated).
- Target on fallback-condition prices, or only on Near Mint?
- Verify with the token: DeckItem condition value ("NM" vs "Near Mint"), reverse field, coverage of
  special prints (stamps, staff, cosmos, deck) as blueprints, any 30-day average data.

## Forks Explored
- Fair price list: paper fair page as the PDF's last page, its columns, NA / asterisk rules.

Full session: brainstorm-untitled-20261023-1420.md
