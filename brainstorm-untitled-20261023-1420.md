# Brainstorm: untitled
Date: 2026-10-23 14:20
Technique(s) used: Free Association

## [MAIN] untitled

Topic: switching the price/buying side from Cardmarket (via TCGGO) to CardTrader (own API: language + condition filters, wishlist import)

## [MAIN] Switching from Cardmarket to CardTrader
- Context: CardTrader API v2, bearer token; marketplace products filterable by expansion/blueprint + language (en) + condition; rate limits 200/10s, 10/s marketplace; wishlist import per user's reading of the docs (to verify)
- Idea: lowest NM English price straight from CardTrader listings (no third party in between)
- Idea: average of the 5 lowest NM English listings becomes possible again (individual listings!)
- Idea: master set missing list -> CardTrader wishlist pushed by the script, no copy-paste
- Idea: one card identity map: our card (set, number, variant) <-> CardTrader blueprint id, cached
- Idea: CardTrader Zero / hub shipping: many sellers, one parcel -> the "few sellers" problem shrinks
- Idea: keep Cardmarket as a second opinion column, or drop it entirely
- Idea: special prints (stamps, staff, cosmos) as separate blueprints? coverage check per set
- Idea: wishlist sync both ways: bought on CardTrader -> card leaves the wishlist -> add_entries suggestion
- Idea: price alert: wishlist max price = your own threshold per card
- User: unsure about current API (all points); Cardmarket wants-list import + "sellers with most cards" cart broken; will try CardTrader + CardTrader Zero; two phases: (1) fairs with an accurate NM EN price list, (2) endgame on CardTrader for the last hard-to-find cards
- Inspiration: CardTrader Zero = buy from many sellers, they ship to CT's hub, CT checks condition and buys back mismatches, one shipment to you; 9-14 days on average; Zero 1-Day for cards already at the hub
- Idea (phase 1, fairs): the list's price = CardTrader NM EN lowest + avg of 5 lowest (offline-friendly, dated)
- Idea: "walk-away price" column you fill in yourself per card before the fair
- Idea: price bands on the fair list: cheap (<1), mid, chase (>20) so you know where to look hardest
- Idea: phone version of the list sorted by binder order AND a version sorted by price
- Idea: at the fair, tick cards bought -> later one add_entries run (the list doubles as new_entries input?)
- Idea (phase 2, endgame): only the last N cards go to a CardTrader wishlist; trigger = missing count below a threshold, or a date
- Idea: Zero-only filter on the wishlist / prices (sellers that ship via the hub)
- Idea: Zero 1-Day as "already checked" signal for expensive cards
- Idea: Zero's condition check = extra NM guarantee for chase cards
- Idea: compare fair price paid vs CardTrader NM EN avg afterwards (opt-in, not tracking)
- Idea: hybrid moment: before a fair, regenerate the list so prices are fresh that week

