# Brainstorm: Reworking master set tracking (preventing dupe purchases)
Date: 2026-10-18 10:18
Technique(s) used: Free Association

## [MAIN] Reworking master set tracking
Trigger: the PBL list (placeholders.py, based on the bulk catalogue) led to buying 17 dupes of bulk cards already owned.

User's proposal:
- pokemon_mastersets.xlsx stays private (not in git)
- clearer script names (placeholders.py / masterset.py purpose unclear)
- masterset_setup.py: builds the full card list with qty 0; if the set has a bulk tab, asks whether to transfer 1 copy of each owned card; exits softly if the masterset tab already exists
- works for Pokémon master sets (Kingdra), illustrator sets (Yuka Mori) and set master sets (PBL)
- ALL cards of a set: including stamped promos (e.g. PBL 84 and 85 promo stamp)

PBL still missing (per user): 4 holo, 21 rev, 27 holo, 28 normal (deck), 31 holo, 35 normal (deck), 45 holo, 47 rev, 62 normal (deck), 62 rev, 70 normal (deck), 70 rev, 73 rev, 84 normal (deck), 104 holo, 105 holo, 110 holo, 118 holo, 119 holo, 120 holo. Newly bought: 84 + 85 promo (stamp).

Root-cause ideas (gaps that let dupes through):
- Idea: two inventories (bulk vs binder) drifting apart; the -1 transfer happened outside any process
- Idea: placeholders.py measured "missing" against bulk *after* binder copies were removed, so binder-filled cards looked missing
- Idea: printed list goes stale; purchases happen days later against an old snapshot
- Idea: no "ordered / on its way" state, so things get bought twice
- Idea: the universe of cards changes (deck prints, stamps discovered later) without telling you
- Idea: no "pull from bulk extras instead of buying" hint
- Idea: no physical audit / reconcile step between spreadsheet and binder
- Idea: card identity too loose (number + variant, no stamp/source dimension)
- Idea: overlapping master sets (Kingdra card by Yuka Mori in PBL?) compete for one physical card

Alternative models:
- Idea: one inventory with a location per copy (bulk / binder:PBL / binder:Kingdra / ordered / sold) instead of two files
- Idea: reserve instead of transfer
- Idea: ongoing routing, so new bulk entries prompt "PBL binder needs this"
- Idea: refresh-universe mode adds newly discovered variants to an existing masterset tab without touching qty
- Idea: tiered definition (master / grand master), user picks the tier per set
- Idea: "before you buy" lookup on the phone instead of a printed list
- Idea: list carries a "valid as of" date and a completeness confidence
- Idea: a "known unknowns" section listing variants the sources disagree on

## Provocative Questions Explored
- What if the list said where each card IS rather than what's missing?
- What if a purchase isn't "done" until it's logged?
- Who decides what "ALL" means: TCGplayer, TCGdex, Pokecottage or you?

## External Inspiration (from web)
- Elite Fourum / Pokecottage: master vs grand master set tiers (stamps, staff, prerelease, deck non-holos, store stamps); the definition of "complete" is partly personal

