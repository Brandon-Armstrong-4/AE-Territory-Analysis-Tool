# Scoring

Every agency gets a **Readiness** score from 0 to 100, a **tier**, and a **Priority** used to order lists. All of it is computed in the browser from the merged record (`derive()` in `app/index.html`). Every number on this page is a default that can be changed in Settings.

## Readiness

Readiness is the weighted sum of four dimensions. Each dimension is the sum of its factor points divided by the most points that dimension can earn, times its weight.

| Dimension | Weight | The question it answers |
|---|---|---|
| Fit | 30 | Is this the kind of agency we win? |
| Friction | 25 | Does the agency visibly struggle today? |
| Timing | 30 | Is something about to change? |
| Access | 15 | Can we reach the right person? |

```
Readiness = Σ over dimensions ( raw points ÷ max points × weight ), clamped to 0–100
```

**Unknown scores zero.** A factor with no evidence shows "To verify" and adds nothing, so Readiness only rises as scans find real evidence. The drawer lists the three unknown or zero factors that would add the most if confirmed.

## Factors and points

### Fit

| Factor | Points |
|---|---|
| Type and size | Population band points × type factor. Bands: under 5k 2, 5k–15k 5, 15k–50k 10, 50k–150k 10, 150k+ 7. Type factor: city, town, township, borough, village 1.0; county 0.8; special or school district 0.6; other 0.5. A recreation district gets full points. |
| Recreation capacity | Dedicated department 8, shared but named 5, mentioned 2, none 0 |
| Program breadth | 1 per program type seen (camps, aquatics, leagues, classes, rentals, senior, special events), up to 7 |
| CivicPlus footprint | Two or more products 5, one product 3, new logo 0 |

### Friction

| Factor | Points |
|---|---|
| Registration method | PDF form 10, phone or email 10, legacy online 6, none found 4, modern online 0 |
| Online payment | None 5, partial 3, online 0 |
| Facility booking | Phone 4, form 4, none found 2, online 0 |
| Accessibility gaps | Evidenced 3, suspected 1, none 0 |
| Incumbent weakness | Legacy, unsupported or fragmented 3; adequate or none 0 |

### Timing

| Factor | Points |
|---|---|
| Budget window | Seed window 12, prep 8, outside 4, adoption 3, fiscal year just started 2 |
| Live triggers | Strongest signal plus half the second, capped at 12. Agenda mention 8, vendor change 8, leadership change 5, capital project 5, bond or levy 5, budget workshop 4, grant 3, accessibility pressure 3, news 3, other 1. **Unverified signals count at half.** |
| Seasonal pain | Registration peak within 90 days during a pilot-ask month 6; peak within 180 days 3 |

Signals count only inside their lookback: 12 months by default, 6 months for agenda mentions and budget workshops. An interim director is an ordinary leadership change with no extra weight.

### Access

| Factor | Points |
|---|---|
| Existing relationship | Customer with a known contact 6, customer 4, prior conversation 3, none 0 |
| Named persona | Recreation director 5, recreation staff 3, generic contact 1 |
| Nearby reference | REC customer within 25 miles 4, any CivicPlus customer nearby 2 |

## Budget windows

Each agency uses its own verified budget calendar when a deep scan found one, otherwise its state's default.

| State | Fiscal year starts | Prep | Adoption | Source of the default |
|---|---|---|---|---|
| TX | October | Mar–Jul | Aug–Sep | Guadalupe County FY27 budget calendar |
| PA | January | Aug–Oct | Nov–Dec | Borough Code §1310 (Dec 31 adoption deadline) |
| RI | July | Jan–Apr | May–Jun | Charlestown financial town referendum, June 2026 |
| CT | July | Jan–Mar | Apr–Jun | CT Mirror, April 27, 2026 |
| SD | January | Jun–Aug | Sep–Oct | SDCL 9-21-2 (appropriation ordinance by the first September meeting) |

The **seed window** opens four months before prep starts: the time to plant a line item before the budget is drafted. The window an agency is in today (`seed`, `prep`, `adoption`, `fy_recent`, `outside`) sets its Budget window points and its chip.

Registration peaks default to February–May and July–August; pilot-ask months are November–January and April–June.

## Tiers

| Tier | Rule |
|---|---|
| Tier 1, needs deep scan | Readiness ≥ 75 **and** timing ready (a live trigger or the seed window), not yet deep scanned |
| Tier 1, pending your check | Same, deep scanned, the rep has not verified the key facts |
| Tier 1 | Same, deep scanned and verified |
| Tier 2 | Readiness ≥ 55 |
| Tier 3 | Scanned, below 55 |
| Awaiting scan | Not scanned yet |
| Set aside | A set-aside rule or the rep's decision applies |

**Near the line:** not Tier 1, timing ready, and within 10 points of the Tier 1 line. These are the best candidates for a deep scan.

## Priority

Until a pricing table is entered, Priority is relative: `Readiness × population band rank` (rank 1 for under 5k up to 5 for 150k and up). Once pricing is set per band and program breadth, Priority becomes expected dollars: `price × Readiness ÷ 100`.

## Set-aside reasons

| Reason | Applied by | Comes back when |
|---|---|---|
| Already owns REC | Rule | Not while the REC contract holds |
| Not suitable for outbound in Salesforce | Rule | The Salesforce flag changes, or the rep pursues it |
| Excluded agency type | Rule | The agency runs a public recreation department under its own name |
| No recreation function | Rule or rep | The agency adds a coordinator, a facility or programs |
| Outside your population range | Rule or rep | The range is widened |
| No reachable contact | Rep | New staff appear, or a neighbor wins |
| Run by a school district or outside partner | Rep | The city takes program management back |
| Other | Rep | Per the rep's note |

A rep's set-aside reopens on its own when a new signal arrives after it was set or a seed window opens. **A competitor platform is never a set-aside reason.**

## Headlines

Each scanned agency that is not set aside gets one headline from its strongest angle:

| Angle | Weight |
|---|---|
| Recreation software on an agenda, vendor change | 10 |
| PDF registration with no online payment | 9 |
| PDF registration, phone or email registration | 8 |
| New recreation leadership, capital project, bond or levy | 7 |
| Competitor platform with a known contract end (a displacement play) | 7 |
| Budget workshop, no online registration, legacy system, inaccessible forms | 6 |
| Grant, accessibility pressure, competitor platform | 5 |
| News | 3 |

A verified signal adds 1. Under the headline sit up to three supporting facts: the next-best angle, the budget window when it is seed or prep, customer or new logo, and the named director.

Headlines are ordered by tier first (Tier 1, pending check, needs deep scan, near the line, Tier 2, the rest), then Priority, then angle weight. Each state tab shows its own; **All Five** shows the top headlines from each state.