---
## [FORK 1] Fair price list: what it shows, how it's carried and used at the stand
Parent: MAIN
- Idea: card picture thumbnail on the list: recognise the exact print at a glance in a binder at the stand
- Idea: big, glanceable rows on a phone: number + name + print + one price, nothing else
- Idea: offline-first: the list works without signal in a fair hall (file on the phone, not a web page)
- Idea: search box / filter by set code or name while flipping a seller's binder
- Idea: "seen at" note: stand number + asking price, to compare stands before buying
- Idea: quick tick "bought" + price paid, exported back as new_entries rows at home
- Idea: printed one-pager per set: dense grid, checkbox, price, for people who don't want to stare at a phone
- Idea: condition reminder per row: NM price only valid for NM; quick checklist for inspecting a card at the stand
- Idea: haggle helper: show "CardTrader NM EN lowest" as a number you can show the seller
- Idea: budget line at the top: total of what's still missing at CardTrader prices
- Decision (user): pen and paper at fairs, no phone
- Decision (user): haggles a bit -> wants the 90% indication back (opening offer)
- Idea: printed list columns: checkbox | # | name | print | lowest NM EN | 90% (offer) | paid (blank to write in)
- Idea: write-in columns: "paid", "stand" so the sheet becomes the record of the day
- Idea: haggle ladder per card: 90% (open) -> 100% lowest (fair) -> avg of 5 (walk away above)
- Idea: price rounded for the stand (€7.20 -> €7) so it's quick to say out loud
- Idea: cheap cards (<€1) grouped as "bulk: pay per handful" instead of per card prices
- Idea: sort printed list by set then number = order you see in sellers' binders
- Idea: date + "prices from CardTrader NM EN" on top of each page, so old printouts are recognisable
- Idea: big chase cards boxed / bold so they stand out on paper
- Idea: back home: type ticked rows into new_entries.xlsx (paper -> xlsx), or the list xlsx has a "bought" column to fill in from the paper
- Decision (user): the printed fair sheet = last page of *-missing.pdf (brings the list page back into the PDF), columns: series number, card name, rarity, market price, target (90%)
- Open: does the separate -missing.xlsx stay (for links / home use) or go?
- Open: "market price" = CardTrader NM EN lowest, average of 5 lowest, or both?
- Idea: print in the binder's order so the sheet follows the placeholders
- Idea: a checkbox in front of each row for ticking at the fair (pen)
- Idea: a narrow write-in "paid" column even if not asked: cheap, and feeds the home update
- Idea: the "series number" as printed on the card (e.g. PBL 117 / MEP 084) so it matches what you read in a seller's binder
- Idea: a header with date + price source + "NM English only" so a reprint of last month's sheet is recognisable
- Decision (user): fair sheet prices = lowest NM EN + 30-day average (NM EN); target = 90% of the 30-day average
- Decision (user): the -missing.xlsx becomes redundant IF the wanted list can be pushed to CardTrader via the API
- Open (white hat): which source gives a 30-day NM English average? CardTrader's marketplace endpoint shows current listings; a history/average endpoint is unconfirmed. Own history was rejected earlier. -> verify in the CardTrader docs
- Idea: if CardTrader has no 30-day average: average of the 5 lowest NM EN listings as stand-in (earlier fallback rule), labelled
- Idea: verify the CardTrader wishlist API first: it decides whether the xlsx stays
- Decision (user): fallback for the 30-day average = average of the 5 lowest NM EN listings, accepted
- Decision (user): column header must say which average is shown
- Decision (user): keep decimals (no rounding)
- Fact: CardTrader docs have a wishlist section (user); third-party guide lists GET /wishlists?game_id, GET /wishlists/{id}, POST /wishlists, DELETE /wishlists/{id}; exact item fields to confirm in the docs (page blocks automated reading)
- Idea: one CardTrader wishlist per master set ("PBL master set"), recreated (delete + create) on each run so it mirrors the missing list
- Idea: wishlist items carry language EN + min condition NM (if the API allows), so CardTrader's own offers already fit
- Idea: if wishlist items need blueprint ids: the card <-> blueprint map does double duty (prices + wishlist)
- Idea: the PDF's last page and the wishlist come from the same run: paper for fairs, wishlist for the endgame, always identical
- Idea: wishlist only for cards above a price, or only after N fairs ("endgame" filter), vs everything from day 1
- Fact (docs pasted by user): wishlist = deck {name, game_id, public, deck_items_attributes [DeckItem]}; DeckItem: quantity, blueprint_id, meta_name, expansion_code, collector_number, language, condition, foil, reverse, first_edition; also deck_items_from_text_deck (unmatched lines silently ignored!); list/show/create/delete; no update -> delete + create
- Decision (user): every master set update -> delete old wishlist, create new one
- Decision (user): wishlist names: "PBL - Pitch Black" (set), "Kingdra" (pokemon), "Yuka Mori" (illustrator)
- Decision (user): items language English, condition Near Mint as minimum
- Decision (user): every master set update also regenerates the "fair page" (PDF last page)
- Idea: wishlist public = false (privacy: valuable cards stay private)
- Idea: DeckItem.reverse / first_edition -> reverse holos and 1st Editions get their own wishlist lines (and maybe their own prices!)
- Idea: avoid deck_items_from_text_deck (silently drops unmatched lines = hidden gaps); use blueprint ids + report every card without a blueprint
- Idea: "update" = any change to a master set: add_entries --to masterset:X, masterset_setup, manual qty edits -> one command that refreshes PDF + wishlist
- Idea: safety: only delete a wishlist whose name matches exactly, never others; show "deleted X, created Y (N items)"
- Idea: quantity per item = how many still missing (normally 1)
- Idea: wishlist item count vs missing count check: every missing card accounted for (in wishlist, or listed as "no blueprint")
- Idea: complete master set -> wishlist deleted, not left empty
- Idea: offline / no token -> PDF still made, wishlist step skipped with a clear message