---
## [FORK 1] Two ledgers + one bridge (started as "one inventory", rejected: breaks desktop/laptop sync of the public collection)
Parent: MAIN
- Idea: a "copies" ledger: one row per physical copy (or per card + location + qty)
- Idea: locations: bulk, binder:<name>, ordered, in transit, for trade, sold, graded
- Idea: transfer = changing a location, never adding/subtracting in two files
- Idea: public site shows a filtered view (bulk + binders, valuables hidden), private file holds everything
- Idea: "want" lives on the binder side; "have" lives in the ledger; missing = want minus copies located there
- Idea: spares view = copies in bulk beyond what any binder wants, so "pull" before "buy"
- Idea: ordered copies count toward "covered", so nothing gets bought twice
- Idea: every purchase enters as "ordered" with a date and shop, then flips to bulk/binder on arrival
- Idea: overlap rule: a copy can be claimed by only one binder; a second binder needing it shows "claimed by Kingdra"
- Idea: audit mode: walk the binder page by page, tick slots, mismatches get flagged
- Idea: event log instead of quantities (bought, moved, sold); quantities are computed, history is never lost
- Constraint (user): a single private file breaks the git sync of the public bulk collection to the laptop -> two stores needed, but they must not drift
- Idea: private overlay: public file = bulk truth; private file only holds claims/moves that reference public cards (like a layer on top)
- Idea: private file never copies quantities, only "binder X holds 1 of card Y"; missing/spares are computed by joining both
- Idea: sync the private file by another road: private GitHub repo, git submodule, OneDrive/iCloud folder, USB stick
- Idea: encrypt the private file inside the public repo (git-crypt / age / password-protected xlsx): one sync, one place, unreadable to others
- Idea: split by sensitivity, not by purpose: public = everything below a value threshold; private = valuables only
- Idea: public file shows a valuable card as owned without detail ("1 hidden copy")
- Idea: double-entry bookkeeping: every move writes both sides at once, plus a balance check that both ledgers agree
- Idea: reconciliation report run before every shopping list: refuses to print if the two files disagree
- Idea: shared card IDs (e.g. TCGplayer product id + variant) as the glue between the files, so names/numbers can't mismatch
- Idea: the laptop doesn't need the private data at all if the shopping list is generated from the private side only where it lives
- Idea: one master file kept private, the public bulk file generated from it (export, not edit)
- Decision (user): two independent ledgers with the same shape ("I own X copies of card Y"): public = bulk only (git), private = everything incl. expensive cards (only for me). One bridge: when starting a masterset, optionally transfer 1 copy public -> private.
- Idea: the bridge is the only risky moment, so make it a single explicit event with a receipt (what moved, when, from which tab)
- Idea: a transfer log kept privately, so a later "why does bulk show 2 not 3?" has an answer
- Idea: shopping list consults BOTH ledgers: "missing in binder, but bulk has 2: pull, don't buy"
- Idea: a second bridge moment: after setup, a new bulk copy of a card the masterset still lacks -> "route to binder?" prompt
- Idea: purchases for a masterset land in the private ledger directly; dupes that arrive go to the public one
- Idea: same card identity in both ledgers (same numbers/variants/stamps), so a transfer can't land on the wrong row
- Idea: undo / reverse transfer (binder copy back to bulk) for when you abandon a masterset
- Idea: Kingdra / Yuka Mori mastersets pull from many public tabs at once, so the setup question lists per tab what could move
- Idea: the public site loses a count when a copy moves; show nothing about it, or a neutral "1 copy in a private binder"
- Decision (user): bridge = any public copy of a card the masterset wants may move; set card lists are identical in public and private
- Decision (user): arrivals go through new_entries.xlsx + add_entries.py with an obligatory destination flag (public or masterset X), no default; missing flag -> soft exit; all labels validated against the destination list first, soft exit listing every unidentified label before anything is written
- Decision (user): mastersets are independent: cards in a finished masterset stay put; each new masterset chases its own copies; transfers only from public -> a NEW masterset
- Idea: identical lists imply one shared "universe" per set used by both ledgers (incl. stamps, deck prints), so the public site also shows stamped promos
- Idea: universe changes (new stamp discovered) must reach both ledgers the same way
- Idea: destination sanity check: adding to masterset X a card it already has -> "this would be a dupe in X; did you mean public?"
- Idea: reverse check: adding to public a card an unfinished masterset still lacks -> notice only (no auto-route, to respect the bridge rule)
- Idea: mixed parcels: per-row destination column in new_entries.xlsx vs one flag per run (split the parcel into two runs)
- Idea: flag names that read like a sentence: --to public / --to masterset:PBL / --to masterset:Kingdra
- Idea: validation report groups problems: unknown number, unknown variant, variant not in that set, stamp not recognised
- Idea: dry-run summary as the default first step: show destination, counts, dupes before writing
- Idea: Kingdra/illustrator mastersets: bridge scans every public tab for matching cards, list per set what can move
- Idea: masterset identity: a name + type (set / pokemon / illustrator) + its card list, created once by setup
- Decision (user): public site shows ALL cards of a set (stamps, deck prints, ...)
- Decision (user): when a series gains cards, the set (public + every masterset of it) is updated
- Decision (user): a masterset is "finished" until its set receives an update, then it re-opens
- Idea: per-set changelog: "18 Oct: +2 stamped promos (84, 85)" visible privately and/or on the site
- Idea: re-open alert: "PBL master set re-opened: 2 new cards" at the top of the build output / shopping list
- Idea: states: building -> complete -> re-opened -> complete again, with dates
- Idea: what triggers the update check: every build, weekly refresh, a manual "check for new variants" command
- Idea: removed cards (source error): flag instead of deleting, never silently drop a row with qty
- Idea: site badge "complete as of <date>" on finished master sets... (private only?) / public set page "new cards added <date>"
- Idea: watchlist: sets known to still get promos (league, prerelease, staff) re-checked more often than old ones

---
## [MAIN] Reworking master set tracking (continued)
Returned from: FORK 1 (Two ledgers + one bridge)
- Idea: script names say what they do: build_site_catalogue / add_cards / masterset_setup / masterset_shopping_list / masterset_placeholders
- Idea: split "placeholders" (binder printouts, rarely change) from "shopping list" (prices + missing, changes often) as separate outputs/scripts
- Idea: every printout states its source ledger ("from: private PBL master set, as of 18 Oct 10:45")
- Idea: a shopping list is only "valid" while nothing was added since; the header shows the last add_entries run
- Idea: phone-friendly shopping list (HTML / artifact) instead of paper, refreshed on each run
- Idea: "already got it?" lookup before buying at a fair: card number -> where it lives (public qty, master set qty)
- Idea: a buy log separate from arrivals: "ordered" entries count as covered until they arrive
- Idea: shopping list names the exact print (number + variant + stamp + picture), so a reverse isn't mistaken for a holo
- Idea: guard against the old leak: a list built from a ledger that isn't the master set refuses to call cards "missing"
- Context (user): bought singles only at fairs so far; wants to buy on Cardmarket; wants a Cardmarket wantlist generated from a master set's missing cards
- Idea: generate a text list in Cardmarket's "Add Decklist" format (one card per line, count + full card name + set) and paste it into a wants list
- Idea: the import reports added vs not-added lines: treat the red "not added" list as a to-check list
- Idea: one wants list per master set (PBL wants, Kingdra wants), regenerated after every add_entries run
- Idea: per-card direct links using Cardmarket product ids (TCGdex already carries idProduct), as a fallback for lines the import can't match
- Idea: put the target price (90%) in the wants list as "max price", so the wizard only fills at or below target
- Idea: condition / language / reverse-holo filters per line (NM, English, reverse only) to avoid buying the wrong print
- Idea: Shopping Wizard (10 runs/day) vs "Sellers with the most cards": few sellers = fewer shipping costs
- Idea: batch strategy: one big order per month vs many small ones (shipping cost per seller)
- Idea: fair checklist and Cardmarket list come from the same missing-list, with "ordered" status flipping after checkout
- Idea: after an order: paste order confirmation -> mark cards "ordered" -> on arrival add_entries --to masterset:PBL
- Idea: fairs vs Cardmarket split: cheap bulk at fairs, expensive SIRs on Cardmarket (or vice versa), list marks where to hunt each card