---
## [MAIN] Switching from Cardmarket to CardTrader (continued)
Returned from: FORK 1 (Fair price list)
- Idea (switch): CardTrader replaces TCGGO as price source: lowest NM EN + avg of 5 lowest from marketplace listings
- Idea (switch): retire TCGGO + RapidAPI key, or keep it one season as a cross-check
- Idea (switch): the card <-> CardTrader blueprint map: built from expansion exports, matched on collector number + name, cached; specials/deck/staff matched or reported
- Idea (switch): Cardmarket links dropped from the outputs; CardTrader card links instead
- Idea (endgame): switch trigger = only N cards left, or a card missed at 2-3 fairs, or chase cards right away
- Idea (endgame): Zero-only prices as the realistic endgame price (hub shipping)
- Idea (endgame): buy with Zero, then one add_entries run when the parcel arrives
- Idea (endgame): CardTrader token stored next to the other keys (git-ignored)
- Idea (endgame): seller country / EU+UK question becomes moot with the hub
- Fact: user has a CardTrader account + API token (to be stored git-ignored when implementing; token was pasted in chat)
- Decision (user): no listing for a card -> fair page shows "NA"; the card still goes on the wishlist
- Decision (user): no switch trigger: fair with the page -> buy what's there -> at home add cards to the master set -> PDF/fair page + wishlist update automatically. CardTrader wishlist is live all the time in parallel.
- Open: does Cardmarket remain anywhere (links?) or disappear completely
- Idea: the add_entries --to masterset:X run is THE moment: it writes the cards, regenerates the PDF, replaces the wishlist, prints a receipt
- Idea: fair page prints the date of the wishlist it matches ("wishlist updated 23 Oct, 29 cards")
- Idea: "NA" vs "no NM EN offer" distinction: no listing at all vs only lower conditions / other languages
- Clarified: "no listing -> NA" refers to CardTrader
- Decision (user): add_entries --to masterset:X = writes cards + regenerates PDF + replaces wishlist + one receipt
- Decision (user): no NM English listing -> best available condition (English) with an asterisk, condition explained at the bottom of the fair page; no listing at all -> NA
- Idea: footnote per asterisk: "* PBL 117: cheapest English copy is Lightly Played" (per card, not one generic line)
- Idea: different asterisk marks per condition (* EX, ** GD...) vs one * + per-card footnote
- Idea: the average of 5 lowest uses the same condition as the shown price (so lowest and average are comparable)
- Idea: target (90%) only for NM prices, or also for the fallback condition?
- Idea: if only non-English copies exist: NA (English strict) - consistent with earlier decision

---
## Final Summary
Ideas logged: 77 (plus 16 decisions by the user). Forks: 1 (Fair price list).

Key themes:
- Replace Cardmarket/TCGGO with CardTrader's own API: listings filtered on English + condition, private wishlists via the API
- Fair page = last page of *-missing.pdf: series number, name, rarity, lowest NM EN, 30-day avg NM EN (fallback: avg of 5 lowest, named in the header), target = 90% of that average, decimals kept; no NM -> best English condition with * + footnote; no English listing -> NA
- Private CardTrader wishlist per master set ("PBL - Pitch Black", "Kingdra", "Yuka Mori"), English + Near Mint minimum, deleted and recreated on every update; the -missing.xlsx goes away
- One moment does everything: add_entries --to masterset:X writes the cards, regenerates PDF + fair page, replaces the wishlist, prints one receipt
- No switch trigger: fairs with the paper page and the CardTrader wishlist run in parallel

Open items:
- Store the CardTrader token git-ignored (it was pasted in chat; can be regenerated)
- Check whether CardTrader exposes any 30-day average; otherwise the avg-of-5 fallback applies
- Target (90%) on fallback-condition prices or only on NM?
- Verify DeckItem fields with the token (reverse / first_edition lines; condition value "NM" vs "Near Mint")
- Coverage of special prints (stamps, staff, cosmos, deck) as CardTrader blueprints