---
## [FORK 2] Cardmarket flow: wants list, efficient carts, shipping vs price, ordered status, fairs vs online
Parent: MAIN
- Idea: anchor-first buying: buy the most expensive missing card first, then fill the rest from that same seller (forum workaround)
- Idea: "seller sweep": after anchoring, check that seller's other listings for any remaining missing cards
- Idea: shipping threshold rule: only add a new seller if the cards from them save more than one extra shipping fee
- Idea: tiers in the wants list: "must have now" (cheap, plentiful) vs "wait for a deal" (SIRs) vs "fair only" (bulk reverses)
- Idea: price alerts: a card drops below target -> it moves to "buy now"
- Idea: Cardmarket Optimizer extension (third-party) for 10-30% savings claims
- Idea: TCGplayer-style cart optimizer as a mental model: fewest sellers, total incl. shipping
- Idea: a "batch day": collect missing cards over a month, buy once
- Idea: domestic sellers first (cheaper/faster shipping, same country)
- Idea: track real cost per card incl. shipping share, compare to market price: was it a good deal?
- Idea: trust/condition filter: seller rating + "Near Mint only" for binder cards, "any condition" for placeholders-to-replace
- Idea: the wants list is a mirror, not the truth: the private ledger stays master, the wants list is rebuilt from it
- Preference (user): as few sellers as possible; fair card prices (no €10 for a €2 card); Near Mint minimum always; compare seller price vs lowest and 30-day average
- Idea: fairness band per card: OK if seller price <= 30-day avg + tolerance
- Idea: tolerance that scales: cheap cards get an absolute margin (+€0.50), expensive ones a percentage (+10%)
- Idea: traffic light per line: green (<= avg30), amber (within band), red (above band: skip or swap seller)
- Idea: cart-level overpay budget: overpaying up to one shipping fee in total is fine if it saves a seller
- Idea: the trade-off in one line: "seller B saves €X shipping, costs €Y extra on cards"
- Idea: seller report card: how many missing cards they have at a fair price, NM, and total incl. shipping
- Idea: "lowest" vs "lowest Near Mint": the price guide's low may be a worse condition, so the honest comparison is against NM offers
- Idea: comparison sheet columns: card | seller price | lowest | 30-day avg | difference | verdict
- Idea: wants list lines carry min condition NM + English + max price = the fair ceiling, so unfair offers never show up
- Idea: after an order, store what was paid vs avg30 for later "how good were my deals" stats
- Requirement (user): all Cardmarket prices used (incl. lowest) must be for Near Mint (or better) English copies
- White hat: the public price guide behind our current prices (low / trend / avg7 / avg30 via TCGdex) is, as far as known, not filtered to NM + English -> verify
- Idea: lowest NM-EN = what the Cardmarket product page shows with filters language=English, condition>=NM
- Idea: product links that open with those filters already set, one per missing card
- Idea: wants list lines with min condition NM + English, so every offer the wizard / seller lists show already qualifies
- Idea: build our own NM-EN price history: record the lowest NM-EN offer each time a card is checked -> own 30-day average over time
- Idea: two columns side by side, clearly labelled: "guide avg30 (all conditions)" vs "NM-EN lowest today"
- Idea: Cardmarket API access (if available to private buyers) could give filtered offers directly
- Idea: browser extension angle: read the filtered product page while browsing and log the NM-EN price
- Idea: the fairness band uses NM-EN lowest as the floor reference, guide avg30 as a sanity check
- Decision (user): prices checked only at two moments: creating the missing-cards list, and creating a shopping list
- Decision (user): English is strict (no other language)
- Decision (user): no tracking of price history or amounts paid (drops the "own NM-EN history" idea)
- Open tension: "30-day average NM English" needs history or a filtered source; without own history -> use guide avg30 labelled "all conditions"? drop it? or a filtered source at shopping time?
- Idea: missing list shows a price snapshot with its date; the shopping list re-checks and flags cards whose price moved since
- Idea: "price moved" marker: up/down vs the missing-list snapshot, so a jump is visible before buying
- Idea: two moments, two purposes: missing list = budget estimate; shopping list = actual decision with NM-EN offers
- Idea: shopping list only ever uses NM-EN offers; anything that can't be verified as NM-EN is marked "check manually"

---
## [MAIN] Reworking master set tracking (continued)
Returned from: FORK 2 (Cardmarket flow) - open question there: what reference replaces the "30-day average" given NM-EN-only and no history
- Idea: "ALL cards" universe sources stacked: set group + subset groups + Deck Exclusives + Miscellaneous (stamped/cosmos) + Promos groups (prerelease/staff/league) on TCGplayer, plus TCGdex variants
- Idea: Pokecottage master set guides as a cross-check for the count per set
- Idea: a manual additions list per set for prints no source lists (store stamps, event stamps)
- Idea: labels vocabulary fixed up front: normal, holo, reverse, pattern names, deck, stamp:<name>, staff, prerelease, cosmos
- Idea: every universe row records its source(s), so you can see why a card is on the list
- Idea: first-run PBL migration: start the private PBL ledger from the user's physical binder + the missing list given today, not from bulk
- Evidence (user): Morpeko ex SIR (PBL 117) shown ~€50-54 market, NM copies cost at least €70. Guide data: low €25, 7-day avg €54.14, 30-day €56.19, trend €51.55 -> all-condition / all-language figures (confirms white hat)
- Idea: never call guide figures "market price" on a printout; label them "Cardmarket guide (all conditions/languages)"
- Idea: placeholders/binder printouts carry no price at all (already decided), and shopping lists only NM-EN prices
- Idea: show a range instead of one number: "guide €54 · NM-EN from €70" so the gap is visible
- Idea: "condition premium" flag: when NM-EN lowest is far above the guide average, mark the card (likely: valuable cards where condition matters most)
- Idea: the 90% target is meaningless on an all-condition average; the target should derive from NM-EN prices only
- Idea: cheap cards: guide numbers are close enough; expensive cards (> €X): require an NM-EN check before any number is shown
- Decision (user): clear market values that are NM English, not guide figures (rejects "no price" / range-only)
- Idea: Cardmarket API (official): articles of a product filtered on language + min condition (verify private access / tokens)
- Idea: read the filtered Cardmarket product page itself at list-creation / shopping time (lowest NM-EN offers)
- Idea: third-party listing data (Apify Cardmarket scrapers with minCondition + language filters)
- Idea: definition of "market value NM-EN": lowest offer? median of the cheapest 5 NM-EN offers? avoids one outlier
- Idea: TCGplayer marketPrice is English-only and condition-based (NM) but USD -> converted fallback, clearly labelled
- Idea: browser extensions (Enhanced Cardmarket) as inspiration for reading prices while browsing
- Idea: show "NM-EN from €X (n offers)" so a thin market is visible
- Idea: the targets (90%) and the fairness band both derive from the same NM-EN value
- Decision (user): market value = BOTH current lowest listing AND 30-day average, English, Near Mint
- Decision (user): no NM available -> best available condition (fallback ladder), shown as such
- Decision (user): EU sellers only
- Open tension: an NM-EN 30-day average needs sales/offer history; user doesn't want to track prices themselves -> where does it come from? (a source that publishes it, or a silent technical cache that isn't "tracking" for the user?)
- Idea: condition ladder: NM -> EX -> GD -> LP..., the value always shows its condition ("€70 NM", "€55 EX*")
- Idea: per card two numbers + a verdict: lowest now | 30-day avg | which one the target uses
- Idea: target derived from the lower of the two, or from the average (a deal = below average)
- Idea: "lowest is suspiciously low" flag when lowest is far below the 30-day average (fake/mislabelled listing?)
- Idea: EU filter also applies to the shopping-list seller choice, not only to prices
- Idea: country-level preference: domestic first, then EU
- Clarified: "hidden cache" = a file on the user's machine collecting observations to compute an own average -> rejected (not the purpose)
- Decision (user): scripts return two facts, not a "market value": current lowest price + 30-day average (English, Near Mint or best available condition)
- Decision (user): the user decides what's acceptable -> no computed target / fairness verdict needed (drops the 90% target column and traffic lights)
- Decision (user): EU + UK sellers
- Idea: each price shows its source and date checked ("Cardmarket, 18 Oct")
- Idea: each price shows its condition and offer count ("€72 NM · 4 offers")
- Idea: the 30-day average comes from a source as-is; if that source's average isn't NM-EN-filtered, it's labelled so ("30-day avg, all conditions")
- Idea: columns: card | lowest NM-EN (EU+UK) | condition | 30-day avg | source/date
- Idea: no number at all beats an invented one: "no English offer in EU/UK" as an explicit outcome
- Decision (user): all-condition 30-day average is NOT acceptable (clear underestimate); only an NM-EN 30-day average counts
- Open question: which source publishes a 30-day average for NM English? Candidates to verify: Pokemon Price Tracker API (EUR, historical), Eyevo, Apify price checkers (seem to mirror the same Cardmarket guide avg30 -> likely all-condition)
- Idea: if no source gives NM-EN avg30, the column says "not available" rather than a wrong number
- Idea: TCGplayer NM market price (English-only marketplace, condition-based) in USD as a clearly separate column, if wanted
- Idea: verify a candidate source with Morpeko ex SIR (PBL 117) as the test card: does its avg land near the €70+ NM reality?
- Decision (user): TODO after brainstorm: verify a source for an NM-EN 30-day sales average (test card: Morpeko ex SIR PBL 117)
- Decision (user): if no NM-EN 30-day sales average exists, report the average of the 5 lowest NM-EN listings (EU+UK) instead, labelled as such
- Idea: label makes the difference clear: "30-day sales avg" vs "avg of 5 lowest listings"
- Idea: fewer than 5 listings -> average of what exists, with the count ("avg of 3 listings")
- Idea: same condition fallback applies: if fewer than 5 NM, does the average include EX copies? (open)
- Idea: one listing per seller in the 5, so one shop's multiple copies can't dominate
- Clarified (user): the PBL missing list given earlier is what placeholders.py output (old universe, no stamps); after the rework the user will physically check the binder against the new output
- Idea: PBL migration = new universe minus the user's list, then a physical audit; stamps 84/85 promo enter as owned via add_entries --to masterset:PBL
- Idea: audit sheet for the physical check: binder order, one line per slot, tick box, so differences are written down on the spot
- Idea: audit result feeds back as a correction file (not hand edits in the xlsx)
- Idea: the audit also catches the 17 dupes: where do they go? (public bulk, since the binder already has its copy)
- Decision (user): the audit sheet is on screen (no printout)
- Idea: on-screen audit in binder order, page by page (9 pockets per screen = one binder page)
- Idea: card pictures on screen so a slot can be recognised at a glance
- Idea: tap/tick states per slot: present / missing / wrong variant
- Idea: the audit's result is the correction file directly (no retyping)
- Idea: audit as the master set xlsx itself, filtered to binder order (simplest on-screen form)
- Decision (user): audit = simply a list of missing cards generated from the master set xlsx (no special audit tool)
- Idea: the missing list in binder order with number + name + exact print, so it doubles as the audit checklist
- Idea: corrections after the check go in via add_entries --to masterset:PBL (owned) like any arrival
- Decision (user): the audit IS the checklist page at the end of the placeholders PDF (generated from the master set xlsx)
- Implication: that checklist must be built from the private master set ledger (not bulk), with the full universe and exact print labels, and its prices follow the NM-EN rules

---
## Final Summary
Ideas logged: 168 (plus 23 explicit decisions by the user). Forks: 2.

Key themes:
- Root cause of the 17 dupes: the PBL list measured "missing" against bulk after binder copies were removed; the list never knew the binder existed
- Two independent ledgers with the same shape and identical card lists per set: public (bulk, git-synced, on the site) and private (everything, local only); one bridge: public -> NEW master set at setup only
- Every arrival goes through add_entries.py with an obligatory destination (public / masterset:X), validated before writing, soft exit on problems
- A living card universe per set: ALL cards (stamps, deck prints, ...) on site and in master sets; a set update re-opens a finished master set
- Prices: two facts, no verdicts: lowest NM English listing (EU+UK, best condition fallback) + NM English 30-day sales average, else average of the 5 lowest listings; checked only when creating the missing list and the shopping list; no history kept
- Cardmarket: as few sellers as possible, NM English only, wants list generated from the master set's missing cards
- Audit = the checklist page of the placeholders PDF, built from the private master set ledger

Forks explored:
- FORK 1 Two ledgers + one bridge (started as "one inventory", rejected by the user: breaks desktop/laptop sync)
- FORK 2 Cardmarket flow

Open items after the brainstorm:
- Verify a source for an NM English 30-day sales average (test: Morpeko ex SIR PBL 117, guide says ~€54-56, NM reality €70+)
- Clearer script names (masterset_setup etc.); "ALL cards" universe sources (Deck Exclusives, Miscellaneous stamps, promo groups)
